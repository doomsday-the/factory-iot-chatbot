import os
import re
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    # Render provides DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)
    
    # Fallback to local
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432)),
        dbname=os.getenv("DB_NAME", "iot_dashboard"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "Arush@01")
    )

def is_safe_query(sql: str) -> bool:
    # 1. Remove comments
    clean_sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
    clean_sql = re.sub(r'/\*.*?\*/', '', clean_sql, flags=re.DOTALL)
    clean_sql = clean_sql.strip()
    
    # 2. Must start with SELECT
    if not clean_sql.lower().startswith("select"):
        return False
        
    # 3. Reject modifying keywords anywhere in the query
    forbidden = [
        r"\binsert\b", r"\bupdate\b", r"\bdelete\b", r"\bdrop\b", 
        r"\balter\b", r"\bcreate\b", r"\btruncate\b", r"\bgrant\b", r"\brevoke\b"
    ]
    for pattern in forbidden:
        if re.search(pattern, clean_sql.lower()):
            return False
            
    return True

def execute_query(sql: str):
    if not is_safe_query(sql):
        raise ValueError("Security validation failed: Only SELECT statements are allowed.")
        
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()
