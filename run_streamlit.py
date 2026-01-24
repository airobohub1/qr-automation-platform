import os
import subprocess

# port = os.environ.get("PORT", "8501")
port = os.environ.get("PORT", "8080")

subprocess.run([
    "streamlit",
    "run",
    "app/main.py",
    "--server.port", port,
    "--server.address", "0.0.0.0",
])
 