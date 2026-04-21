import yfinance as ticker_data
import json
import pandas as pd

# ==========================================
# 💡 追蹤清單
# ==========================================
# 將原本的 TARGET_STOCKS 替換成這個擴大版清單
TARGET_STOCKS = [
    # 半導體與電子代工
    "2330", "2317", "2454", "2308", "2382", "3231", "2356", "2303", "3711", "2408",
    # 金融保險
    "2881", "2882", "2891", "2886", "2884", "2885", "2892", "2880", "2883", "2887",
    # 傳產、航運與電信
    "2603", "2609", "2615", "2002", "1301", "1303", "1216", "2412", "3045", "4904"
]

def fetch_stock_financials(stock_id):
    symbol = f"{stock_id}.TW"
    stock = ticker_data.Ticker(symbol)
    try:
        # 1. 抓取基本資訊 (介紹)
        info = stock.info
        summary = info.get('longBusinessSummary', '尚無公司簡介資料。')
        
        # 2. 抓取三大報表
        income_stmt = stock.financials        
        balance_sheet = stock.balance_sheet   
        cash_flow = stock.cashflow            

        if income_stmt.empty: return None

        # 3. 抓取最新 5 則新聞
        raw_news = stock.news
        news_list = []
        for item in raw_news[:5]:
            pub_time = pd.to_datetime(item.get('providerPublishTime', 0), unit='s')
            pub_time = pub_time + pd.Timedelta(hours=8) 
            news_list.append({
                "title": item.get('title', '無標題'),
                "publisher": item.get('publisher', '未知來源'),
                "link": item.get('link', '#'),
                "time": pub_time.strftime('%Y-%m-%d %H:%M')
            })

        # 4. 打包資料
        data = {
            "stock_id": stock_id,
            "name": info.get('shortName', stock_id),
            "summary": summary,  # 🚀 新增公司簡介
            "last_updated": pd.Timestamp.now().strftime('%Y-%m-%d'),
            "income_statement": format_df(income_stmt),
            "balance_sheet": format_df(balance_sheet),
            "cash_flow": format_df(cash_flow),
            "news": news_list
        }
        return data
    except Exception as e:
        print(f"抓取 {stock_id} 錯誤: {e}")
        return None

def format_df(df):
    if df.empty: return {}
    df_t = df.transpose()
    df_t.index = df_t.index.strftime('%Y') 
    df_t = df_t.fillna(0) 
    return df_t.to_dict(orient='index')

if __name__ == "__main__":
    all_data = {}
    for sid in TARGET_STOCKS:
        print(f"正在抓取 {sid} 的完整資料...")
        result = fetch_stock_financials(sid)
        if result: all_data[sid] = result

    with open('financial_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print("✅ 資料庫升級完成！")
