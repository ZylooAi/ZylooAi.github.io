from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client

app = Flask(__name__)

# 👇 Enable CORS for your GitHub Pages frontend
CORS(app, origins=["https://zylooai.github.io"])

# 👇 Supabase config (keep the key secret in production)
SUPABASE_URL = 'https://okuabkqfcmjevmcjnuzq.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9rdWFia3FmY21qZXZtY2pudXpxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0Nzc4MTU5NywiZXhwIjoyMDYzMzU3NTk3fQ.2rZ3asntNX5R41czyKNs5mypgRj0dCK1eMAJC_QBEz0'
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/maps-link', methods=['POST', 'OPTIONS'])
def receive_maps_link():
    # 🧼 Handle preflight CORS
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()
        link = data.get('link')

        if not link or "google.com/maps" not in link:
            return jsonify({'error': 'Invalid or missing Google Maps link'}), 400


        # Return the link back in the response too
        return jsonify({'message': 'Link received and saved successfully ✅', 'link': link})

    except Exception as e:
        return jsonify({'error': f'Exception: {str(e)}'}), 500

# Optional: add root route to make Render happy
@app.route('/')
def index():
    return "Maps Link API is running! 🗺️"

if __name__ == '__main__':
    app.run(debug=True)
