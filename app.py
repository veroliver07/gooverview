# railway_api.py - Deploy this to Railway
import os
import uuid
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Your extracted tokens - get these from the request headers
API_URL = "https://api.miniapps.ai/chat"
TOOL_ID = "4fd31f91-f033-4b6f-9c42-ca6473658926"
MODEL_ID = "dc2db118-7888-466a-a8d1-bf9d96bab4b6"

# Get these from your browser's request headers
AUTH_TOKEN = "YOUR_AUTH_TOKEN_HERE"  # Extract from Authorization header
SESSION_COOKIE = "YOUR_SESSION_COOKIE_HERE"  # Extract from Cookie header

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
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Cookie": SESSION_COOKIE,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Origin": "https://miniapps.ai",
        "Referer": "https://miniapps.ai/"
    }
    
    response = requests.post(
        API_URL,
        json=payload,
        headers=headers
    )
    
    return jsonify(response.json())

@app.route('/')
def home():
    return "Uncensored API is running!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
