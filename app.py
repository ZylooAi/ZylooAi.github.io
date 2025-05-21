from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client
import requests

app = Flask(__name__)
CORS(app)  # allow frontend like GitHub Pages to hit this API

SUPABASE_URL = 'https://okuabkqfcmjevmcjnuzq.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9rdWFia3FmY21qZXZtY2pudXpxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0Nzc4MTU5NywiZXhwIjoyMDYzMzU3NTk3fQ.2rZ3asntNX5R41czyKNs5mypgRj0dCK1eMAJC_QBEz0'  # exposed for demo only
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def root():
    return jsonify({"message": "Hello from Flask backend!"})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    # Supabase login with REST API
    resp = requests.post(
        f'{SUPABASE_URL}/auth/v1/token?grant_type=password',
        headers={
            'apikey': SUPABASE_KEY,
            'Content-Type': 'application/json'
        },
        json={
            'email': email,
            'password': password
        }
    )

    if resp.status_code != 200:
        return jsonify({'error': 'Invalid login credentials'}), 401

    auth_data = resp.json()
    user = auth_data.get('user')
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user_id = user['id']

    # Check if the user is activated
    meta = supabase.table('user_meta').select('is_activated').eq('id', user_id).single().execute()

    if not meta.data or not meta.data.get('is_activated'):
        return jsonify({'is_activated': False})

    return jsonify({
        'is_activated': True,
        'user_id': user_id,
        'access_token': auth_data.get('access_token')
    })

if __name__ == '__main__':
    app.run(debug=True)
