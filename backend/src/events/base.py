"""
事件通知渠道基类
所有通知渠道必须继承此基类
"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class ChannelBase(ABC):
    """通知渠道抽象基类"""

    # 渠道类型标识（如：wecom-bot, dingtalk, email 等）
    type: str = ""

    # 渠道显示名称
    name: str = ""

    # 渠道描述
    description: str = ""

    @abstractmethod
    def format_message(self, event: str, data: Any) -> Dict[str, Any]:
        """
        格式化消息内容

        Args:
            event: 事件类型（如 work.created）
            data: 事件数据

        Returns:
            渠道特定的消息格式（字典）
        """
        pass

    @abstractmethod
    async def send(self, content: Dict[str, Any]) -> tuple[bool, str]:
        """
        发送消息到渠道

        Args:
            content: 格式化的消息内容

        Returns:
            (是否成功, 错误信息或响应)
        """
        pass

    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """
        验证渠道配置（可选实现）

        Args:
            config: 配置字典

        Returns:
            (是否有效, 错误信息)
        """
        return True, ""


class EventFormatter:
    """事件数据格式化工具"""

    # 事件中文描述映射
    EVENT_NAMES = {
        "team.created": "队伍创建",
        "team.updated": "队伍更新",
        "team.deleted": "队伍删除",
        "team.member_added": "队伍成员添加",
        "team.member_removed": "队伍成员移除",
        "work.created": "作品提交",
        "work.updated": "作品更新",
        "work.deleted": "作品删除",
        "review.created": "评审创建",
        "review.updated": "评审更新",
        "vote.created": "投票创建",
        "content.created": "内容创建",
        "content.updated": "内容更新",
        "content.deleted": "内容删除",
        "user.registered": "用户注册",
    }

    @classmethod
    def get_event_name(cls, event: str) -> str:
        """获取事件中文名称"""
        return cls.EVENT_NAMES.get(event, event)

    @classmethod
    def get_event_emoji(cls, event: str) -> str:
        """获取事件对应的表情"""
        emojis = {
            "team.created": "👥",
            "team.updated": "📝",
            "team.deleted": "🗑️",
            "team.member_added": "➕",
            "team.member_removed": "➖",
            "work.created": "🎉",
            "work.updated": "📝",
            "work.deleted": "🗑️",
            "review.created": "⭐",
            "review.updated": "⭐",
            "vote.created": "🗳️",
            "content.created": "📄",
            "content.updated": "📝",
            "content.deleted": "🗑️",
            "user.registered": "👤",
        }
        return emojis.get(event, "📌")