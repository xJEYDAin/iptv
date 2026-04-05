"""IPTV 主入口"""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from .config import Config
from .fetcher import Fetcher
from .validator import Validator
from .grouper import Grouper
from .generator import Generator
from .cache import Cache


async def run(config_dir: str = None, output_dir: str = None, use_cache: bool = True):
    """运行完整流程"""
    config = Config(config_dir)
    output_dir = Path(output_dir) if output_dir else Path(__file__).parent.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    cache = Cache()
    cache_key = "channels_raw"

    # 1. 抓取
    if use_cache:
        channels_data = cache.get(cache_key)
        if channels_data:
            print(f"[Main] Using cached channels: {len(channels_data)}")
            from .fetcher import Channel
            channels = [Channel(**d) for d in channels_data]
        else:
            fetcher = Fetcher(config)
            channels = await fetcher.fetch_all()
            cache.set(cache_key, [ch.__dict__ for ch in channels])
    else:
        fetcher = Fetcher(config)
        channels = await fetcher.fetch_all()

    print(f"[Main] Fetched {len(channels)} channels")

    # 2. 验证
    validator = Validator(config)
    valid_channels = await validator.validate(channels)
    print(f"[Main] Validated {len(valid_channels)} channels")

    # 3. 分组
    grouper = Grouper(config)
    grouped = grouper.group(valid_channels)
    print(f"[Main] Grouped into {len(grouped)} groups")

    # 4. 生成
    generator = Generator()

    # 生成合并文件
    combined_path = output_dir / "iptv.m3u"
    generator.generate(grouped, str(combined_path))
    print(f"[Main] Generated: {combined_path}")

    # 生成分组文件
    multi_dir = output_dir / "channels"
    generator.generate_multi(grouped, str(multi_dir))
    print(f"[Main] Generated grouped files in: {multi_dir}")

    # 统计
    stats = {g: len(chs) for g, chs in grouped.items()}
    stats_path = output_dir / "stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"[Main] Stats: {stats}")

    return {
        "total": len(valid_channels),
        "groups": len(grouped),
        "output": str(combined_path),
        "stats": stats,
    }


def main():
    parser = argparse.ArgumentParser(description="IPTV 抓取、验证、分组、生成工具")
    parser.add_argument("--config", "-c", default=None, help="配置文件目录")
    parser.add_argument("--output", "-o", default=None, help="输出目录")
    parser.add_argument("--no-cache", action="store_true", help="禁用缓存")
    args = parser.parse_args()

    result = asyncio.run(run(
        config_dir=args.config,
        output_dir=args.output,
        use_cache=not args.no_cache,
    ))
    print(f"\n✅ 完成！共 {result['total']} 个频道，分 {result['groups']} 组")


if __name__ == "__main__":
    main()
