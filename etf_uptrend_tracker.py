"""
同花顺ETF上升趋势池数据抓取工具
- 接口1: 获取上升趋势ETF列表（代码+名称+市场）
- 接口2: 获取上升趋势详细指标（总涨幅、持续天数、连涨天数、涨停占比）
- 输出: JSON数据 + 控制台TOP排名

Cookie过期后重新从浏览器F12抓包替换即可
"""

import requests
import json
import os
import csv
from datetime import datetime

# ============ 配置区（Cookie过期需更新） ============
POOL_COOKIE = "v=A-hg3lGuFXCmUTn0KVen6KGHvdz_EUwbLnUgn6IZNGNW_YfDSiEcq36F8C3x; _clsk=he4oka%7C1778084894694%7C2%7C1%7C; _clck=1x2613x%7C2%7Cg5t%7C0%7C0; IFUserCookieKey={\"userid\":\"438819001\",\"escapename\":\"%25u6715%25u7684%25u540e%25u5bab%25u53ea%25u6709\",\"custid\":\"100121177685\"}; cuc=1eab8703c6d74d3a8e8b1eb20d0f35b3; sess_tk=eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6InNlc3NfdGtfMSIsImJ0eSI6InNlc3NfdGsifQ.eyJqdGkiOiI0M2FiODMzNTMzMzBmZWZhMmE0ZWFkZjIyMDJjZWQ5ZDEiLCJpYXQiOjE3NzYzMTIyMTgsImV4cCI6MTc3ODk5MDYxOCwic3ViIjoiNDM4ODE5MDAxIiwiaXNzIjoidXBhc3MuMTBqcWthLmNvbS5jbiIsImF1ZCI6IjIwMjMwODA0OTA3NTEyOTIiLCJhY3QiOiJvZmMiLCJjdWhzIjoiYWJjNTZlZjlkYmRlMGE1NGQyZDAzYWI3MDhkMGRkOGU2ODAxZjIzMmRkNmZhOGY5Y2MyMTI5Mzg3NjZhOTZlYiJ9.02HQMVj_an7DPvdcmhnOVuWpNpM_rFMe_zIGbGoHXFWZ4lCNA5y29k7rFNjo2bcyqj1oW4hbERZmRdri41GO4g; ticket=80fdc178173ecb806504deee82ed27f5; u_name=%EB%DE%B5%C4%BA%F3%B9%AC%D6%BB%D3%D0; user=MDrr3rXEuvO5rNa709A6Ok5vbmU6NTAwOjQ0ODgxOTAwMTo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxMDEsNDA7MiwxLDQwOzMsMSw0MDs1LDEsNDA7OCwwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMSw0MDsxMDIsMSw0MDoxNjo6OjQzODgxOTAwMToxNzc2MzEyMjE4Ojo6MTUxOTcxMTM4MDoyNjc4NDAwOjA6MTlkZWQyYzIwZjJhZDRlMmFmYWZlMzAzMzM1ODNhYjQzOjox; user_status=0; userid=438819001; locale=en-us"

DETAIL_COOKIE = "ticket=80fdc178173ecb806504deee82ed27f5; user=MDrr3rXEuvO5rNa709A6Ok5vbmU6NTAwOjQ0ODgxOTAwMTo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxMDEsNDA7MiwxLDQwOzMsMSw0MDs1LDEsNDA7OCwwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMSw0MDsxMDIsMSw0MDoxNjo6OjQzODgxOTAwMToxNzc2MzEyMjE4Ojo6MTUxOTcxMTM4MDoyNjc4NDAwOjA6MTlkZWQyYzIwZjJhZDRlMmFmYWZlMzAzMzM1ODNhYjQzOjox"

OUTPUT_DIR = "./output"

# ============ 接口地址 ============
POOL_URL = "https://fund.10jqka.com.cn/quotation/fund_pool/v2/query"
DETAIL_URL = "https://dataq.10jqka.com.cn/fetch-data-server/fetch/v1/specific_data"


def _pool_headers():
    return {
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15",
        'Content-Type': "application/json",
        'hexin-v': "A-hg3lGuFXCmUTn0KVen6KGHvdz_EUwbLnUgn6IZNGNW_YfDSiEcq36F8C3x",
        'Origin': "https://fund.10jqka.com.cn",
        'Referer': "https://fund.10jqka.com.cn/thsjj-jj-fe-market-domain/uptrend-list/index.html",
        'Cookie': POOL_COOKIE,
    }


def _detail_headers():
    return {
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15",
        'Content-Type': "application/json",
        'Origin': "https://fund.10jqka.com.cn",
        'Referer': "https://fund.10jqka.com.cn/",
        'X-Auth-ProgId': "7047",
        'X-Auth-Version': "1.0",
        'Platform': "hxkline",
        'X-Auth-AppName': "AINVEST",
        'X-Auth-Type': "ths",
        'Source-Id': "hxkline-FW_ETFUpTrend_Page",
        'X-Fuyao-Auth': "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRob3JpemVyX25hbWVzcGFjZSI6ImNvbW1vbi1ocS1hZ2dyIiwibGljZW5zZWVfdHlwZSI6IkZST05UX0FQUCIsImxpY2Vuc2VlX25hbWVzcGFjZSI6Imh4a2xpbmUtRldfRVRGVXBUcmVuZF9QYWdlIn0.ZSEljLYXljW_vHLvgrAw6F_T2ND8UB4Vktkj7Zs2e-A",
        'Cookie': DETAIL_COOKIE,
    }


def fetch_uptrend_pool():
    """接口1: 获取上升趋势ETF列表"""
    payload = {
        "businessKey": "etfUpTrend",
        "businessPoolKey": "1f3b943f-c5f4-312f-95b9-64de02642115",
        "custom": {"fieldList": ["subMarket"], "limit": 10000, "offset": 0,  "uniqueTracking": True,}
    }
    resp = requests.post(POOL_URL, json=payload, headers=_pool_headers())
    resp.raise_for_status()
    data = resp.json()

    if data.get("status_code") != 0:
        raise Exception(f"接口1错误: {data.get('status_msg')}")

    items = data['data']['itemList']
    print(f"[池子列表] 共{data['data']['total']}只, 返回{len(items)}只")
    return items


def fetch_detail(code_list, batch_size=200):
    """接口2: 分批获取上升趋势详情指标"""
    all_results = []

    for i in range(0, len(code_list), batch_size):
        batch = code_list[i:i + batch_size]
        payload = {
            "code_selectors": {
                "include": [{"type": "stock_code", "values": batch}],
                "exclude": [], "intersection": []
            },
            "indexes": [
                {"index_id": "security_name"},
                {"index_id": "price_change_ratio_pct", "source_id": "199112", "req_uniq_id": "199112", "needSubscribe": True},
                {"index_id": "etf_up_trend_total_ratio", "needSubscribe": True},
                {"index_id": "etf_up_trend_duration"},
                {"index_id": "etf_up_trend_consecutive_up_days"},
                {"index_id": "etf_limit_up_stock_cnt"},
                {"index_id": "etf_limit_up_stock_pct"},
            ],
            "page_info": {"page_size": len(batch), "page_begin": 0, "code_begin": 0},
            "sort": [{"idx": 1, "type": "desc"}]
        }

        resp = requests.post(DETAIL_URL, json=payload, headers=_detail_headers())
        resp.raise_for_status()
        data = resp.json()

        batch_data = data.get('data', {}).get('data', [])
        all_results.extend(batch_data)
        print(f"  [详情] 批次{i // batch_size + 1}: {len(batch_data)}条")

    print(f"[详情] 总计: {len(all_results)}条")
    # print(all_results[0])
    return all_results


def parse_detail(raw_list):
    """解析详情数据（idx按indexes顺序：0=name,1=total_ratio,2=duration,3=consecutive_days,4=limit_up_cnt,5=limit_up_pct）"""
    parsed = []
    for item in raw_list:
        market, code = item['code'].split(':')
        vals = {v['idx']: v['value'] for v in item['values']}
        # print(vals)

        parsed.append({
            "code": code,
            "market": "沪市" if market == "20" else "深市",
            "name": vals.get(0, ""),
            'price_change_ratio_pct': vals.get(1,''),#当日涨幅%
            "etf_up_trend_total_ratio": vals.get(2,''),       # 上升趋势总涨幅%
            "etf_up_trend_duration": vals.get(3,''),           # 上升趋势持续天数
            "etf_up_trend_consecutive_up_days": vals.get(4,''),   # 连涨天数
            "etf_limit_up_stock_cnt": vals.get(5,''),       # 涨停股数
            "etf_limit_up_stock_pct": vals.get(6,''),       # 涨停股占比%
          
        })
    return parsed


def print_top(parsed, n=30):
    """打印TOP排名"""
    by_ratio = sorted(parsed, key=lambda x: float(x['etf_limit_up_stock_pct'] or 0), reverse=True)
    print(f"\nTOP{n} 上升趋势涨停股占比最高")
    print(f"{'排名':<4} {'代码':<8} {'市场':<4} {'名称':<22} {'当日涨幅%':>8} {'总涨幅%':>8} {'持续天数':>8} {'连涨':>4} {'涨停股数':>4} {'涨停占比%':>8}")
    print("-" * 70)
    for i, p in enumerate(by_ratio[:n]):
        print(f"{i+1:<4} {p['code']:<8} {p['market']:<4} {p['name'][:20]:<22} {str(p['price_change_ratio_pct']):>8} {str(p['etf_up_trend_total_ratio']):>8} {str(p['etf_up_trend_duration']):>8} {str(p['etf_up_trend_consecutive_up_days']):>8} {str(p['etf_limit_up_stock_cnt']):>4} {str(p['etf_limit_up_stock_pct']):>8}")



    # by_dur = sorted(parsed, key=lambda x: int(x['etf_up_trend_duration'] or 0), reverse=True)
    # print(f"\nTOP{n} 上升趋势持续天数最长")
    # print(f"{'排名':<4} {'代码':<8} {'市场':<4} {'名称':<22} {'当日涨幅%':>8} {'总涨幅%':>8} {'持续天数':>8} {'总涨幅%':>8} {'连涨':>4}")
    # print("-" * 60)
    # for i, p in enumerate(by_dur[:n]):
    #     pass
        # print(f"{i+1:<4} {p['code']:<8} {p['market']:<4} {p['name'][:20]:<22} {str(p['etf_up_trend_duration']):>8} {str(p['etf_up_trend_total_ratio']):>8} {str(p['etf_up_trend_consecutive_up_days']):>4}")


THEMES = {
    "芯片/半导体": ["芯片", "半导体", "集成电路"],
    "人工智能/AI": ["人工智能", "AI"],
    "科创板": ["科创板", "科创50", "科创成长", "科创200"],
    "数字经济": ["数字经济"],
    "有色金属": ["有色金属", "矿业"],
    "新能源": ["新能源", "光伏", "电池", "风电"],
    "消费": ["消费"],
    "医药": ["医药", "医疗"],
    "金融": ["银行", "券商", "金融", "保险"],
    "港股/恒生": ["港股", "恒生", "港交所"],
    "机器人": ["机器人"],
    "军工": ["军工", "国防"],
    "汽车/智驾": ["汽车", "智能驾驶"],
    "红利": ["红利"],
    "黄金": ["黄金"],
    "纳指/标普": ["纳指", "标普"],
}


def print_themes(parsed):
    """打印主题分布"""
    print(f"\n主题分布")
    print("-" * 30)
    for theme, kws in sorted(THEMES.items()):
        count = sum(1 for p in parsed if any(kw in p['name'] for kw in kws))
        if count > 0:
            print(f"  {theme}: {count}只")


def main():
    today = datetime.now().strftime("%Y%m%d")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Step1: 池子列表
    pool_items = fetch_uptrend_pool()

    # Step2: 详情数据
    code_list = [f"{item[0]}:{item[1]}" for item in pool_items]
    raw = fetch_detail(code_list)

    # Step3: 解析保存
    parsed = parse_detail(raw)

    out_file = os.path.join(OUTPUT_DIR, f"etf_uptrend_{today}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)
    print(f"已保存：{out_file}")
    
    # 保存为 CSV 格式
    csv_file = os.path.join(OUTPUT_DIR, f"etf_uptrend_{today}.csv")
    fieldnames = ["code",
    "market",
    "name",
    "price_change_ratio_pct",
    "etf_up_trend_total_ratio",
    "etf_up_trend_duration",
    "etf_up_trend_consecutive_up_days",
    "etf_limit_up_stock_cnt",
    "etf_limit_up_stock_pct"]
    
    chinese_headers = ["代码",
    "市场",
    "名称",
    "当日涨幅%",
    "上升趋势总涨幅%",
    "上升趋势持续天数",
    "连涨天数",
    "涨停股数",
    "涨停股占比%"]
    
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        f.write(",".join(chinese_headers) + "\n")
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerows(parsed)
    print(f"已保存：{csv_file}")
    


    # Step4: 排名和分布
    print_top(parsed)
    # print_themes(parsed)


if __name__ == "__main__":
    main()
