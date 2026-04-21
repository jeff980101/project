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
        # 1. 抓取三大報表
        income_stmt = stock.financials        
        balance_sheet = stock.balance_sheet   
        cash_flow = stock.cashflow            

        if income_stmt.empty: return None

        # 2. 抓取最新 5 則相關新聞 (🚀 這是這次新增的功能)
        raw_news = stock.news
        news_list = []
        for item in raw_news[:5]:
            # Yahoo 給的是 Unix 時間戳，我們把它轉換成台灣時間並格式化
            pub_time = pd.to_datetime(item.get('providerPublishTime', 0), unit='s')
            pub_time = pub_time + pd.Timedelta(hours=8) 
            
            news_list.append({
                "title": item.get('title', '無標題'),
                "publisher": item.get('publisher', '未知來源'),
                "link": item.get('link', '#'),
                "time": pub_time.strftime('%Y-%m-%d %H:%M')
            })

        # 3. 打包所有資料
        data = {
            "stock_id": stock_id,
            "name": stock.info.get('shortName', stock_id),
            "last_updated": pd.Timestamp.now().strftime('%Y-%m-%d'),
            "income_statement": format_df(income_stmt) if not income_stmt.empty else {},
            "balance_sheet": format_df(balance_sheet) if not balance_sheet.empty else {},
            "cash_flow": format_df(cash_flow) if not cash_flow.empty else {},
            "news": news_list  # 🚀 將新聞清單加進資料庫中
        }
        return data
    except Exception as e:
        print(f"抓取 {stock_id} 時發生錯誤: {e}")
        return None

def format_df(df):
    df_t = df.transpose()
    df_t.index = df_t.index.strftime('%Y') 
    df_t = df_t.fillna(0) 
    return df_t.to_dict(orient='index')

if __name__ == "__main__":
    all_data = {}
    for sid in TARGET_STOCKS:
        print(f"正在抓取 {sid} 的財報與即時新聞...")
        result = fetch_stock_financials(sid)
        if result: all_data[sid] = result

    with open('financial_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print("✅ 財報與即時新聞更新完成！")
