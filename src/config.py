"""配置加载模块"""
import os
from pathlib import Path
from typing import Dict, List, Any

import yaml


class Config:
    """统一配置管理"""

    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = Path(__file__).parent.parent / "config"
        self.config_dir = Path(config_dir)
        self._sources: List[Dict] = []
        self._groups: List[Dict] = []
        self._whitelist: List[str] = []
        self._proxy_domains: List[str] = []

    @property
    def sources(self) -> List[Dict]:
        if not self._sources:
            self._load_sources()
        return self._sources

    @property
    def groups(self) -> List[Dict]:
        if not self._groups:
            self._load_groups()
        return self._groups

    @property
    def whitelist(self) -> List[str]:
        if not self._whitelist:
            self._load_whitelist()
        return self._whitelist

    @property
    def proxy_domains(self) -> List[str]:
        if not self._proxy_domains:
            self._load_proxy_domains()
        return self._proxy_domains

    def _load_yaml(self, filename: str) -> Any:
        path = self.config_dir / filename
        if not path.exists():
            return [] if filename.endswith(".yaml") else ""
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or []

    def _load_text(self, filename: str) -> List[str]:
        path = self.config_dir / filename
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]

    def _load_sources(self):
        data = self._load_yaml("sources.yaml")
        self._sources = [s for s in data.get("sources", []) if s.get("enabled", True)]

    def _load_groups(self):
        data = self._load_yaml("groups.yaml")
        self._groups = data.get("groups", [])

    def _load_whitelist(self):
        self._whitelist = self._load_text("whitelist.txt")

    def _load_proxy_domains(self):
        self._proxy_domains = self._load_text("proxy.txt")
