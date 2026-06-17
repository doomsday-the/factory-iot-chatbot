import os
import re
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    # Supports full DATABASE_URL for Render deployment, or fallback to individual env vars
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)
    
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432)),
        dbname=os.getenv("DB_NAME", "iot_dashboard"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "Arush@01")
    )

def inspect_schemas():
    views = ["welding_dashboard", "gascutting_dashboard", "deviation_dashboard", "clad_dashboard", "machines"]
    schemas = {}
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            for view in views:
                cursor.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{view}'
                    ORDER BY ordinal_position;
                """)
                cols = cursor.fetchall()
                if cols:
                    schemas[view] = [f"{col[0]} ({col[1]})" for col in cols]
    finally:
        conn.close()
    return schemas

def is_safe_query(sql: str) -> bool:
    # Remove comments and whitespace
    clean_sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
    clean_sql = re.sub(r'/\*.*?\*/', '', clean_sql, flags=re.DOTALL)
    clean_sql = clean_sql.strip()
    
    # Must start with SELECT (case-insensitive)
    if not clean_sql.lower().startswith("select"):
        return False
        
    # Strictly reject modifications
    forbidden_patterns = [
        r"\binsert\b", r"\bupdate\b", r"\bdelete\b", r"\bdrop\b", 
        r"\balter\b", r"\bcreate\b", r"\btruncate\b"
    ]
    for pattern in forbidden_patterns:
        if re.search(pattern, clean_sql.lower()):
            return False
            
    return True

def execute_query(sql: str):
    if not is_safe_query(sql):
        raise ValueError("Security violation: Only SELECT queries are permitted.")
        
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql)
            results = cursor.fetchall()
            return results
    finally:
        conn.close()
