import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.db import execute_query
from backend.llm import generate_sql, generate_friendly_answer

app = FastAPI(title="Factory IoT API")

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    sql: str
    friendly_answer: str

@app.post("/api/chat", response_model=QueryResponse)
def chat_endpoint(request: QueryRequest):
    try:
        # 1. Generate SQL
        sql = generate_sql(request.question)
        
        # 2. Execute SQL securely
        results = execute_query(sql)
        
        # 3. Generate Answer
        friendly_answer = generate_friendly_answer(request.question, sql, results)
        
        return QueryResponse(
            question=request.question,
            sql=sql,
            friendly_answer=friendly_answer
        )
    except ValueError as ve:
        # DB Validation Error
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # General/Connection/LLM Error
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
