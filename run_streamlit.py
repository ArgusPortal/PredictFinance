"""
Script para executar a aplicação Streamlit
"""
import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app_streamlit.py", "--server.port=8501"])
