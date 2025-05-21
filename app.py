from flask import Flask, request, jsonify
from supabase import create_client

app = Flask(__name__)

SUPABASE_URL = 'https://okuabkqfcmjevmcjnuzq.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9rdWFia3FmY21qZXZtY2pudXpxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0Nzc4MTU5NywiZXhwIjoyMDYzMzU3NTk3fQ.2rZ3asntNX5R41czyKNs5mypgRj0dCK1eMAJC_QBEz0'  # keep it secret on Render backend
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    # Sign in with Supabase auth REST API or SDK
    # Since supabase_py doesn't have signInWithPassword, call REST API directly:
    import requests

    resp = requests.post(
        f'{SUPABASE_URL}/auth/v1/token?grant_type=password',
        headers={'apikey': SUPABASE_KEY, 'Content-Type': 'application/json'},
        json={'email': email, 'password': password}
    )
    if resp.status_code != 200:
        return jsonify({'error': 'Invalid login credentials'}), 401

    auth_data = resp.json()
    user_id = auth_data['user']['id']

    # Check activation status
    meta = supabase.table('user_meta').select('is_activated').eq('id', user_id).single().execute()

    if meta.status_code != 200 or not meta.data or not meta.data.get('is_activated'):
        return jsonify({'is_activated': False})

    return jsonify({'is_activated': True, 'user_id': user_id})
