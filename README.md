# Finbot
## 專案說明
原本只是想要利用excel紀錄自己的股票收益而已，但後來想到說是不是可以直接程式幫忙紀錄到excel裡面就做了這個。然後因為沒有碰過大語言模型串接跟Docker，所以決定在這個主題上增加這兩個部分。總體而言，這個專案是由python程式
紀錄你的股票收益跟庫存，然後company.ipynb這個程式會根據你購買股票的公司幫你從FinMind上抓取對應的財報資料並利用PostreSQL存入資料庫中，最後利用langchain架構串接LLM模型製作一個AI agent去幫你分析財報和你打算所購買股票公司的數據。
## 紀錄股票庫存、交易紀錄
transaction_record.py負責記錄購買的股票，只要在Terminal輸入你購買的股票代號以及數量，會自動將其儲存於transactions.csv內，另外購買或售出股票時的收益增減紀錄於portfolio.csv，還有將股票所屬公司的名稱與代號紀錄於companyname.json，以利後面進行FinMind抓取資料。
<img width="828" height="263" alt="image" src="https://github.com/user-attachments/assets/0a0254a5-2601-4edf-bbff-17d1f000ec60" />
## 串接FinMind API 收集股票基本面數據
當我們購買股票時會將發行該股票公司紀錄於companyname.json，此處調用FinMind API抓取相關基本面數據，並透過基礎數據計算出部分進階數據。
數據如下:
* eps: "EPS(每股盈餘)",
* roe: "ROE(股東權益報酬率)",
* revenue: "營收(千元)",
* net_income: "本期淨利(合併)(千元)",
* operating_income: "營業利益(千元)",
* gross_margin:"毛利率(%)",
* operating_margin:"營業利率(%)",
* net_margin: "淨利率(%)"
並生成對應報表financial_report.xlsx
<img width="828" height="699" alt="image" src="https://github.com/user-attachments/assets/cb9cc68b-1112-4fc1-9058-67680bdd4d80" />
## 轉為postgresql
讀取financial_report.xlsx，並寫入PostgreSQL。
## 串接Langchain
得到資料庫後串接LLM模型，此處使用的是gemini-2.5-flash，然後連線資料庫並建立 SQL Agent 執行器，輸入問題並等待回應。
<img width="1178" height="53" alt="image" src="https://github.com/user-attachments/assets/955ded6e-c9ca-46fc-ad40-6b602a5a644c" />
<img width="1118" height="181" alt="image" src="https://github.com/user-attachments/assets/43b19d72-193c-4d73-8f24-3905890040d9" />

