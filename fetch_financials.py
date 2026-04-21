import yfinance as ticker_data
import json
import pandas as pd

# ==========================================
# 💡 你的追蹤清單 (可隨時自行增減)
# ==========================================
TARGET_STOCKS = ["2330", "2317", "2454", "2881", "2603", "2303"] 

def fetch_stock_financials(stock_id):
    symbol = f"{stock_id}.TW"
    stock = ticker_data.Ticker(symbol)
    try:
        # 分別抓取三大報表
        income_stmt = stock.financials        # 損益表
        balance_sheet = stock.balance_sheet   # 資產負債表
        cash_flow = stock.cashflow            # 現金流量表

        # 如果連損益表都沒有，代表這檔股票可能下市或代碼錯誤
        if income_stmt.empty: return None

        # 將三大報表全部打包進字典裡
        data = {
            "stock_id": stock_id,
            "name": stock.info.get('shortName', stock_id),
            "last_updated": pd.Timestamp.now().strftime('%Y-%m-%d'),
            "income_statement": format_df(income_stmt) if not income_stmt.empty else {},
            "balance_sheet": format_df(balance_sheet) if not balance_sheet.empty else {},
            "cash_flow": format_df(cash_flow) if not cash_flow.empty else {}
        }
        return data
    except Exception as e:
        print(f"抓取 {stock_id} 時發生錯誤: {e}")
        return None

def format_df(df):
    df_t = df.transpose()
    df_t.index = df_t.index.strftime('%Y') 
    
    # 填補空缺值，避免 JavaScript 讀取 NaN 時崩潰
    df_t = df_t.fillna(0) 
    
    return df_t.to_dict(orient='index')

if __name__ == "__main__":
    all_data = {}
    for sid in TARGET_STOCKS:
        print(f"正在抓取 {sid} 三大報表...")
        result = fetch_stock_financials(sid)
        if result: all_data[sid] = result

    with open('financial_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print("✅ 三大財報資料更新完成！")
