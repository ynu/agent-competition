"""
事件通知渠道模块
自动发现并注册所有渠道插件
"""
from .base import ChannelBase, EventFormatter
from .registry import ChannelRegistry, get_channel, get_available_channels, discover_channels

# 自动发现并注册所有渠道
discover_channels()

__all__ = [
    "ChannelBase",
    "EventFormatter",
    "ChannelRegistry",
    "get_channel",
    "get_available_channels",
    "discover_channels",
]