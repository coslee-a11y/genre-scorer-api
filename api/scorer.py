from flask import Flask, request, jsonify
from collections import Counter
import json # You'll need this for testing/local development, though Flask handles parsing

# --- YOUR GENRE LOGIC (as provided in the previous answer) ---
GENRE_HIERARCHY = {
    # ... your full genre hierarchy map ...
}

def score_genres(raw_genres_list):
    # ... your full score_genres function ...
    genre_scores = Counter()
    
    for genre_id in raw_genres_list:
        normalized_genre_id = genre_id.lower().strip()
        genre_scores[normalized_genre_id] += 1
        
        parents = GENRE_HIERARCHY.get(normalized_genre_id, [])
        for parent_id in parents:
            genre_scores[parent_id] += 1
            
    top_5_tuples = genre_scores.most_common(5)
    top_5_genres = [genre_id for genre_id, count in top_5_tuples]
    return top_5_genres
# -----------------------------------------------------------


# Vercel entry point requires an instance named 'app'
app = Flask(__name__)

# Define the API route. This endpoint will be accessible at /api/scorer
@app.route('/api/scorer', methods=['POST'])
def handle_genres():
    # 1. Get data from the POST request
    data = request.get_json()
    if not data or 'genres' not in data:
        # Return a 400 Bad Request if input is missing
        return jsonify({"error": "Missing 'genres' list in request body"}), 400

    raw_genres = data['genres']

    # 2. Process the data using your core logic
    top_genres = score_genres(raw_genres)

    # 3. Return the results as JSON
    return jsonify({
        "top_genres": top_genres,
        "count": len(top_genres)
    })

if __name__ == '__main__':
    # This block is for local testing only
    app.run(debug=True)