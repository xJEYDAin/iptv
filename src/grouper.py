"""分组模块：关键词 + 正则匹配、频道名称标准化"""
import re
from typing import List, Dict, Optional

from .config import Config
from .fetcher import Channel


class Grouper:
    """频道分组器"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self._compiled_regex: Dict[str, List[re.Pattern]] = {}
        self._compile_regexes()

    def _compile_regexes(self):
        """预编译正则表达式"""
        for group in self.config.groups:
            patterns = group.get("regex", [])
            compiled = []
            for p in patterns:
                try:
                    compiled.append(re.compile(p, re.IGNORECASE))
                except re.error as e:
                    print(f"[Grouper] Invalid regex '{p}': {e}")
            self._compiled_regex[group["name"]] = compiled

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
        name = channel.name
        # 先用别名标准化名称
        name = self._normalize_name(name)

        for group in self.config.groups:
            # 检查关键词
            for kw in group.get("keywords", []):
                if kw.lower() in name.lower():
                    return group["name"]

            # 检查正则
            for pattern in self._compiled_regex.get(group["name"], []):
                if pattern.search(name):
                    return group["name"]

        # 默认分组
        for group in self.config.groups:
            if group.get("default"):
                return group["name"]

        return "其他"

    def _normalize_name(self, name: str) -> str:
        """根据别名标准化频道名称"""
        name_lower = name.lower().strip()
        for group in self.config.groups:
            for alias, full_name in group.get("aliases", {}).items():
                if alias.lower() == name_lower:
                    return full_name
        return name
