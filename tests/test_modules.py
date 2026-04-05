"""单元测试"""
import pytest
import asyncio
from src.config import Config
from src.fetcher import Channel, Fetcher
from src.grouper import Grouper
from src.generator import Generator


class TestConfig:
    def test_load_sources(self):
        config = Config()
        assert isinstance(config.sources, list)

    def test_load_groups(self):
        config = Config()
        assert isinstance(config.groups, list)
        assert len(config.groups) > 0

    def test_whitelist(self):
        config = Config()
        assert isinstance(config.whitelist, list)

    def test_proxy_domains(self):
        config = Config()
        assert isinstance(config.proxy_domains, list)


class TestChannel:
    def test_channel_creation(self):
        ch = Channel(name="CCTV-1", url="http://example.com/stream", logo="http://logo.png", group="中国")
        assert ch.name == "CCTV-1"
        assert ch.url == "http://example.com/stream"
        assert ch.logo == "http://logo.png"
        assert ch.group == "中国"


class TestGrouper:
    def test_keyword_match(self):
        config = Config()
        grouper = Grouper(config)
        ch = Channel(name="CCTV-1 综合", url="http://example.com")
        grouped = grouper.group([ch])
        assert "CCTV-1 综合" in list(grouped.values())[0][0].name

    def test_normalize_name(self):
        config = Config()
        grouper = Grouper(config)
        name = grouper._normalize_name("CCTV-1")
        assert name  # 应返回标准化后的名称或原名


class TestGenerator:
    def test_generate_m3u(self):
        generator = Generator()
        channels = [
            Channel(name="Test Channel", url="http://example.com/stream", group="Test"),
        ]
        content = generator.generate({"Test": channels})
        assert "#EXTM3U" in content
        assert "#EXTINF:" in content
        assert "http://example.com/stream" in content

    def test_group_tag(self):
        generator = Generator(include_group_tag=True)
        channels = [Channel(name="Test", url="http://example.com", group="MyGroup")]
        content = generator.generate({"MyGroup": channels})
        assert 'group-title="MyGroup"' in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
