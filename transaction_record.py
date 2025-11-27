import csv
import os
from tabulate import tabulate
import json
from datetime import datetime
FILENAME = "portfolio.csv"
COMPANY_FILE = "companyname.json"
TRANSACTION_FILE = "transactions.csv"


# 初始化檔案
def init_file():
    if not os.path.exists(FILENAME):
        with open(FILENAME, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
            "stock", "company", "quantity", "avg_price"])
    
    if not os.path.exists(TRANSACTION_FILE):
        with open(TRANSACTION_FILE, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "transaction_company", "quantity", "price"])
    
    
# 讀取公司對照表
def load_companies():
    if not os.path.exists(COMPANY_FILE):
        return {}
    with open(COMPANY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    
# 更新公司對照表
def save_companies(companies):
    with open(COMPANY_FILE, "w", encoding="utf-8") as f:
        json.dump(companies, f, ensure_ascii=False, indent=4)

# 新增/更新股票
def add_stock(stock,quantity, price):
    today = datetime.today()
    data = read_portfolio()
    companies = load_companies()

    # 自動抓公司名稱
    if stock in companies:
        name = companies[stock]
    else:
        # JSON 沒有，手動輸入並更新 JSON
        name = input(f"{stock} 尚未有對應公司名稱，請輸入公司名稱: ")
        companies[stock] = name
        save_companies(companies)

    if stock in data:
        name, old_qty, old_price = data[stock]
        new_qty = old_qty + quantity
        new_avg = (old_qty * old_price + quantity * price) / new_qty
        data[stock] = (name, new_qty, new_avg)
    else:
        data[stock] = (name, quantity, price)

    write_portfolio(data)
    write_transactions([[today.strftime("%Y/%m/%d"),name,quantity,price]])

# 刪除股票
def remove_stock(stock):
    data = read_portfolio()
    if stock in data:
        del data[stock]
        write_portfolio(data)
    else:
        print("沒有這檔股票")

# 讀取庫存
def read_portfolio():
    data = {}
    with open(FILENAME, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data[row["stock"]] = (row["company"],int(row["quantity"]), float(row["avg_price"]))
    return data

# 寫入庫存
def write_portfolio(data):
    with open(FILENAME, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["stock","company","quantity", "avg_price"])
        for stock, (name,qty, price) in data.items():
            writer.writerow([stock,name, qty, price])
            
# 寫入交易紀錄
def write_transactions(transactions):
    with open(TRANSACTION_FILE, mode="a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        for transaction in transactions:
            writer.writerow(transaction)

# 顯示庫存
def show_portfolio():
    data = read_portfolio()
    table = [[stock, name, qty, f"{price:.2f}"] for stock, (name, qty, price) in data.items()]
    print(tabulate(table, headers=["股票","公司","持股數量","平均成本"], tablefmt="grid"))

# 主程式
if __name__ == "__main__":
    init_file()
    while True:
        print("\n1. 新增/更新股票")
        print("2. 刪除股票")
        print("3. 顯示庫存")
        print("4. 離開")
        choice = input("選擇功能: ")
        if choice == "1":
            stock = str(input("輸入股票代號: "))
            qty = int(input("輸入數量: "))
            price = float(input("輸入買入價格: "))
            add_stock(stock, qty, price)
        elif choice == "2":
            stock = input("輸入股票代號: ")
            remove_stock(stock)
        elif choice == "3":
            show_portfolio()
        elif choice == "4":
            break
        else:
            print("選項錯誤")