from flask import Flask, request, redirect, jsonify
import string
import random
import json
import os


app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to FastLink URL Shortener API!"

DATA_FILE = 'database.json'

# Load database if exists
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as file:
        url_mapping = json.load(file)
else:
    url_mapping = {}

# Function to generate short code
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits  # base62
    while True:
        short_code = ''.join(random.choice(characters) for _ in range(length))
        if short_code not in url_mapping:
            return short_code

# POST /shorten endpoint
@app.route('/shorten', methods=['POST'])
def shorten_url():
    long_url = request.json.get("long_url")
    custom_code = request.json.get("custom_code")

    if not long_url:
        return jsonify({"error": "long_url is required"}), 400

    # If custom code provided:
    if custom_code:
        if custom_code in url_mapping:
            return jsonify({"error": "Custom short URL already taken!"}), 400
        url_mapping[custom_code] = long_url
        short_code = custom_code
    else:
        # Check if this URL is already shortened
        for code, url in url_mapping.items():
            if url == long_url:
                return jsonify({"short_url": request.host_url + code})
        # Generate random short code
        short_code = generate_short_code()
        url_mapping[short_code] = long_url

    # Save to JSON DB
    with open(DATA_FILE, 'w') as file:
        json.dump(url_mapping, file)

    return jsonify({"short_url": request.host_url + short_code})

# GET /<short_code> endpoint
@app.route('/<short_code>')
def redirect_url(short_code):
    long_url = url_mapping.get(short_code)
    if long_url:
        return redirect(long_url)
    else:
        return "Invalid short URL", 404

if __name__ == "__main__":
    app.run(debug=True)
