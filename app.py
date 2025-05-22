from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client
import os

# Groq AI import for compound-beta
from groq import Groq  # assuming the package name and usage; adjust if needed

app = Flask(__name__)
CORS(app, origins=["https://zylooai.github.io"])


# Initialize Groq AI client (using environment variable or hardcoded API key)
groq = Groq(api_key='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')

def extract_email(text):
    import re
    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return emails[0] if emails else None

@app.route('/api/maps-link', methods=['POST', 'OPTIONS'])
def receive_maps_link():
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()
        link = data.get('link')

        if not link or "google.com/maps" not in link:
            return jsonify({'error': 'Invalid or missing Google Maps link'}), 400

        # Call Groq We Search model
        # The prompt asks the AI to scrape and analyze the business page info.
        prompt = f"""
        Scrape this Google Maps business page: {link}
        Extract the following:
        1. Business name and contact email if available.
        2. Perform sentiment analysis on the reviews: count how many are good, neutral, and bad.
        3. List at least 3 commonly mentioned things about the business and count their mentions.
        Return the result in a structured JSON format.
        """

        # Use the compound-beta model to run the prompt (adjust the method if differs)
        result = groq.complete(
            model="compound-beta",
            prompt=prompt,
            max_tokens=1000,
            temperature=0.2,
        )

        # The result is expected to be JSON string, so parse it
        import json
        output_json = json.loads(result.text)

        # Extract fields safely
        business_name = output_json.get('business_name', 'Unknown Business')
        contact_email = output_json.get('contact_email', 'No email found')

        sentiment = output_json.get('review_sentiment', {})
        positive = sentiment.get('positive', 0)
        neutral = sentiment.get('neutral', 0)
        negative = sentiment.get('negative', 0)

        common_mentions = output_json.get('common_mentions', {})

        # Save to Supabase
        supabase.table('business_maps').insert({
            'link': link,
            'business_name': business_name,
            'contact_email': contact_email,
            'sentiment_positive': positive,
            'sentiment_neutral': neutral,
            'sentiment_negative': negative,
            'keywords': list(common_mentions.keys()),
            'keyword_counts': common_mentions
        }).execute()

        return jsonify({
            'message': 'Business info scraped and saved successfully ✅',
            'business': {
                'name': business_name,
                'contact_email': contact_email,
            },
            'review_sentiment': {
                'positive': positive,
                'neutral': neutral,
                'negative': negative,
            },
            'common_mentions': common_mentions,
            'link': link
        })

    except Exception as e:
        return jsonify({'error': f'Exception: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
