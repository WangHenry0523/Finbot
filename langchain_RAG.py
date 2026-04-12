import logging
import os
from dataclasses import dataclass, field
from datetime import datetime

from dotenv import load_dotenv
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from tenacity import retry, stop_after_attempt, wait_exponential

# 建立日誌紀錄器
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# 避免危險的 SQL 關鍵字被執行(SQL Injection 防護)
DANGEROUS_KEYWORDS = {"drop", "delete", "update", "insert", "truncate", "alter"}

# ── Config ────────────────────────────────────────────────────────────────────

@dataclass
class Config:
    """ 配置類別，從環境變數讀取必要的設定 """
    google_api_key: str
    database_url: str
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0
    verbose: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        """讀取環境變數並建立 Config 實例"""
        load_dotenv()
        cfg = cls(
            google_api_key=os.getenv("GEMINI_API_KEY", ""),
            database_url=os.getenv("DATABASE_URL", ""),
        )
        cfg.validate()
        return cfg

    def validate(self):
        """驗證必要的環境變數是否存在"""
        missing = [k for k, v in {
            "GEMINI_API_KEY": self.google_api_key,
            "DATABASE_URL": self.database_url,
        }.items() if not v]
        if missing:
            raise EnvironmentError(f"Missing env vars: {', '.join(missing)}")
        
# ── Result ────────────────────────────────────────────────────────────────────

@dataclass
class QueryResult:
    """ 結果類別，封裝查詢的輸入、輸出、成功狀態和錯誤訊息 """
    query: str
    output: str = ""
    success: bool = False
    error: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)


# ── Core functions ────────────────────────────────────────────────────────────

def build_agent(config: Config, tables: list[str] | None = None):
    """建立 SQL Agent 執行器"""
    llm = ChatGoogleGenerativeAI(
        model=config.model_name,
        temperature=config.temperature,
        google_api_key=config.google_api_key,
    )
    """連接資料庫"""
    # 加上資料庫連線 timeout
    from sqlalchemy import create_engine
    engine = create_engine(
        config.database_url,
        connect_args={"connect_timeout": 10}  # 10 秒連不上就報錯
    )
    db = SQLDatabase(engine, include_tables=tables)  # 直接傳 engine 進去
    """建立 SQL Toolkit"""
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    """返回 Agent 執行器"""
    return create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        agent_type="openai-tools",
        verbose=config.verbose,
        handle_parsing_errors=True,
    )


def sanitize_query(query: str) -> str:
    """檢查查詢中是否包含危險的SQL關鍵字，清理輸入"""
    if any(kw in query.lower() for kw in DANGEROUS_KEYWORDS):
        raise ValueError("Query contains a forbidden write/DDL keyword.")
    return query.strip()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
def invoke_agent(agent, query: str) -> str:
    output = agent.invoke({"input": query})["output"]
    
    # 如果是 list（結構化回傳），提取所有 text 欄位
    if isinstance(output, list):
        return "\n".join(
            block["text"]
            for block in output
            if block.get("type") == "text" and "text" in block
        )
    
    # 如果已經是純字串，直接回傳
    return output


def run(query: str, tables: list[str] | None = None) -> QueryResult:
    result = QueryResult(query=query)
    try:
        config = Config.from_env()
        clean_query = sanitize_query(query)
        agent = build_agent(config, tables)
        result.output = invoke_agent(agent, clean_query)
        result.success = True
        logger.info("Query succeeded.")
    except Exception as exc:
        result.error = str(exc)
        logger.error("Query failed: %s", exc)
    return result

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    q = (
        "請從 financial_quarterly 表格中，"
        "找出 stock_id 是 '2330' 且 year 是 2024 quarter 是 3 的 revenue 資料。"
    )
    res = run(q, tables=["financial_quarterly"])
    print("=" * 50)
    if res.success:
        print("Success Result:\n", res.output)
    else:
        print("Error:\n", res.error)