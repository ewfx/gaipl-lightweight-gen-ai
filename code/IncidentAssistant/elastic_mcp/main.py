# main.py
import sys
import os
from dotenv import load_dotenv

# ✅ Add 'src' to the Python path so Python can find your package
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# ✅ Import and run your server main
from elasticsearch_mcp_server.server import main

load_dotenv()  # ⬅️ Load .env variables

# Now these will work:
username = os.getenv("ELASTIC_USERNAME")
password = os.getenv("ELASTIC_PASSWORD")

if __name__ == "__main__":
    main()
