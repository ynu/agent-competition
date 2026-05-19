"""
通知服务
触发事件通知到所有订阅的渠道
"""
from datetime import datetime
from typing import Any, List
from sqlalchemy.orm import Session

from app.models.event_channel import EventChannel
from src.events import get_channel


class NotificationService:
    """通知服务"""

    def __init__(self, db: Session):
        self.db = db

    async def notify(self, event: str, data: Any) -> List[dict]:
        """
        触发通知

        查找所有订阅了该事件且处于启用状态的渠道，发送通知。

        Args:
            event: 事件类型（如 work.created）
            data: 事件数据

        Returns:
            发送结果列表 [{"channel_id": 1, "name": "xxx", "success": True, "message": "..."}]
        """
        # 查找订阅了该事件的渠道
        channels = self.db.query(EventChannel).filter(
            EventChannel.is_active == True
        ).all()

        # 筛选订阅了指定事件的渠道
        matching_channels = [
            c for c in channels
            if event in (c.events or [])
        ]

        if not matching_channels:
            return []

        results = []

        for channel in matching_channels:
            result = await self._send_to_channel(channel, event, data)
            results.append({
                "channel_id": channel.id,
                "name": channel.name,
                **result
            })

        return results

    async def _send_to_channel(
        self,
        channel: EventChannel,
        event: str,
        data: Any
    ) -> dict:
        """
        向单个渠道发送通知

        Args:
            channel: 渠道配置
            event: 事件类型
            data: 事件数据

        Returns:
            {"success": True/False, "message": "..."}
        """
        # 获取渠道实现类
        channel_class = get_channel(channel.channel_type)
        if not channel_class:
            self._update_channel_status(channel, False, f"不支持的渠道类型: {channel.channel_type}")
            return {"success": False, "message": f"不支持的渠道类型: {channel.channel_type}"}

        try:
            # 创建渠道实例
            channel_instance = channel_class(**channel.config)

            # 格式化消息
            message_content = channel_instance.format_message(event, data)

            # 发送消息
            success, result = await channel_instance.send(message_content)

            # 更新渠道状态
            self._update_channel_status(channel, success, result if not success else None)

            return {
                "success": success,
                "message": result
            }

        except Exception as e:
            error_msg = str(e)
            self._update_channel_status(channel, False, error_msg)
            return {"success": False, "message": error_msg}

    def _update_channel_status(
        self,
        channel: EventChannel,
        success: bool,
        error: str = None
    ):
        """更新渠道的最后触发状态"""
        channel.last_triggered_at = datetime.utcnow()
        channel.last_trigger_status = success
        channel.last_error = error
        self.db.commit()


async def trigger_notification(db: Session, event: str, data: Any) -> List[dict]:
    """
    便捷函数：触发事件通知

    可以在业务逻辑中直接调用此函数发送通知：
        await trigger_notification(db, "work.created", {"name": "xxx", ...})
    """
    service = NotificationService(db)
    return await service.notify(event, data)


async def notify_work_created(db: Session, work_data: dict):
    """发送作品创建通知"""
    await trigger_notification(db, "work.created", work_data)


async def notify_work_updated(db: Session, work_data: dict):
    """发送作品更新通知"""
    await trigger_notification(db, "work.updated", work_data)


async def notify_team_created(db: Session, team_data: dict):
    """发送队伍创建通知"""
    await trigger_notification(db, "team.created", team_data)


async def notify_team_member_added(db: Session, member_data: dict):
    """发送成员添加通知"""
    await trigger_notification(db, "team.member_added", member_data)


async def notify_review_created(db: Session, review_data: dict):
    """发送评审创建通知"""
    await trigger_notification(db, "review.created", review_data)


async def notify_vote_created(db: Session, vote_data: dict):
    """发送投票创建通知"""
    await trigger_notification(db, "vote.created", vote_data)


async def notify_user_registered(db: Session, user_data: dict):
    """发送用户注册通知"""
    await trigger_notification(db, "user.registered", user_data)