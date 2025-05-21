from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from anywhere

@app.route('/')
def home():
    return "Yo, Flask API is live on Render! 🚀"

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({
        "message": "Hello from Flask backend!",
        "status": "success"
    })

@app.route('/api/echo', methods=['POST'])
def echo():
    data = request.json
    return jsonify({
        "you_sent": data,
        "status": "echoed"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use Render's port if available
    app.run(host='0.0.0.0', port=port)
