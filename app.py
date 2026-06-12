# railway_api.py - Deploy this to Railway
import os
import uuid
import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Your extracted values from browser
API_URL = "https://api.miniapps.ai/chat"
TOOL_ID = "4fd31f91-f033-4b6f-9c42-ca6473658926"
MODEL_ID = "dc2db118-7888-466a-a8d1-bf9d96bab4b6"

# Your JWT token from cookie (this will expire, you'll need to refresh)
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImFlOTBhZmU1LWEyMmYtNDg4NS04ZTZlLWQ1YTk1Nzc2ODk4MCIsImVtYWlsIjoicmF5YW5nYW5nNjQ3QGdtYWlsLmNvbSIsImlhdCI6MTc4MTI4NTk3MiwiZXhwIjoxNzgyNTgxOTcyfQ.Esb16FawFiTbdMCpz5IvesE_fnUmMYwTz3NrFqHHK_A"

# CSRF token
CSRF_TOKEN = "87a53f8ce47db02b802bb695fa7f02665302aea0dffc2096ae8f31113d412a0c"

def generate_request_id():
    return str(uuid.uuid4())

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    conversation_id = data.get('conversationId', str(uuid.uuid4()))
    
    payload = {
        "toolId": TOOL_ID,
        "revision": 1,
        "modelId": MODEL_ID,
        "conversationId": conversation_id,
        "requestId": generate_request_id(),
        "elements": [
            {
                "type": "text",
                "text": user_message
            }
        ],
        "language": "en"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://miniapps.ai",
        "Referer": "https://miniapps.ai/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cookie": f"jwt={JWT_TOKEN}; __Host-miniapps.x-csrf-token={CSRF_TOKEN}; _ga=GA1.1.1787519609.1781282781; __cf_bm=lNIRGKclLLqFUuTzvcmmRXNur_XOUBixtMsxcMCFCR0-1781285957.341665-1.0.1.1-s2GIe77cD_k2KqgixTL5Rn22ebgyeqGVG8dpHSxyIrjEHGcMyq.bfuW.UoNwZQX2X6O5CE3taBGVeJ1mLTrX3w3N6uZYZWL4bgEUsyq03epe8uVxyBWhtDoRu4V9UIsQ",
        "X-CSRF-Token": CSRF_TOKEN
    }
    
    response = requests.post(
        API_URL,
        json=payload,
        headers=headers
    )
    
    # Return streaming response if it's a stream
    if response.headers.get('content-type', '').startswith('text/event-stream'):
        def generate():
            for line in response.iter_lines():
                if line:
                    yield line.decode('utf-8') + '\n'
        return Response(generate(), mimetype='text/event-stream')
    
    return jsonify(response.json())

@app.route('/new_conversation', methods=['GET'])
def new_conversation():
    """Generate a new conversation ID"""
    return jsonify({"conversationId": str(uuid.uuid4())})

@app.route('/')
def home():
    return """
    <h1>Uncensored API is running!</h1>
    <p>Send POST requests to /chat endpoint</p>
    <p>Example: curl -X POST https://your-app.railway.app/chat -H "Content-Type: application/json" -d '{"message": "Hello"}'</p>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
