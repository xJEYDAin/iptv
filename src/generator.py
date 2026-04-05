"""生成模块：生成 m3u 格式、支持 #EXTGRP 分组标签"""
import re
from typing import List, Dict, Optional

from .fetcher import Channel


class Generator:
    """m3u 播放列表生成器"""

    def __init__(self, include_group_tag: bool = True, sort: bool = True):
        self.include_group_tag = include_group_tag
        self.sort = sort

    def generate(self, grouped: Dict[str, List[Channel]], output_path: str = None) -> str:
        """生成 m3u 内容"""
        lines = ["#EXTM3U"]

        # 按分组生成
        for group_name, channels in grouped.items():
            if self.sort:
                channels = sorted(channels, key=lambda c: c.name)

            for ch in channels:
                lines.append(self._format_extinf(ch, group_name))
                lines.append(ch.url)

        content = "\n".join(lines) + "\n"

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

        return content

    def _format_extinf(self, channel: Channel, group_name: str) -> str:
        """格式化 #EXTINF 行"""
        attrs = []

        if channel.logo:
            attrs.append(f'tvg-logo="{channel.logo}"')

        if self.include_group_tag:
            attrs.append(f'group-title="{group_name}"')

        if channel.name:
            attrs.append(f'tvg-name="{channel.name}"')

        attr_str = " ".join(attrs) + " " if attrs else ""
        return f"#EXTINF:0 {attr_str}{channel.name}"

    def generate_multi(
        self, grouped: Dict[str, List[Channel]], output_dir: str, prefix: str = ""
    ) -> Dict[str, str]:
        """生成分组播放列表文件"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        paths = {}
        for group_name, channels in grouped.items():
            safe_name = re.sub(r'[<>:"/\\|?*]', "_", group_name)
            filename = f"{prefix}{safe_name}.m3u" if prefix else f"{safe_name}.m3u"
            path = os.path.join(output_dir, filename)
            self.generate({group_name: channels}, path)
            paths[group_name] = path

        return paths
