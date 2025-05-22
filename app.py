from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app, origins=["https://zylooai.github.io"])

# Your Groq API key (not safe for prod, but here you go)
GROQ_API_KEY = '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'
groq_client = Groq(api_key=GROQ_API_KEY)

@app.route('/api/maps-link', methods=['POST', 'OPTIONS'])
def receive_maps_link():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        link = data.get('link')
        
        if not link or "google.com/maps" not in link:
            return jsonify({'error': 'Invalid or missing Google Maps link'}), 400
        
        prompt = f"""
        You are a smart AI assistant. Given this Google Maps business URL:
        {link}

        Please provide the following info in JSON format:
        1. Basic business info: name, contact email (if any), phone number, address.
        2. Review sentiment analysis: number of good, neutral, bad reviews (assign numbers).
        3. Top 3 commonly mentioned keywords or topics in reviews with counts or estimates.

        Return the JSON ONLY, no explanations.
        """
        
        completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="compound-beta",
        )

        ai_response = completion.choices[0].message.content

        import json
        try:
            business_info = json.loads(ai_response)
        except json.JSONDecodeError:
            business_info = {"raw_response": ai_response}

        # No DB saving, just respond
        return jsonify({
            "message": "Link received and info scraped successfully ✅",
            "data": business_info,
            "link": link
        })

    except Exception as e:
        return jsonify({'error': f'Exception: {str(e)}'}), 500

@app.route('/')
def index():
    return "Maps Link API is running! 🗺️"

if __name__ == '__main__':
    app.run(debug=True)
