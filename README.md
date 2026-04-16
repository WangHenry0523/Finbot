#  Finbot — AI 驅動的股票財報分析工具

> 結合 FinMind API、PostgreSQL、LangChain 與 Gemini LLM，自動化記錄股票庫存並以 AI Agent 分析財報數據。

---

##  目錄

- [專案說明](#專案說明)
- [功能架構](#功能架構)
- [專案結構](#專案結構)
- [環境需求](#環境需求)
- [安裝與設定](#安裝與設定)
- [使用方式](#使用方式)
- [資料說明](#資料說明)
- [技術棧](#技術棧)

---

## 專案說明

最初只是想用 Excel 記錄自己的股票收益，後來逐步演進成一個完整的自動化工具：

1. **自動記錄**股票庫存與交易紀錄
2. **串接 FinMind API** 抓取基本面財報數據
3. **存入 PostgreSQL** 進行結構化管理
4. **串接 LangChain + Gemini LLM**，以自然語言查詢財報資料

整個專案也作為學習 **LLM 串接** 與 **Docker 部署** 的實作練習。

---

## 功能架構

```
使用者輸入股票代號
        │
        ▼
┌─────────────────────┐
│ transaction_record  │  記錄交易、庫存、公司名稱
│       .py           │
└────────┬────────────┘
         │ companyname.json
         ▼
┌─────────────────────┐
│   company.ipynb     │  串接 FinMind API 抓取財報
│                     │  計算進階指標、輸出 Excel
└────────┬────────────┘
         │ financial_report.xlsx
         ▼
┌─────────────────────┐
│  xlsx → PostgreSQL  │  將財報資料寫入資料庫
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  LangChain Agent    │  自然語言查詢財報數據
│  (Gemini 2.5 Flash) │
└─────────────────────┘
```

---

## 專案結構

```
Finbot/
├── transaction_record.py     # 股票交易記錄主程式
├── company_finance.ipynb             # FinMind 財報抓取與處理
├── langchain_RAG.py                   # LangChain SQL Agent 查詢
├── .env.example              # 環境變數範本
├── data/
│   ├── transactions.csv      # 交易紀錄
│   ├── portfolio.csv         # 損益紀錄
│   ├── companyname.json      # 公司代號對照表
│   └── financial_report.xlsx # 財報輸出
└── README.md
```

---

## 環境需求

- Python 3.10+
- PostgreSQL 14+
- Docker（選用）

---

## 安裝與設定

### 1. 複製專案

```bash
git clone https://github.com/your-username/finbot.git
cd finbot
```

### 2. 安裝套件

```bash
pip install -r requirements.txt
```

### 3. 設定環境變數

複製範本並填入你的設定：

```bash
cp .env.example .env
```

`.env` 內容範例：

```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/finbot
FINMIND_TOKEN=your_finmind_token
```

### 4. 初始化資料庫

確認 PostgreSQL 服務已啟動，資料庫會在寫入時自動建立 table。

---

## 使用方式

### Step 1：記錄股票交易

```bash
python transaction_record.py
```

依照提示輸入股票代號與數量，資料會自動寫入：
- `transactions.csv` — 交易明細
- `portfolio.csv` — 損益紀錄
- `companyname.json` — 公司代號對照

### Step 2：抓取財報並寫入資料庫

開啟 `company.ipynb`，逐步執行：

1. 讀取 `companyname.json` 取得持股公司清單
2. 串接 FinMind API 抓取各季財報
3. 計算進階指標（毛利率、營業利率、淨利率）
4. 輸出 `financial_report.xlsx`
5. 將資料寫入 PostgreSQL

### Step 3：以自然語言查詢財報

```bash
python langchain_RAG.py
```

範例查詢：

```
請從 financial_quarterly 表格中，找出 stock_id 是 '2330' 且 year 是 2024 quarter 是 3 的 revenue 資料。
```

輸出結果：

```
The revenue for stock_id '2330' in year 2024 quarter 3 is 759,692,143,000.
```

---

## 資料說明

### financial_quarterly 資料表欄位

| 欄位 | 說明 |
|------|------|
| `stock_id` | 股票代號（如 `2330`） |
| `year` | 年度 |
| `quarter` | 季度（1–4） |
| `eps` | EPS（每股盈餘） |
| `roe` | ROE（股東權益報酬率） |
| `revenue` | 營收（千元） |
| `net_income` | 本期淨利-合併（千元） |
| `operating_income` | 營業利益（千元） |
| `gross_margin` | 毛利率（%） |
| `operating_margin` | 營業利率（%） |
| `net_margin` | 淨利率（%） |

---

## 技術棧

| 分類 | 工具 |
|------|------|
| 語言 | Python 3.10+ |
| LLM 框架 | LangChain |
| LLM 模型 | Google Gemini 2.5 Flash |
| 財報資料來源 | FinMind API |
| 資料庫 | PostgreSQL |
| ORM / 連線 | SQLAlchemy |
| 報表輸出 | openpyxl |
| 容器化 | Docker |

---

##  注意事項

- `.env` 檔案含有 API 金鑰，請勿上傳至 GitHub，確認已加入 `.gitignore`
- FinMind 免費方案有每日 API 呼叫上限，大量抓取請注意配額
- Gemini API 同樣有免費用量限制，請參閱 [Google AI Studio](https://aistudio.google.com/) 的方案說明
