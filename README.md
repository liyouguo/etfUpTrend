# ETF 上升趋势数据采集工具

自动抓取同花顺 ETF 上升趋势数据，支持 JSON 和 CSV 格式输出，并提供 GitHub Actions 自动化定时任务。

## 功能特性

- ✅ 获取上升趋势 ETF 列表（代码 + 名称 + 市场）
- ✅ 获取详细指标（总涨幅、持续天数、连涨天数、涨停占比）
- ✅ 输出 JSON 和 CSV 格式数据
- ✅ CSV 支持中文标题，易于阅读
- ✅ GitHub Actions 定时自动采集（每天北京时间 9:40）
- ✅ 自动邮件通知
- ✅ 自动上传输出文件到 GitHub Artifact

## 项目结构

```
etfUpTrend/
├── etf_uptrend_tracker.py      # 主程序
├── requirements.txt            # 项目依赖
├── README.md                   # 项目说明
├── .github/workflows/
│   └── data_collection.yml     # GitHub Actions 工作流
└── output/                     # 输出目录（自动生成）
    ├── etf_uptrend_YYYYMMDD.json
    └── etf_uptrend_YYYYMMDD.csv
```

## 本地运行

### 环境要求

- Python 3.12+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
python etf_uptrend_tracker.py
```

运行后会在 `output/` 目录下生成：
- `etf_uptrend_YYYYMMDD.json` - JSON 格式详细数据
- `etf_uptrend_YYYYMMDD.csv` - CSV 格式表格数据（带中文标题）

## 数据字段说明

| 字段 | 说明 |
|------|------|
| code | ETF 代码 |
| market | 市场（沪市/深市） |
| name | ETF 名称 |
| price_change_ratio_pct | 当日涨幅% |
| etf_up_trend_total_ratio | 上升趋势总涨幅% |
| etf_up_trend_duration | 上升趋势持续天数 |
| etf_up_trend_consecutive_up_days | 连涨天数 |
| etf_limit_up_stock_cnt | 涨停股数 |
| etf_limit_up_stock_pct | 涨停股占比% |

## GitHub Actions 自动化

### 配置 Secrets

在 GitHub 仓库设置中添加以下 Secrets：

1. **SMTP_USER** - QQ 邮箱账号
   - 例如：`your_email@qq.com`

2. **SMTP_PASSWORD** - QQ 邮箱授权码
   - 需要在 QQ 邮箱设置中开启 SMTP 服务并获取授权码

3. **RECIPIENTS** - 收件人邮箱
   - 多个收件人用逗号分隔：`email1@qq.com,email2@qq.com`

### 工作流说明

- **触发时间**：每天北京时间 9:40（UTC 时间 1:40）
- **手动触发**：支持在 GitHub Actions 页面手动运行
- **输出内容**：
  - 邮件通知任务完成情况
  - 附件包含 CSV 数据文件
  - GitHub Artifact 保存 10 天的输出文件

### 查看运行结果

1. 访问 GitHub Actions 页面：https://github.com/liyouguo/etfUpTrend/actions
2. 点击最近一次运行记录
3. 在 "Artifacts" 部分下载输出文件

## 注意事项

1. **Cookie 更新**：程序依赖同花顺网站的 Cookie，如果接口失效需要从浏览器 F12 抓包更新代码中的 `POOL_COOKIE` 和 `DETAIL_COOKIE`

2. **数据源**：数据来自同花顺 ETF 上升趋势页面，仅用于个人学习参考

3. **运行频率**：建议每天运行一次，避免频繁请求被限制

## 技术栈

- Python 3.12
- requests - HTTP 请求库
- GitHub Actions - 自动化工作流

## License

MIT License

## 更新日志

### v1.0.0 (2026-05-08)
- ✨ 初始版本发布
- ✨ 支持 ETF 上升趋势数据抓取
- ✨ JSON + CSV 双格式输出
- ✨ GitHub Actions 自动化定时任务
- ✨ 邮件通知功能
