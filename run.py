import subprocess
import sys
import time
import os

def start_services():
    print("Starting Factory IoT ChatBot Rebuild MVP...")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(os.path.dirname(__file__))
    
    print("\n[1/2] Starting FastAPI Backend...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        env=env
    )
    
    time.sleep(2)
    
    print("\n[2/2] Starting Streamlit Frontend...")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py"],
        env=env
    )
    
    print("\n✅ Services running! Backend: http://localhost:8000 | Frontend: http://localhost:8501")
    print("\nPress Ctrl+C to stop both services.\n")
    
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nStopping services...")
        backend_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    start_services()
