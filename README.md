# 🌐 IPTV 直播源管理工具

> 全新重构的 IPTV 直播源抓取、验证、分组、生成工具。支持 20+ 数据源，自动过滤无效链接，每日定时更新。

---

## 📤 播放列表地址

**主分支**（每日自动更新）：

| 文件 | 地址 |
|------|------|
| 全部频道 | https://raw.githubusercontent.com/xJEYDAin/iptv/main/output/all_merged.m3u |
| 港澳台 | https://raw.githubusercontent.com/xJEYDAin/iptv/main/output/hk_merged.m3u |

---

## 📊 频道统计

| 分组 | 数量 |
|------|------|
| 央视频道 | 1,552 |
| 各省频道 | ~2,000 |
| 港澳台 | ~700 |
| 海外国际 | ~20,000 |

**总计**：约 23,000 个频道

---

## 📡 数据源

**20 个数据源**，按优先级排序：

| 优先级 | 源 | 说明 |
|--------|------|------|
| 1 | sammy0101 | 香港本地源 |
| 2 | xiweiwong-hk-iptv | 香港本地源 |
| 2 | zhi35-iptv | 台标完整 |
| 2 | freetv-fun | 综合频道 |
| 2 | epg-pw | EPG 友好 |
| 3 | fanmingming-live | IPv6 支持 |
| 3 | CCSH-iptv | 综合频道 |
| 3 | gitee-why006-TV | 国内镜像 |
| 4 | iptv-org | 全球综合 |
| 4 | hujingguang-iptv | 中国频道 |
| 4 | Harbin-byte-iptv | 香港补充 |
| 4 | suxuang-myIPTV | IPv4 优先 |
| 5 | free-tv-* (HK/TW/CN/JP/KR) | 各国频道 |
| 6 | free-tv-* (US/UK) | 欧美频道 |
| 5 | vbskycn-iptv4 | IPv6 特色 |

---

## 🏗️ 架构流程

```
数据源 → Fetcher(并发抓取) → Validator(URL验证)
      → Grouper(智能分组) → Generator(m3u生成)
```

**核心模块：**

| 模块 | 职责 |
|------|------|
| Fetcher | 多源抓取、m3u 解析、并发控制 |
| Validator | HEAD 验证、Content-Type 检查、代理域名拒绝 |
| Grouper | 关键词+正则分组、频道名称标准化 |
| Generator | m3u 格式生成、EPG 支持 |
| Cache | JSON 缓存、TTL 支持 |

---

## 🔧 配置

### 数据源配置

`config/sources.yaml` - 启用/禁用数据源

### 分组规则

`config/groups.yaml` - 关键词、正则、别名

### 白名单

`config/whitelist.txt` - CDN 白名单，跳过验证

### 代理域名

`config/proxy.txt` - 代理域名黑名单，直接拒绝

---

## 🚀 快速开始

```bash
# 克隆
git clone https://github.com/xJEYDAin/iptv.git
cd iptv

# 安装依赖
pip install -r requirements.txt

# 运行完整流程
python -m src.main --config ./config --output ./output

# 跳过验证（快速测试）
python -m src.main --skip-validation
```

---

## ⚙️ CLI 参数

| 参数 | 说明 |
|------|------|
| `--config, -c` | 配置文件目录 |
| `--output, -o` | 输出目录 |
| `--no-cache` | 禁用缓存 |
| `--skip-validation` | 跳过 URL 验证 |

---

## 📄 许可证

MIT License
