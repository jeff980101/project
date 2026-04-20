import yfinance as ticker_data
import json
import pandas as pd

# ==========================================
# 💡 在這裡輸入你想要追蹤的股票清單
# ==========================================
TARGET_STOCKS = ["2330", "2317", "2454", "2881", "2603", "2303"] 

def fetch_stock_financials(stock_id):
    symbol = f"{stock_id}.TW"
    stock = ticker_data.Ticker(symbol)
    try:
        # 抓取損益表 (Income Statement)
        income_stmt = stock.financials
        if income_stmt.empty: return None

        # 我們主要抓取：總收入、毛利、淨利
        data = {
            "stock_id": stock_id,
            "name": stock.info.get('shortName', stock_id),
            "last_updated": pd.Timestamp.now().strftime('%Y-%m-%d'),
            "income_statement": format_df(income_stmt)
        }
        return data
    except:
        return None

def format_df(df):
    df_t = df.transpose()
    df_t.index = df_t.index.strftime('%Y') # 只保留年份，方便繪圖
    # 👇 新增這行：將所有空缺資料(NaN)替換為數字 0，確保 JavaScript 能看懂！
    df_t = df_t.fillna(0)
    return df_t.to_dict(orient='index')

if __name__ == "__main__":
    all_data = {}
    for sid in TARGET_STOCKS:
        print(f"正在抓取 {sid}...")
        result = fetch_stock_financials(sid)
        if result: all_data[sid] = result

    with open('financial_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print("✅ 財報資料更新完成！")
