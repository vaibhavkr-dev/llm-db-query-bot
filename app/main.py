from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os

# LangChain imports
from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from langchain.sql_database import SQLDatabase
from sqlalchemy import create_engine
from pymongo import MongoClient

# Environment variables for connections
SQL_URI = os.getenv("SQL_CONNECTION_STRING")
MONGO_URI = os.getenv("MONGO_CONNECTION_STRING")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="LLM DB Query Bot")

class QueryRequest(BaseModel):
    query: str
    db_type: str  # 'mongo' or 'sql'

# Connectors

def run_sql_query(query: str):
    """Execute an SQL query using SQLAlchemy engine."""
    if not SQL_URI:
        raise HTTPException(status_code=500, detail="SQL connection string not configured")
    engine = create_engine(SQL_URI)
    with engine.connect() as conn:
        result = conn.execute(query)
        rows = [dict(row) for row in result]
    return rows

def run_mongo_query(query: str):
    """Execute a MongoDB query. Expects a JSON string with db, collection and filter."""
    if not MONGO_URI:
        raise HTTPException(status_code=500, detail="Mongo connection string not configured")
    client = MongoClient(MONGO_URI)
    import json
    try:
        params = json.loads(query)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Mongo query format")
    db = client[params["db"]]
    coll = db[params["collection"]]
    filter_dict = params.get("filter", {})
    docs = list(coll.find(filter_dict))
    for doc in docs:
        # Convert ObjectId to string for JSON serialization
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
    return docs

# LangChain agent setup

def get_agent():
    """Initialize a LangChain agent that can run SQL or MongoDB queries based on the user's intent."""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)
    tools = []
    # SQL tool
    if SQL_URI:
        def sql_run(q: str) -> str:
            return str(run_sql_query(q))
        tools.append(Tool(name="sql_query", func=sql_run, description="Execute SQL queries"))
    # Mongo tool
    if MONGO_URI:
        def mongo_run(q: str) -> str:
            return str(run_mongo_query(q))
        tools.append(Tool(name="mongo_query", func=mongo_run, description="Execute MongoDB queries"))
    agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)
    return agent

@app.post("/query")
async def query_db(req: QueryRequest):
    """Endpoint to execute a query against either SQL or MongoDB based on db_type."""
    db_type = req.db_type.lower()
    if db_type == "sql":
        result = run_sql_query(req.query)
        return {"result": result}
    elif db_type == "mongo":
        result = run_mongo_query(req.query)
        return {"result": result}
    else:
        raise HTTPException(status_code=400, detail="Unsupported db_type. Use 'sql' or 'mongo'.")

@app.post("/agent")
async def query_agent(req: QueryRequest):
    """Endpoint to handle natural language queries via LangChain agent."""
    agent = get_agent()
    try:
        response = agent.run(req.query)
        return {"result": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
