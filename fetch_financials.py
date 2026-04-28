import yfinance as ticker_data
import pandas as pd
import json
import time
from datetime import datetime

TARGET_STOCKS = [
    # 半導體與電子代工
    "2330", "2317", "2454", "2308", "2382", "3231", "2356", "2303", "3711", "2408",
    # 金融保險
    "2881", "2882", "2891", "2886", "2884", "2885", "2892", "2880", "2883", "2887",
    # 傳產、航運與電信
    "2603", "2609", "2615", "2002", "1301", "1303", "1216", "2412", "3045", "4904"
]

# ==========================================
# 📊 財務健康評分系統
# ==========================================

def _interpolate(val, thresholds, scores, higher_is_better):
    """
    依照門檻值與方向，計算線性插值後的分數（0～20 分）。
    higher_is_better=True  → 數值越大越好（ROE、毛利率、淨利率、流動比率）
    higher_is_better=False → 數值越小越好（負債比率）
    """
    t, s = thresholds, scores
    if higher_is_better:
        if val >= t[4]: return s[4]
        if val >= t[3]: return s[3] + (s[4]-s[3]) * (val-t[3]) / (t[4]-t[3])
        if val >= t[2]: return s[2] + (s[3]-s[2]) * (val-t[2]) / (t[3]-t[2])
        if val >= t[1]: return s[1] + (s[2]-s[1]) * (val-t[1]) / (t[2]-t[1])
        if val >= t[0]: return s[0] + (s[1]-s[0]) * (val-t[0]) / (t[1]-t[0])
        return 0.0
    else:
        if val <= t[4]: return s[4]
        if val <= t[3]: return s[3] + (s[4]-s[3]) * (t[3]-val) / (t[3]-t[4])
        if val <= t[2]: return s[2] + (s[3]-s[2]) * (t[2]-val) / (t[2]-t[3])
        if val <= t[1]: return s[1] + (s[2]-s[1]) * (t[1]-val) / (t[1]-t[2])
        if val <= t[0]: return s[0] + (s[1]-s[0]) * (t[0]-val) / (t[0]-t[1])
        return 0.0

def calc_health_score(income_dict, balance_dict):
    """
    從最新一年的財報計算五大指標，回傳評分卡字典。

    輸出格式：
    {
        "metrics": {
            "roe":          {"value": 26.5, "score": 20.0, "unit": "%"},
            "gross_margin": {"value": 53.0, "score": 20.0, "unit": "%"},
            "net_margin":   {"value": 36.4, "score": 20.0, "unit": "%"},
            "debt_ratio":   {"value": 42.3, "score": 13.5, "unit": "%"},
            "current_ratio":{"value":  2.2, "score": 19.0, "unit": "倍"},
        },
        "total_score": 92.5,   # 各項加總（滿分 100）
        "grade": "A",
        "grade_label": "財務健康"
    }
    None 表示當年資料不足，無法計算。
    """
    # 取最新年度的損益表與資產負債表（第一個 key 即最新）
    if not income_dict or not balance_dict:
        return None

    latest_income_year  = next(iter(income_dict))
    latest_balance_year = next(iter(balance_dict))
    inc = income_dict[latest_income_year]
    bal = balance_dict[latest_balance_year]

    def safe(d, *keys):
        """依序嘗試多個 key，回傳第一個非零數值，否則回傳 None。"""
        for k in keys:
            v = d.get(k, 0)
            if v and v != 0:
                return float(v)
        return None

    # --- 從財報擷取原始數值 ---
    total_revenue    = safe(inc, "Total Revenue")
    gross_profit     = safe(inc, "Gross Profit")
    net_income       = safe(inc, "Net Income")
    total_assets     = safe(bal, "Total Assets")
    total_liab       = safe(bal, "Total Liabilities Net Minority Interest", "Total Liab")
    equity           = safe(bal, "Stockholders Equity", "Total Stockholder Equity", "Common Stock Equity")
    current_assets   = safe(bal, "Current Assets")
    current_liab     = safe(bal, "Current Liabilities")

    metrics = {}

    # 1. ROE（股東權益報酬率）
    if net_income and equity and equity != 0:
        roe = net_income / equity * 100
        metrics["roe"] = {
            "value": round(roe, 2),
            "score": round(_interpolate(roe, [5,10,15,20,25], [0,8,13,17,20], True), 2),
            "unit": "%"
        }

    # 2. 毛利率
    if gross_profit and total_revenue and total_revenue != 0:
        gm = gross_profit / total_revenue * 100
        metrics["gross_margin"] = {
            "value": round(gm, 2),
            "score": round(_interpolate(gm, [10,20,30,45,60], [0,5,10,16,20], True), 2),
            "unit": "%"
        }

    # 3. 淨利率
    if net_income and total_revenue and total_revenue != 0:
        nm = net_income / total_revenue * 100
        metrics["net_margin"] = {
            "value": round(nm, 2),
            "score": round(_interpolate(nm, [2,5,8,12,18], [0,5,10,15,20], True), 2),
            "unit": "%"
        }

    # 4. 負債比率（越低越好）
    if total_liab and total_assets and total_assets != 0:
        dr = total_liab / total_assets * 100
        metrics["debt_ratio"] = {
            "value": round(dr, 2),
            "score": round(_interpolate(dr, [80,65,50,35,20], [0,5,10,15,20], False), 2),
            "unit": "%"
        }

    # 5. 流動比率
    if current_assets and current_liab and current_liab != 0:
        cr = current_assets / current_liab
        metrics["current_ratio"] = {
            "value": round(cr, 2),
            "score": round(_interpolate(cr, [0.8,1.0,1.5,2.0,2.5], [0,5,10,15,20], True), 2),
            "unit": "倍"
        }

    if not metrics:
        return None

    total = round(sum(m["score"] for m in metrics.values()), 1)

    # 若指標不足 5 項，按比例換算至 100 分
    if len(metrics) < 5:
        total = round(total / len(metrics) * 5, 1)

    grade_map = [
        (85, "A", "財務健康"),
        (70, "B", "體質不錯"),
        (55, "C", "有待改善"),
        (40, "D", "需要注意"),
        ( 0, "F", "高風險"),
    ]
    grade, grade_label = next(
        (g, l) for threshold, g, l in grade_map if total >= threshold
    )

    return {
        "metrics": metrics,
        "total_score": total,
        "grade": grade,
        "grade_label": grade_label
    }

# ==========================================
# 📥 個股資料抓取
# ==========================================

def fetch_stock_financials(stock_id):
    symbol = f"{stock_id}.TW"
    stock = ticker_data.Ticker(symbol)

    try:
        # 1. 基本資訊
        info = {}
        try:
            info = stock.info                              # ✅ 修正：移除 Markdown 連結語法
        except Exception:
            print(f"  警告：無法獲取 {stock_id} 的 info 資料")

        summary = info.get("longBusinessSummary", "目前無法取得公司簡介。")
        name    = info.get("longName", info.get("shortName", str(stock_id)))

        # 2. 最新股價
        current_price = 0
        try:
            current_price = stock.fast_info["last_price"]  # ✅ 修正：移除斷行
        except Exception:
            hist = stock.history(period="1d")
            if not hist.empty:
                current_price = hist["Close"].iloc[-1]

        # 3. 財報（轉為以年份字串為 key 的字典）
        income_dict, balance_dict, cash_dict = {}, {}, {}
        try:
            if not stock.financials.empty:
                income_dict  = {str(k)[:4]: v for k, v in
                                stock.financials.fillna(0).to_dict().items()}
            if not stock.balance_sheet.empty:
                balance_dict = {str(k)[:4]: v for k, v in
                                stock.balance_sheet.fillna(0).to_dict().items()}
            if not stock.cashflow.empty:
                cash_dict    = {str(k)[:4]: v for k, v in
                                stock.cashflow.fillna(0).to_dict().items()}
        except Exception as e:
            print(f"  警告：無法獲取 {stock_id} 的財報 - {e}")

        # 4. 新聞
        news_list = []
        try:
            for n in stock.news[:5]:                       # ✅ 修正：移除 Markdown 連結語法
                pub_time = n.get("providerPublishTime", 0)
                time_str = (datetime.fromtimestamp(pub_time).strftime("%Y-%m-%d %H:%M")
                            if pub_time > 0 else "未知時間")
                news_list.append({
                    "title":     n.get("title", "無標題"),
                    "link":      n.get("link", "#"),
                    "publisher": n.get("publisher", "未知來源"),
                    "time":      time_str
                })
        except Exception as e:
            print(f"  警告：無法獲取 {stock_id} 的新聞 - {e}")

        # 5. ✨ 財務健康評分（新增）
        health = calc_health_score(income_dict, balance_dict)
        if health:
            print(f"  → 財務評分：{health['total_score']} 分 ({health['grade']} {health['grade_label']})")
        else:
            print(f"  → 財務評分：資料不足，略過")

        return {
            "name":             name,
            "summary":          summary,
            "currentPrice":     current_price,
            "income_statement": income_dict,
            "balance_sheet":    balance_dict,
            "cash_flow":        cash_dict,
            "news":             news_list,
            "health_score":     health        # ✨ 新增欄位
        }

    except Exception as e:
        print(f"❌ 抓取 {stock_id} 發生嚴重錯誤: {e}")
        return None

# ==========================================
# 🚀 主程式
# ==========================================

if __name__ == "__main__":
    all_data = {}

    for sid in TARGET_STOCKS:
        print(f"\n正在抓取 {sid} 的完整資料...")
        result = fetch_stock_financials(sid)
        if result:
            all_data[sid] = result

        time.sleep(3)  # 每檔間隔 3 秒，避免被 Yahoo Finance 封鎖

    with open("financial_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    print(f"\n🎉 完成！共取得 {len(all_data)} 檔股票資料，已儲存至 financial_data.json")
