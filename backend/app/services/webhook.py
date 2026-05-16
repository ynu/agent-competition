"""
Webhook 服务层
"""
import json
import asyncio
import httpx
from datetime import datetime
from typing import Optional, Any
from sqlalchemy.orm import Session

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
        return {
            "id": f"wh_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{hash(str(data)) % 100000}",
            "event": event,
            "action": action,
            "created_at": datetime.utcnow().isoformat() + "Z",
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

    def trigger_event(self, event: str, data: Any, action: str = None):
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

        # 同步触发所有匹配的 Webhook
        for webhook in matching_webhooks:
            self._trigger_single(webhook, payload)

    def _trigger_single(self, webhook: Webhook, payload: dict, attempt: int = 1):
        """触发单个 Webhook（同步版本）"""
        payload_str = json.dumps(payload, ensure_ascii=False)

        # 执行请求
        status, response_body, error = asyncio.run(
            self._send_request(webhook, payload, attempt)
        )

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
        webhook.last_triggered_at = datetime.utcnow()
        webhook.last_trigger_status = status
        self.db.commit()

    async def trigger_event_async(self, event: str, data: Any, action: str = None):
        """异步触发 Webhook 事件"""
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

        # 记录投递（在事件循环外需要特殊处理）
        self._record_delivery(
            webhook.id,
            payload["event"],
            payload_str,
            status,
            response_body,
            error,
            attempt
        )

        webhook.last_triggered_at = datetime.utcnow()
        webhook.last_trigger_status = status
        self.db.commit()

    def test_webhook(self, webhook_id: int) -> dict:
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
        status, response_body, error = asyncio.run(
            self._send_request(webhook, test_payload)
        )

        # 记录测试投递
        self._record_delivery(
            webhook.id,
            "test",
            payload_str,
            status,
            response_body,
            error
        )

        webhook.last_triggered_at = datetime.utcnow()
        webhook.last_trigger_status = status
        self.db.commit()

        return {
            "success": status == 200,
            "status": status,
            "response": response_body,
            "error": error
        }


def trigger_webhook(db: Session, event: str, data: Any, action: str = None):
    """便捷函数：触发 Webhook 事件"""
    service = WebhookService(db)
    service.trigger_event(event, data, action)