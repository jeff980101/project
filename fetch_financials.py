import yfinance as ticker_data
import json
import pandas as pd
import os

def fetch_stock_financials(stock_id):
    # 台股代碼需要加上 .TW 結尾，例如 2330.TW
    symbol = f"{stock_id}.TW"
    stock = ticker_data.Ticker(symbol)
    
    try:
        # 抓取三大表 (預設抓取最近四年的年度報表)
        # .financials -> 損益表
        # .balance_sheet -> 資產負債表
        # .cashflow -> 現金流量表
        
        income_stmt = stock.financials
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow

        # 如果抓不到資料就跳過
        if income_stmt.empty:
            print(f"找不到 {stock_id} 的資料")
            return None

        # 整理成 JSON 格式：將 DataFrame 轉為字典，並處理時間格式
        data = {
            "stock_id": stock_id,
            "last_updated": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            "income_statement": format_df(income_stmt),
            "balance_sheet": format_df(balance_sheet),
            "cash_flow": format_df(cash_flow)
        }
        return data
    except Exception as e:
        print(f"抓取 {stock_id} 時發生錯誤: {e}")
        return None

def format_df(df):
    """將 Pandas DataFrame 轉為適合 JSON 的格式"""
    # 轉置表格，讓日期變成 Key
    df_t = df.transpose()
    # 將 Timestamp 轉為字串日期 'YYYY-MM-DD'
    df_t.index = df_t.index.strftime('%Y-%m-%d')
    # 轉為字典
    return df_t.to_dict(orient='index')

if __name__ == "__main__":
    # 你想要追蹤的股票清單
    target_stocks = ["2330", "2317", "2454", "2881"] 
    all_data = {}

    for sid in target_stocks:
        print(f"正在抓取 {sid}...")
        result = fetch_stock_financials(sid)
        if result:
            all_data[sid] = result

    # 儲存為 JSON 檔案
    with open('financial_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    
    print("✅ 財報數據已成功儲存至 financial_data.json")
