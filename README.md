# 📈 個人財經小工具-企業財報分析系統 (Corporate Financial Analysis System)

這是一個基於 Python 爬蟲與 GitHub Pages 靜態網頁技術打造的「自動化企業財報與新聞視覺化系統」。
本專案旨在解決散戶投資人查詢財務數據時，面臨的資訊零碎、缺乏視覺化比較工具等痛點，提供一個快速、直觀且無伺服器成本 (Serverless) 的解決方案。

## ✨ 核心特色功能

* **⚡ 自動化資料流 (Data Pipeline)**：利用 GitHub Actions 定期執行 Python 爬蟲，自動從 Yahoo Finance 抓取指定台灣權值股的財報與新聞，並更新至 JSON 靜態資料庫。
* **📊 互動式視覺化圖表**：前端採用 `Chart.js`，將枯燥的財報數據轉化為直觀的長條圖與折線圖。
* **⚔️ 同業 PK 比較模式**：支援「主代碼」與「比較代碼」雙軌輸入，可將兩家公司的財報數據並列呈現，優劣勢一目了然。
* **🧮 進階財務比率動態計算**：除了原始的絕對金額（如總營收、淨利），前端加入了動態計算引擎，即時算出「毛利率 (%)」、「EPS (每股盈餘)」、「ROE (股東權益報酬率)」等關鍵指標。

## 🛠️ 技術架構 (Tech Stack)

* **前端 (Frontend)**：HTML5, CSS3, JavaScript (ES6), [Chart.js](https://www.chartjs.org/)
* **資料爬蟲 (Data Extraction)**：Python 3, `yfinance`, `pandas`
* **自動化與部署 (CI/CD & Hosting)**：GitHub Actions, GitHub Pages

## 📂 專案結構

```text
├── fetch_financials.py     # Python 爬蟲主程式 (負責抓取資料並延遲防阻擋)
├── financial.html          # 前端核心網頁 (包含版面佈局、圖表渲染與計算邏輯)
├── index.html              # 系統入口首頁
├── financial_data.json     # 系統的靜態資料庫 (由 GitHub Actions 自動生成/更新)
└── README.md               # 專案說明文件
