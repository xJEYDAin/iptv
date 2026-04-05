# IPTV 工具

Python 版 IPTV 频道抓取、验证、分组、生成工具。

## 功能

- **抓取**: 从多个数据源抓取 m3u/yaml 格式的频道列表
- **验证**: HEAD 请求 + Content-Type 检查，过滤无效链接
- **分组**: 关键词 + 正则匹配，支持别名标准化
- **生成**: 输出 m3u 格式，支持 #EXTGRP 分组标签

## 设计原则

- **DRY**: 配置与代码分离，避免重复
- **单一职责**: 每个模块只做一件事
- **配置化**: 代理域名、白名单等均可配置
- **可测试**: 独立的模块便于单元测试

## 目录结构

```
iptv/
├── src/
│   ├── main.py       # 入口
│   ├── fetcher.py    # 抓取模块
│   ├── validator.py  # 验证模块
│   ├── grouper.py    # 分组模块
│   ├── generator.py  # 生成模块
│   ├── cache.py      # 缓存模块
│   └── config.py     # 配置加载
├── config/
│   ├── sources.yaml  # 数据源
│   ├── groups.yaml   # 分组规则
│   ├── whitelist.txt # CDN 白名单
│   └── proxy.txt     # 代理域名黑名单
├── tests/
├── .github/workflows/
│   └── update.yml    # 每日运行
└── requirements.txt
```

## 快速开始

```bash
pip install -r requirements.txt
python -m src.main
```

## 配置说明

### sources.yaml

```yaml
sources:
  - name: "IPTV-org"
    url: "https://..."
    enabled: true
    priority: 1
```

### groups.yaml

```yaml
groups:
  - name: "中国大陆"
    keywords:
      - "CCTV"
      - "央视频"
    regex:
      - "^CCTV\\d+$"
    aliases:
      "cctv-1": "CCTV-1 综合"
```

### whitelist.txt

CDN 白名单，命中直接跳过验证。

### proxy.txt

代理域名黑名单，命中直接拒绝。

## License

MIT
