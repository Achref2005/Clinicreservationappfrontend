"""
Quick test to verify Groq API is working
"""
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY", "")

if not api_key:
    print("❌ GROQ_API_KEY not found in .env file")
    print("   Please add: GROQ_API_KEY=gsk_your_key_here")
    exit(1)

print(f"✅ Found GROQ_API_KEY: {api_key[:10]}...")

try:
    client = Groq(api_key=api_key)
    print("✅ Groq client created successfully")
    
    # Test a simple completion
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Current recommended model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello"}
        ],
        temperature=0.7
    )
    
    if completion.choices:
        response = completion.choices[0].message.content
        print(f"✅ Groq API is working!")
        print(f"   Response: {response}")
    else:
        print("❌ Groq API returned no choices")
        
except Exception as e:
    print(f"❌ Error testing Groq API: {e}")
    import traceback
    traceback.print_exc()

