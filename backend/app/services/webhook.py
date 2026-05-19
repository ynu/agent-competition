"""
Webhook 服务层
"""
import json
import asyncio
import httpx
from datetime import datetime, timezone
from typing import Optional, Any
from sqlalchemy.orm import Session


def trigger_event(db: Session, event: str, data: Any, action: str = None):
    """
    统一触发事件函数，同时触发 Webhook 和事件通知渠道

    Args:
        db: 数据库会话
        event: 事件类型（如 work.created）
        data: 事件数据
        action: 操作类型（created/updated/deleted 等）
    """
    # 延迟导入避免循环依赖
    from app.services.notification_service import trigger_notification

    # 创建异步任务
    async def _trigger():
        service = WebhookService(db)
        await service.trigger_event(event, data, action)
        await trigger_notification(db, event, data)

    # 在 FastAPI 的同步上下文中运行异步代码
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果已在运行中，创建任务
            asyncio.create_task(_trigger())
        else:
            loop.run_until_complete(_trigger())
    except RuntimeError:
        # 没有事件循环，创建新的
        asyncio.run(_trigger())

from app.models.webhook import Webhook, WebhookDelivery, WebhookEventType


class WebhookService:
    """Webhook 服务类"""

    MAX_RETRIES = 3
    TIMEOUT = 30  # 秒

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def create_delivery_payload(event: str, data: Any, action: str = None) -> dict:
        """创建投递载荷（GitHub 风格）"""
        now = datetime.now(timezone.utc)
        return {
            "id": f"wh_{now.strftime('%Y%m%d%H%M%S')}_{hash(str(data)) % 100000}",
            "event": event,
            "action": action,
            "created_at": now.isoformat().replace("+00:00", "Z"),
            "data": data
        }

    async def _send_request(
        self,
        webhook: Webhook,
        payload: dict,
        attempt: int = 1
    ) -> tuple[int, str, str]:
        """发送 HTTP 请求"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AgentCompetition-Webhook/1.0",
            "X-Webhook-Event": payload["event"],
            "X-Webhook-Delivery": payload["id"],
        }

        # 添加自定义请求头
        if webhook.headers:
            headers.update(webhook.headers)

        # 添加签名
        payload_str = json.dumps(payload, ensure_ascii=False)
        if webhook.secret:
            headers["X-Hub-Signature-256"] = Webhook.generate_signature(payload_str, webhook.secret)

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.post(
                    webhook.url,
                    content=payload_str,
                    headers=headers
                )
                return (
                    response.status_code,
                    response.text[:5000] if response.text else "",  # 限制响应长度
                    ""
                )
        except httpx.TimeoutException:
            return (0, "", "Request timeout")
        except httpx.RequestError as e:
            return (0, "", str(e))
        except Exception as e:
            return (0, "", str(e))

    def _record_delivery(
        self,
        webhook_id: int,
        event: str,
        payload: str,
        status: int,
        response_body: str,
        error_message: str,
        attempt: int = 1
    ):
        """记录投递历史"""
        delivery = WebhookDelivery(
            webhook_id=webhook_id,
            event=event,
            payload=payload,
            response_status=status,
            response_body=response_body,
            error_message=error_message,
            attempt=attempt
        )
        self.db.add(delivery)
        self.db.commit()

    async def trigger_event(self, event: str, data: Any, action: str = None):
        """触发 Webhook 事件"""
        # 获取订阅了该事件的所有活跃 Webhook
        webhooks = self.db.query(Webhook).filter(
            Webhook.is_active == True
        ).all()

        matching_webhooks = [
            w for w in webhooks
            if event in (w.events or [])
        ]

        if not matching_webhooks:
            return

        # 创建载荷
        payload = self.create_delivery_payload(event, data, action)

        for webhook in matching_webhooks:
            await self._trigger_single(webhook, payload)

    async def _trigger_single(self, webhook: Webhook, payload: dict, attempt: int = 1):
        """触发单个 Webhook"""
        payload_str = json.dumps(payload, ensure_ascii=False)

        status, response_body, error = await self._send_request(webhook, payload, attempt)

        # 记录投递
        self._record_delivery(
            webhook.id,
            payload["event"],
            payload_str,
            status,
            response_body,
            error,
            attempt
        )

        # 更新 Webhook 最后触发信息
        webhook.last_triggered_at = datetime.now(timezone.utc)
        webhook.last_trigger_status = status
        self.db.commit()

    async def trigger_event_async(self, event: str, data: Any, action: str = None):
        """异步并发触发 Webhook 事件"""
        webhooks = self.db.query(Webhook).filter(
            Webhook.is_active == True
        ).all()

        matching_webhooks = [
            w for w in webhooks
            if event in (w.events or [])
        ]

        if not matching_webhooks:
            return

        payload = self.create_delivery_payload(event, data, action)

        # 并发发送所有请求
        tasks = [
            self._send_single_async(webhook, payload)
            for webhook in matching_webhooks
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_single_async(self, webhook: Webhook, payload: dict, attempt: int = 1):
        """异步发送单个 Webhook 请求"""
        payload_str = json.dumps(payload, ensure_ascii=False)

        status, response_body, error = await self._send_request(webhook, payload, attempt)

        # 记录投递
        self._record_delivery(
            webhook.id,
            payload["event"],
            payload_str,
            status,
            response_body,
            error,
            attempt
        )

        webhook.last_triggered_at = datetime.now(timezone.utc)
        webhook.last_trigger_status = status
        self.db.commit()

    async def test_webhook(self, webhook_id: int) -> dict:
        """测试 Webhook"""
        webhook = self.db.query(Webhook).filter(Webhook.id == webhook_id).first()
        if not webhook:
            return {"success": False, "error": "Webhook 不存在"}

        # 发送测试事件
        test_payload = self.create_delivery_payload(
            "test",
            {"message": "This is a test webhook delivery"},
            "test"
        )

        payload_str = json.dumps(test_payload, ensure_ascii=False)
        
        # use await/async in fastapi context
        status, response_body, error = await self._send_request(webhook, test_payload)

        # 记录测试投递
        self._record_delivery(
            webhook.id,
            "test",
            payload_str,
            status,
            response_body,
            error
        )

        webhook.last_triggered_at = datetime.now(timezone.utc)
        webhook.last_trigger_status = status
        self.db.commit()

        return {
            "success": status == 200,
            "status": status,
            "response": response_body,
            "error": error
        }


async def trigger_webhook(db: Session, event: str, data: Any, action: str = None):
    """便捷函数：仅触发 Webhook 事件（保留向后兼容）"""
    service = WebhookService(db)
    await service.trigger_event(event, data, action)


async def trigger_webhook_and_notification(db: Session, event: str, data: Any, action: str = None):
    """
    触发 Webhook 和事件通知渠道

    便捷函数：同时触发 Webhook 和所有订阅的事件通知渠道
    """
    service = WebhookService(db)
    await service.trigger_event(event, data, action)

    # 延迟导入避免循环依赖
    from app.services.notification_service import trigger_notification
    await trigger_notification(db, event, data)


def trigger_event_sync(db: Session, event: str, data: Any, action: str = None):
    """
    同步触发事件（Webhook + 通知渠道）

    在 FastAPI 同步上下文中调用，自动处理异步
    """
    # 创建异步任务
    async def _trigger():
        await trigger_webhook_and_notification(db, event, data, action)

    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(_trigger())
        else:
            loop.run_until_complete(_trigger())
    except RuntimeError:
        asyncio.run(_trigger())