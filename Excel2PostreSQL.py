import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
load_dotenv()
db_url = os.getenv("database_url")
# === 1. PostgreSQL 連線資訊 ===
engine = create_engine(db_url)

# === 2. 讀取 Excel 所有 Sheets ===
excel_path = "output\\financial_report.xlsx"
sheets = pd.read_excel(excel_path, sheet_name=None)

rows = []

for sheet_name, df in sheets.items():
    stock_id = sheet_name.split("_")[0]

    df = df.set_index("type").T
    df.index = pd.to_datetime(df.index)

    for date, row in df.iterrows():
        rows.append({
            "stock_id": stock_id,
            "date": date,
            "year": int(date.year),
            "quarter": int((date.month - 1) // 3 + 1),

            "eps": row.get("EPS(每股盈餘)"),
            "roe": row.get("ROE(股東權益報酬率)"),
            "revenue": row.get("營收(千元)"),
            "net_income": row.get("本期淨利(合併)(千元)"),
            "operating_income": row.get("營業利益(千元)"),
            "gross_margin": row.get("毛利率(%)"),
            "operating_margin": row.get("營業利率(%)"),
            "net_margin": row.get("淨利率(%)")
        })

final_df = pd.DataFrame(rows)
print(final_df)

# === 3. 寫入 PostgreSQL ===
final_df.to_sql("financial_quarterly", engine, if_exists="append", index=False)

print("資料已成功匯入 PostgreSQL！")
