"""
事件通知渠道注册表
自动发现并管理所有渠道插件
"""
import importlib
import pkgutil
from typing import Dict, List, Optional, Type

from .base import ChannelBase


class ChannelRegistry:
    """渠道注册表"""

    _channels: Dict[str, Type[ChannelBase]] = {}

    @classmethod
    def register(cls, channel_type: str, channel_class: Type[ChannelBase]):
        """
        注册渠道类

        Args:
            channel_type: 渠道类型标识
            channel_class: 渠道类
        """
        if not issubclass(channel_class, ChannelBase):
            raise ValueError(f"{channel_class} must inherit from ChannelBase")
        cls._channels[channel_type] = channel_class

    @classmethod
    def get(cls, channel_type: str) -> Optional[Type[ChannelBase]]:
        """获取渠道类"""
        return cls._channels.get(channel_type)

    @classmethod
    def get_all(cls) -> Dict[str, Type[ChannelBase]]:
        """获取所有已注册的渠道"""
        return cls._channels.copy()

    @classmethod
    def get_choices(cls) -> List[Dict[str, str]]:
        """获取渠道选项列表（用于前端下拉）"""
        return [
            {
                "type": channel_type,
                "name": channel_class.name,
                "description": channel_class.description,
            }
            for channel_type, channel_class in cls._channels.items()
        ]

    @classmethod
    def unregister(cls, channel_type: str):
        """注销渠道"""
        cls._channels.pop(channel_type, None)


def discover_channels():
    """自动发现并注册渠道插件"""
    import os
    # 获取当前模块所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 遍历目录中的所有模块
    for _, module_name, _ in pkgutil.iter_modules([current_dir]):
        if module_name in ("__init__", "base", "registry"):
            continue

        try:
            # 动态导入模块
            module = importlib.import_module(f".{module_name}", package="src.events")

            # 查找所有 ChannelBase 子类
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, ChannelBase)
                    and attr is not ChannelBase
                ):
                    # 注册渠道
                    ChannelRegistry.register(attr.type, attr)
        except Exception as e:
            # 静默忽略加载失败的模块
            print(f"Warning: Failed to load channel {module_name}: {e}")


def get_channel(channel_type: str) -> Optional[Type[ChannelBase]]:
    """获取指定类型的渠道类"""
    return ChannelRegistry.get(channel_type)


def get_available_channels() -> List[Dict[str, str]]:
    """获取所有可用渠道的选项列表"""
    return ChannelRegistry.get_choices()