from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client
import requests
import jwt

app = Flask(__name__)
CORS(app)  # Allow frontend like GitHub Pages to call this API

SUPABASE_URL = 'https://okuabkqfcmjevmcjnuzq.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9rdWFia3FmY21qZXZtY2pudXpxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0Nzc4MTU5NywiZXhwIjoyMDYzMzU3NTk3fQ.2rZ3asntNX5R41czyKNs5mypgRj0dCK1eMAJC_QBEz0'
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

    # Supabase login via REST API
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
    access_token = auth_data.get('access_token')
    if not access_token:
        return jsonify({'error': 'Login failed'}), 500

    # Decode JWT to get user ID (sub claim)
    decoded = jwt.decode(access_token, options={"verify_signature": False})
    user_id = decoded.get('sub')

    # Check activation status in user_meta table
    meta = supabase.table('user_meta').select('is_activated').eq('id', user_id).single().execute()
    is_activated = meta.data.get('is_activated') if meta.data else False

    return jsonify({
        'is_activated': is_activated,
        'user_id': user_id,
        'access_token': access_token
    })

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')

    if not full_name or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400

    # Supabase signup call (no email verification)
    resp = requests.post(
        f'{SUPABASE_URL}/auth/v1/signup',
        headers={
            'apikey': SUPABASE_KEY,
            'Content-Type': 'application/json'
        },
        json={
            'email': email,
            'password': password
        }
    )

    if resp.status_code not in [200, 201]:
        return jsonify({'error': 'Signup failed: ' + resp.text}), resp.status_code

    signup_data = resp.json()
    user = signup_data.get('user')
    if not user:
        return jsonify({'error': 'Signup failed: no user data returned'}), 500

    user_id = user.get('id')

    # Insert user_meta with is_activated=False (admin activates later)
    insert_res = supabase.table('user_meta').insert({
        'id': user_id,
        'full_name': full_name,
        'is_activated': False
    }).execute()

    if insert_res.error:
        return jsonify({'error': 'Failed to create user meta: ' + str(insert_res.error)}), 500

    return jsonify({'message': 'Signup successful! Please wait for activation.'})

if __name__ == '__main__':
    app.run(debug=True)
