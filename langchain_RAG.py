from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_ollama import ChatOllama
import os
from dotenv import load_dotenv

load_dotenv()

# Step 1: 設定 LLM
# 確保 Ollama 服務和 llama3.1:8b 模型正在運行
llm = ChatOllama(model="llama3.1:8b", temperature=0)

# Step 2: 連接 PostgreSQL
# 格式: postgresql+psycopg2://username:password@host:port/database
db_url = os.getenv("database_url")

try:
    db = SQLDatabase.from_uri(db_url,include_tables=['financial_quarterly'])
except Exception as e:
    print(f"Error connecting to database: {e}")
    print("Please check if your PostgreSQL service is running and URI is correct.")
    exit()

# Step 3: 建立 SQL Toolkit
# 將資料庫連接和 LLM 傳遞給工具箱
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Step 4: 建立 SQL Agent 執行器
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    agent_type="zero-shot-react-description",
    verbose=True,  # 開啟詳細模式，觀察 LLM 的思考和 SQL 語句
    handle_parsing_errors=True
)

# Step 5: 測試問句 (專注於數據庫中的結構化查詢)
# 這裡假設您的資料庫中，台積電的 stock_id 為 '2330'
query = "請從 financial_quarterly 表格中，找出 stock_id 是 '2330' 且 year 是 2024 quarter 是 3 的 revenue 資料。"

print(f"Executing Agent Query: {query}")
print("-" * 50)

# 使用新的 invoke 方法來啟動 Agent 執行器
# Agent 的 invoke 需要一個字典作為輸入
try:
    result = agent_executor.invoke({"input": query})
    
    print("-" * 50)
    print("Agent Final Result:")
    # AgentExecutor 的 invoke 返回一個包含 'output' 鍵的字典
    print(result['output']) 

except Exception as e:
    print(f"\n--- Agent Execution Failed ---")
    print(f"Error during agent run: {e}")
    print("This often means the LLM generated a syntactically incorrect SQL query.")