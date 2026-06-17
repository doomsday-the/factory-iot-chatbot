import os
import time
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        _client = genai.Client(api_key=api_key)
    return _client

# Hardcoded strict schemas to prevent hallucination
SCHEMA_PROMPT = """
ALLOWED VIEWS:

1. welding_dashboard
Columns: business_date, shift_name, oid, machine_name, machine_type, weld_current, weld_voltage, rpm, motor_current, motor_voltage, hotspot_temperature, ambient_temperature, travel_mm, current_deviation_flag, voltage_deviation_flag, gas_deviation_flag, created_at

2. gascutting_dashboard
Columns: business_date, shift_name, machine_type, machine_name, start_tm, end_tm, duration, travel_in_mm, lpg_consumption, oxygen_metric_1, oxygen_metric_2, mm_per_min, duration_minutes

3. deviation_dashboard
Columns: hardware_id, machine_name, machine_type, operator_id, shift_id, shift_name, parameter, severity, start_tm, end_tm, duration_seconds, duration_minutes, deviation_date

4. clad_dashboard
Columns: business_date, shift_name, machine_name, machine_type, avg_weld_current, avg_weld_voltage, loss_in_kg, time_spent_minutes

5. machines
Columns: mid, name, hardware_id, des, msid, mtid, hid, orgid, mcsid, mcid, rpm_multiplication_factor, notify, deleted, created_at, updated_at
Note on mtid (it is a TEXT type, always use quotes): '1' = welding, '2' = cladding, '3' = gas cutting
"""

MODEL = "gemini-2.5-flash"

def _call_gemini(prompt: str, max_tokens: int = 1024, temperature: float = 0.0, retries: int = 3):
    client = get_client()
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            return response.text.strip()
        except Exception as e:
            error_msg = str(e)
            if ("429" in error_msg or "503" in error_msg) and attempt < retries - 1:
                time.sleep(15 * (attempt + 1))
                continue
            raise

def generate_sql(question: str) -> str:
    prompt = f"""
{SCHEMA_PROMPT}

CRITICAL RULES:
- Write ONE single PostgreSQL SELECT query for the user's question.
- You MUST ONLY query the views listed above. Do not query any other table or view (e.g. do not use 'users', 'welding').
- If asked to list all machines or any operation regarding all the machines, use the 'machines' table. Do NOT combine from other dashboards for this purpose.
- Output ONLY the raw SQL query. No explanations, no markdown formatting.

Question: {question}
"""
    sql = _call_gemini(prompt)
    
    # Extract the SELECT statement robustly
    match = re.search(r'(?i)(SELECT\s+.*)', sql, re.DOTALL)
    if match:
        sql = match.group(1)
        
    sql = sql.replace('```sql', '').replace('```', '')
    return sql.strip()

def generate_friendly_answer(question: str, sql: str, results: list) -> str:
    # Limit row count sent to LLM to prevent token explosion
    truncated = results[:100]
    result_str = str(truncated)
    if len(results) > 100:
        result_str += "\n(Showing top 100 results)"

    prompt = f"""
Given the user's question, the SQL query used, and the data results, provide a clear, business-friendly answer.
Do NOT mention the SQL query, database structure, or views in your answer. Just answer the question using the data.

Question: {question}
Data Results: {result_str}
"""
    return _call_gemini(prompt, max_tokens=500, temperature=0.3)
