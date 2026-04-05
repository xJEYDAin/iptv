"""分组模块：使用 iptv-scraper 的分类逻辑"""
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any

# 确保 src 目录在 path 中
sys.path.insert(0, str(Path(__file__).parent.parent))

# 尝试导入 iptv-scraper 的分类器和标准化函数
try:
    from src.group.categorizer import categorize
    from src.group.normalize import normalize_channel_name, normalize_channels
    USE_IPTV_SCRAPER = True
except ImportError:
    USE_IPTV_SCRAPER = False


class Channel:
    """频道对象（简化版）"""
    def __init__(self, name: str = "", url: str = "", logo: str = "", group: str = "", **kwargs):
        self.name = name.strip() if name else ""
        self.url = url.strip() if url else ""
        self.logo = logo.strip() if logo else ""
        self.group = group.strip() if group else ""
        self.raw_attrs = kwargs
        self._normalized_name = ""

    def __repr__(self):
        return f"<Channel {self.name}>"


class Grouper:
    """频道分组器"""

    def __init__(self, config=None):
        self.config = config
        self._aliases: Dict[str, str] = {}

    def _load_aliases(self) -> Dict[str, str]:
        """加载别名映射"""
        if self._aliases:
            return self._aliases

        alias_file = Path(__file__).parent.parent / "config" / "alias.txt"
        if alias_file.exists():
            for line in alias_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    # 支持 "->" 和 "=" 分隔符
                    if "->" in line:
                        parts = line.split("->", 1)
                    else:
                        parts = line.split("=", 1)
                    if len(parts) == 2:
                        self._aliases[parts[0].strip()] = parts[1].strip()
        return self._aliases

    def group(self, channels: List[Channel]) -> Dict[str, List[Channel]]:
        """对频道列表进行分组"""
        print(f"[Grouper] 开始分组，共 {len(channels)} 个频道")

        # 1. 标准化频道名称
        if USE_IPTV_SCRAPER:
            print("[Grouper] 使用 iptv-scraper 标准化逻辑")
            aliases = self._load_aliases()
            for ch in channels:
                raw_name = ch.name or ""
                ch._normalized_name = normalize_channel_name(raw_name, aliases)

            # 2. 合并同名频道
            print("[Grouper] 合并同名频道...")
            # 转换为 dict 格式供 normalize_channels 使用
            channels_dict = []
            for ch in channels:
                channels_dict.append({
                    "name": ch.name,
                    "url": ch.url,
                    "logo": ch.logo,
                    "group": ch.group,
                    "_normalized_name": ch._normalized_name,
                })

            merged = normalize_channels(channels_dict, aliases)
            print(f"[Grouper] 合并后剩余 {len(merged)} 个频道")

            # 转换回 Channel 对象，并使用标准化名称
            channels = []
            for ch_dict in merged:
                normalized = ch_dict.get("_normalized_name", "")
                # 使用标准化名称（如果可用）
                display_name = normalized if normalized else ch_dict.get("name", "")
                ch = Channel(
                    name=display_name,
                    url=ch_dict.get("url", ""),
                    logo=ch_dict.get("logo", ""),
                    group=ch_dict.get("group", ""),
                )
                ch._normalized_name = normalized
                channels.append(ch)

        # 3. 分组
        result: Dict[str, List[Channel]] = {}
        for ch in channels:
            group_name = self._match_group(ch)
            if group_name:
                if group_name not in result:
                    result[group_name] = []
                result[group_name].append(ch)

        print(f"[Grouper] 分组完成，共 {len(result)} 个分组")
        return result

    def _match_group(self, channel: Channel) -> Optional[str]:
        """匹配频道所属分组"""
        # 使用标准化后的名称进行匹配
        name = channel._normalized_name or channel.name or ""
        group = channel.group or ""
        logo = channel.logo or ""

        if USE_IPTV_SCRAPER:
            return categorize(name, group, logo)
        else:
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
