"""IPTV 主入口"""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

# 确保 src 目录在 path 中
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.fetcher import Fetcher
from src.validator import Validator
from src.grouper import Grouper
from src.generator import Generator
from src.cache import Cache


async def run(config_dir: str = None, output_dir: str = None, use_cache: bool = True, skip_validation: bool = False):
    """运行完整流程"""
    config = Config(config_dir)
    output_dir = Path(output_dir) if output_dir else Path(__file__).parent.parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    cache = Cache()
    cache_key = "channels_raw"

    # 1. 抓取
    if use_cache:
        channels_data = cache.get(cache_key)
        if channels_data:
            print(f"[Main] Using cached channels: {len(channels_data)}")
            from src.fetcher import Channel
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
    if skip_validation:
        print("[Main] Skipping validation")
        valid_channels = channels
    else:
        validator = Validator(config)
        valid_channels = await validator.validate(channels)
        print(f"[Main] Validated {len(valid_channels)} channels")

    # 3. 分组
    grouper = Grouper(config)
    grouped = grouper.group(valid_channels)
    print(f"[Main] Grouped into {len(grouped)} groups")

    # 4. 生成
    generator = Generator()

    # 生成 hk_merged.m3u 和 all_merged.m3u
    result = generator.generate_hk_and_all(grouped, str(output_dir))
    print(f"[Main] Generated HK: {result['hk']['channels']} channels in {result['hk']['groups']} groups")
    print(f"[Main] Generated ALL: {result['all']['channels']} channels in {result['all']['groups']} groups")

    # 统计
    stats = {g: len(chs) for g, chs in grouped.items()}
    stats_path = output_dir / "stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"[Main] Stats saved to: {stats_path}")

    return {
        "total": len(valid_channels),
        "groups": len(grouped),
        "hk_channels": result['hk']['channels'],
        "all_channels": result['all']['channels'],
        "output": str(output_dir),
        "stats": stats,
    }


def main():
    parser = argparse.ArgumentParser(description="IPTV 抓取、验证、分组、生成工具")
    parser.add_argument("--config", "-c", default=None, help="配置文件目录")
    parser.add_argument("--output", "-o", default=None, help="输出目录")
    parser.add_argument("--no-cache", action="store_true", help="禁用缓存")
    parser.add_argument("--skip-validation", action="store_true", help="跳过 URL 验证")
    args = parser.parse_args()

    result = asyncio.run(run(
        config_dir=args.config,
        output_dir=args.output,
        use_cache=not args.no_cache,
        skip_validation=args.skip_validation,
    ))
    print(f"\n✅ 完成！共 {result['total']} 个有效频道，分 {result['groups']} 组")
    print(f"   港台频道: {result['hk_channels']}")
    print(f"   全球频道: {result['all_channels']}")


if __name__ == "__main__":
    main()
