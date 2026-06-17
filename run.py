import subprocess
import sys
import time
import os

def start_services():
    print("Starting Factory IoT ChatBot Rebuild MVP...")
    
    use_tunnel = input("Do you want to expose the dashboard to the internet using Cloudflare? (y/n): ").strip().lower() == 'y'

    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(os.path.dirname(__file__))
    
    print("\n[1/3] Starting FastAPI Backend...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        env=env
    )
    
    time.sleep(2)
    
    print("\n[2/3] Starting Streamlit Frontend...")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py"],
        env=env
    )
    
    tunnel_process = None
    if use_tunnel:
        print("\n[3/3] Starting Cloudflare Tunnel...")
        tunnel_process = subprocess.Popen(
            ["cloudflared.exe", "tunnel", "--url", "http://localhost:8501"],
            env=env
        )
        print("\n✅ Services running! Backend: http://localhost:8000 | Frontend is being exposed via Cloudflare (check logs above for URL)!")
    else:
        print("\n✅ Services running! Backend: http://localhost:8000 | Frontend: http://localhost:8501")
        
    print("\nPress Ctrl+C to stop all services.\n")
    
    try:
        backend_process.wait()
        frontend_process.wait()
        if tunnel_process:
            tunnel_process.wait()
    except KeyboardInterrupt:
        print("\nStopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        if tunnel_process:
            tunnel_process.terminate()

if __name__ == "__main__":
    start_services()
