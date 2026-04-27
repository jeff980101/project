import yfinance as ticker_data
import pandas as pd
import json
import time # 👈 新增：用來讓程式暫停的模組
from datetime import datetime # 👈 新增：用來處理新聞時間

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
        # 1. 抓取基本資訊 (加入防護機制，如果抓不到不至於整個崩潰)
        info = {}
        try:
            info = stock.info
        except:
            print(f"  警告：無法獲取 {stock_id} 的 info 資料")
            
        summary = info.get('longBusinessSummary', '目前無法取得公司簡介。')
        name = info.get('longName', info.get('shortName', str(stock_id)))

        # 2. 抓取最新股價
        current_price = 0
        try:
            current_price = stock.fast_info['last_price']
        except:
            hist = stock.history(period="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]

        # 3. 抓取財報 (轉為字典格式)
        try:
            income_df = stock.financials.fillna(0).to_dict() if not stock.financials.empty else {}
            balance_df = stock.balance_sheet.fillna(0).to_dict() if not stock.balance_sheet.empty else {}
            cash_df = stock.cashflow.fillna(0).to_dict() if not stock.cashflow.empty else {}
            
            # 將 datetime key 轉為字串 (YYYY)
            income_df = {str(k)[:4]: v for k, v in income_df.items()}
            balance_df = {str(k)[:4]: v for k, v in balance_df.items()}
            cash_df = {str(k)[:4]: v for k, v in cash_df.items()}
        except Exception as e:
            print(f"  警告：無法獲取 {stock_id} 的財報 - {e}")
            income_df, balance_df, cash_df = {}, {}, {}

        # 4. 抓取新聞與正確解析時間
        news_list = []
        try:
            raw_news = stock.news
            for n in raw_news[:5]: # 取前 5 則
                pub_time = n.get('providerPublishTime', 0)
                time_str = datetime.fromtimestamp(pub_time).strftime('%Y-%m-%d %H:%M') if pub_time > 0 else "未知時間"
                
                news_list.append({
                    "title": n.get('title', '無標題'),
                    "link": n.get('link', '#'),
                    "publisher": n.get('publisher', '未知來源'),
                    "time": time_str
                })
        except Exception as e:
            print(f"  警告：無法獲取 {stock_id} 的新聞 - {e}")

        return {
            "name": name,
            "summary": summary,
            "currentPrice": current_price,
            "income_statement": income_df,
            "balance_sheet": balance_df,
            "cash_flow": cash_df,
            "news": news_list
        }

    except Exception as e:
        print(f"❌ 抓取 {stock_id} 發生嚴重錯誤: {e}")
        return None

# ==========================================
# 🚀 主程式執行區
# ==========================================
if __name__ == "__main__":
    all_data = {}
    
    for sid in TARGET_STOCKS:
        print(f"正在抓取 {sid} 的完整資料...")
        result = fetch_stock_financials(sid)
        if result:
            all_data[sid] = result
            
        # ⚠️ 關鍵：每次抓完一檔股票，強迫程式暫停 3 秒，避免被 Yahoo 封鎖
        time.sleep(3) 

    # 存檔
    with open('financial_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
        
    print(f"🎉 全部資料抓取完成！共取得 {len(all_data)} 檔股票資料。")
