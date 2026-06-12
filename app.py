import os
import sys
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Health check endpoint - MUST respond quickly
@app.route('/health')
@app.route('/')
def health_check():
    return jsonify({
        "status": "alive",
        "message": "Google AI Overview API is running",
        "version": "2.0"
    })

# Main API endpoint
@app.route('/ai-overview', methods=['GET'])
def get_ai_overview():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Please provide a query parameter 'q'"}), 400
    
    try:
        # Import here to avoid slow startup
        from scraper import get_google_ai_overview
        
        result = get_google_ai_overview(query)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "query": query,
            "success": False
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
