"""
List all available Groq models for your account
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY", "")

if not api_key:
    print("❌ GROQ_API_KEY not found in .env file")
    exit(1)

url = "https://api.groq.com/openai/v1/models"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("✅ Available Groq Models:")
        print("=" * 50)
        for model in data.get("data", []):
            model_id = model.get("id", "")
            # Filter to show only relevant models
            if any(x in model_id for x in ["llama", "mixtral", "gemma"]):
                print(f"  - {model_id}")
        print("=" * 50)
        print("\n💡 Recommended: llama-3.3-70b-versatile")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Error: {e}")



