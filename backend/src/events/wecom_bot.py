"""
企微机器人通知渠道
通过企微机器人 webhook 发送 Markdown 格式消息
"""
from typing import Any, Dict
import httpx

from .base import ChannelBase, EventFormatter


class WeComBotChannel(ChannelBase):
    """企微机器人渠道"""

    type = "wecom-bot"
    name = "企微机器人"
    description = "通过企微机器人 Webhook 发送 Markdown 格式消息"

    def __init__(self, webhook_url: str):
        """
        初始化企微机器人渠道

        Args:
            webhook_url: 企微机器人 Webhook 地址
        """
        self.webhook_url = webhook_url

    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """验证配置"""
        if not config.get("webhook_url"):
            return False, "webhook_url 不能为空"
        if not config["webhook_url"].startswith("https://qyapi.weixin.qq.com/"):
            return False, "webhook_url 格式不正确，应以 https://qyapi.weixin.qq.com/ 开头"
        return True, ""

    def format_message(self, event: str, data: Any) -> Dict[str, Any]:
        """
        格式化消息为企微 Markdown 格式

        企微机器人支持的 Markdown 语法：
        - 标题：# 一级标题 ## 二级标题
        - 引用：> 引用文本
        - 粗体：**粗体**
        - 链接：[超链接](http://xxx)
        - 图片：![](http://xxx)
        - 有序列表：1. xxx
        - 无序列表：- xxx
        """
        emoji = EventFormatter.get_event_emoji(event)
        event_name = EventFormatter.get_event_name(event)

        # 构建消息内容
        lines = []

        # 标题
        lines.append(f"**{emoji} {event_name}**")
        lines.append("")

        # 根据事件类型添加详情
        if event == "work.created":
            lines.extend(self._format_work_created(data))
        elif event == "work.updated":
            lines.extend(self._format_work_updated(data))
        elif event == "team.created":
            lines.extend(self._format_team_created(data))
        elif event == "team.member_added":
            lines.extend(self._format_team_member_added(data))
        elif event == "review.created":
            lines.extend(self._format_review_created(data))
        elif event == "vote.created":
            lines.extend(self._format_vote_created(data))
        elif event == "user.registered":
            lines.extend(self._format_user_registered(data))
        else:
            lines.extend(self._format_generic(data))

        # 底部时间戳
        from datetime import datetime
        lines.append("")
        lines.append(f"> 🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        content = "\n".join(lines)

        return {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }

    def _format_work_created(self, data: Any) -> list:
        """格式化作品创建事件"""
        lines = []
        if isinstance(data, dict):
            lines.append(f"- **作品名称**：{data.get('name', '未知')}")
            lines.append(f"- **队伍名称**：{data.get('team_name', '未知')}")
            if data.get('description'):
                desc = str(data.get('description', ''))[:100]
                ellipsis = '...' if len(str(data.get('description', ''))) > 100 else ''
                lines.append(f"- **简介**：{desc}{ellipsis}")
            if data.get('submitted_by'):
                lines.append(f"- **提交人**：{data.get('submitted_by')}")
        else:
            lines.append(f"- 数据：{str(data)[:200]}")
        return lines

    def _format_work_updated(self, data: Any) -> list:
        """格式化作品更新事件"""
        lines = []
        if isinstance(data, dict):
            lines.append(f"- **作品名称**：{data.get('name', '未知')}")
            lines.append(f"- **队伍名称**：{data.get('team_name', '未知')}")
            if data.get('updated_fields'):
                fields = ", ".join(data.get('updated_fields', []))
                lines.append(f"- **更新字段**：{fields}")
        else:
            lines.append(f"- 数据：{str(data)[:200]}")
        return lines

    def _format_team_created(self, data: Any) -> list:
        """格式化队伍创建事件"""
        lines = []
        if isinstance(data, dict):
            lines.append(f"- **队伍名称**：{data.get('name', '未知')}")
            if data.get('leader_name'):
                lines.append(f"- **队长**：{data.get('leader_name')}")
            if data.get('member_count'):
                lines.append(f"- **成员数**：{data.get('member_count')}")
        else:
            lines.append(f"- 数据：{str(data)[:200]}")
        return lines

    def _format_team_member_added(self, data: Any) -> list:
        """格式化成员添加事件"""
        lines = []
        if isinstance(data, dict):
            lines.append(f"- **队伍名称**：{data.get('team_name', '未知')}")
            lines.append(f"- **新增成员**：{data.get('member_name', '未知')}")
            if data.get('added_by'):
                lines.append(f"- **添加人**：{data.get('added_by')}")
        else:
            lines.append(f"- 数据：{str(data)[:200]}")
        return lines

    def _format_review_created(self, data: Any) -> list:
        """格式化评审创建事件"""
        lines = []
        if isinstance(data, dict):
            lines.append(f"- **作品名称**：{data.get('work_name', '未知')}")
            lines.append(f"- **队伍名称**：{data.get('team_name', '未知')}")
            if data.get('reviewer'):
                lines.append(f"- **评审人**：{data.get('reviewer')}")
            if data.get('score') is not None:
                lines.append(f"- **评分**：{data.get('score')}")
        else:
            lines.append(f"- 数据：{str(data)[:200]}")
        return lines

    def _format_vote_created(self, data: Any) -> list:
        """格式化投票创建事件"""
        lines = []
        if isinstance(data, dict):
            lines.append(f"- **作品名称**：{data.get('work_name', '未知')}")
            lines.append(f"- **队伍名称**：{data.get('team_name', '未知')}")
            if data.get('voter'):
                lines.append(f"- **投票人**：{data.get('voter')}")
        else:
            lines.append(f"- 数据：{str(data)[:200]}")
        return lines

    def _format_user_registered(self, data: Any) -> list:
        """格式化用户注册事件"""
        lines = []
        if isinstance(data, dict):
            lines.append(f"- **用户名**：{data.get('username', '未知')}")
            lines.append(f"- **昵称**：{data.get('nickname', data.get('username', '未知'))}")
            if data.get('email'):
                lines.append(f"- **邮箱**：{data.get('email')}")
        else:
            lines.append(f"- 数据：{str(data)[:200]}")
        return lines

    def _format_generic(self, data: Any) -> list:
        """通用格式化"""
        lines = []
        if isinstance(data, dict):
            # 提取关键字段
            important_keys = ['name', 'title', 'id', 'username', 'email']
            for key in important_keys:
                if key in data and data[key]:
                    value = str(data[key])
                    if len(value) > 50:
                        value = value[:50] + "..."
                    lines.append(f"- **{key.title()}**：{value}")
        else:
            content = str(data)
            if len(content) > 200:
                content = content[:200] + "..."
            lines.append(f"- {content}")
        return lines

    async def send(self, content: Dict[str, Any]) -> tuple[bool, str]:
        """
        发送消息到企微机器人

        Args:
            content: 消息内容（包含 msgtype 和 markdown/text/image 等）

        Returns:
            (是否成功, 错误信息或响应)
        """
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self.webhook_url,
                    json=content
                )
                result = response.json()

                if result.get("errcode") == 0:
                    return True, "发送成功"
                else:
                    errmsg = result.get("errmsg", "未知错误")
                    return False, f"企微 API 错误: {errmsg}"

        except httpx.TimeoutException:
            return False, "请求超时"
        except httpx.RequestError as e:
            return False, f"网络错误: {str(e)}"
        except Exception as e:
            return False, f"发送失败: {str(e)}"