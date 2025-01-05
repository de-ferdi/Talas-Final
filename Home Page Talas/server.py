from flask import Flask, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Dapatkan path absolut ke file trending_topics.json
file_path = os.path.join(os.path.dirname(__file__), 'trending_topics.json')

@app.route('/trending-topics', methods=['GET'])
def get_trending_topics():
    with open(file_path, 'r') as f:
        trending_topics = json.load(f)
    return jsonify(trending_topics)

if __name__ == '__main__':
    app.run(debug=True)
