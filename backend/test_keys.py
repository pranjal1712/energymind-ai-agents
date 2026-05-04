import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_groq_keys():
    keys = os.getenv("GROQ_API_KEYS", os.getenv("GROQ_API_KEY", "")).split(",")
    keys = [k.strip() for k in keys if k.strip()]
    
    print(f"\n--- Testing {len(keys)} Groq Keys ---")
    model = "llama-3.3-70b-versatile" # Updated model
    
    for i, key in enumerate(keys):
        print(f"Key {i+1} (...{key[-6:]}): ", end="", flush=True)
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 5
        }
        try:
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                print("WORKING")
            else:
                print(f"FAILED (Status: {response.status_code}, Error: {response.text})")
        except Exception as e:
            print(f"ERROR: {str(e)}")

def test_tavily_key():
    key = os.getenv("TAVILY_API_KEY")
    print(f"\n--- Testing Tavily Key (...{key[-6:]}) ---")
    if not key:
        print("❌ NO KEY FOUND")
        return
        
    data = {
        "api_key": key,
        "query": "test",
        "max_results": 1
    }
    try:
        response = requests.post("https://api.tavily.com/search", json=data, timeout=10)
        if response.status_code == 200:
            print("WORKING")
        else:
            print(f"FAILED (Status: {response.status_code}, Error: {response.text})")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    test_groq_keys()
    test_tavily_key()
