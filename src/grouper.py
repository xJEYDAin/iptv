"""分组模块：使用 iptv-scraper 的分类逻辑"""
import re
from typing import List, Dict, Optional

# 尝试导入 iptv-scraper 的分类器
try:
    from src.group.categorizer import categorize
    USE_IPTV_SCRAPER = True
except ImportError:
    USE_IPTV_SCRAPER = False


class Channel:
    """频道对象（简化版）"""
    def __init__(self, name: str = "", url: str = "", logo: str = "", group: str = ""):
        self.name = name.strip() if name else ""
        self.url = url.strip() if url else ""
        self.logo = logo.strip() if logo else ""
        self.group = group.strip() if group else ""


class Grouper:
    """频道分组器"""

    def __init__(self, config=None):
        self.config = config

    def group(self, channels: List[Channel]) -> Dict[str, List[Channel]]:
        """对频道列表进行分组"""
        result: Dict[str, List[Channel]] = {}

        for ch in channels:
            group_name = self._match_group(ch)
            if group_name:
                if group_name not in result:
                    result[group_name] = []
                result[group_name].append(ch)

        return result

    def _match_group(self, channel: Channel) -> Optional[str]:
        """匹配频道所属分组"""
        if USE_IPTV_SCRAPER:
            # 使用 iptv-scraper 的分类逻辑
            name = channel.name or ""
            group = channel.group or ""
            logo = channel.logo or ""
            return categorize(name, group, logo)
        else:
            # 回退：简单按关键词分组
            return self._simple_group(channel)

    def _simple_group(self, channel: Channel) -> str:
        """简单的分组逻辑（回退方案）"""
        name_lower = (channel.name or "").lower()
        group_lower = (channel.group or "").lower()
        full_text = name_lower + " " + group_lower

        # 央视频道
        if "cctv" in full_text or "cetv" in full_text:
            return "📺 央视频道"
        # 港澳台
        if any(kw in full_text for kw in ["tvb", "翡翠台", "viutv", "rthk", "台湾", "tvbs"]):
            return "📺 港澳台"
        # 国际频道
        if any(kw in full_text for kw in ["bbc", "cnn", "nhk", "fox", "abc"]):
            return "🌐 国际"

        return "📺 其他"
