from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # allow all origins, so your GitHub Pages can call this API

@app.route('/api/data')
def data():
    return jsonify({"message": "Hello from Flask backend!", "status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
