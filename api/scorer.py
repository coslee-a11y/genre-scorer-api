from flask import Flask, request, jsonify
from collections import Counter
import json # You'll need this for testing/local development, though Flask handles parsing

# --- YOUR GENRE LOGIC (as provided in the previous answer) ---
GENRE_HIERARCHY = {
    # === Electronic/Techno/House Tree ===
    "techno_rave": ["techno", "rave", "electronic"],
    "hard_techno": ["techno", "electronic"],
    "acid_techno": ["techno", "electronic"],
    "minimal_techno": ["techno", "electronic"],
    "hardcore_techno": ["techno", "electronic"],
    "melodic_techno": ["techno", "electronic"],
    "dub_techno": ["techno", "electronic"],
    "tech_house": ["house", "techno", "electronic"],
    "afro_house": ["house", "electronic"],
    "melodic_house": ["house", "electronic"],
    "deep_house": ["house", "electronic"],
    "progressive_house": ["house", "electronic"],
    "afro_tech": ["techno", "afro_house", "electronic"],
    "latin_house": ["house", "latin"],
    "minimal_deep_tech": ["minimal_techno", "tech_house"],
    "groovy_house": ["house"],
    "turkish_deep_house": ["deep_house", "house"],
    "turkish_edm": ["edm", "electronic"],
    "indie_electronic": ["electronic", "indie"],
    "hypertechno": ["techno"],
    "hyper_techno": ["techno"],
    "melodic_house_techno": ["house", "techno", "electronic"],
    "raw_techno": ["techno"],
    "experimental_techno": ["techno", "electronic"],
    "industrial_techno": ["techno", "industrial", "electronic"],
    "ukrainian_electro": ["electro", "electronic"],
    "uk_garage_bassline": ["house", "electronic"],
    "soulful_house": ["house", "soul"],
    
    # === Rap/Hip Hop/Trap Tree ===
    "greek_trap": ["trap", "hip_hop", "rap"],
    "greek_underground_rap": ["rap", "hip_hop"],
    "greek_rap": ["rap", "hip_hop"],
    "greek_hip_hop": ["hip_hop", "rap"],
    "greek_fem_rap": ["rap", "hip_hop"],
    "jazz_rap": ["jazz", "hip_hop", "rap"],
    "experimental_hip_hop": ["hip_hop", "experimental"],
    "east_coast_hip_hop": ["hip_hop", "rap"],
    "alternative_hip_hop": ["hip_hop", "alternative"],

    # === Rock/Metal/Punk Tree ===
    "thrash_metal": ["metal", "rock"],
    "black_metal": ["metal", "rock"],
    "death_metal": ["metal", "rock"],
    "doom_metal": ["metal", "rock"],
    "speed_metal": ["metal", "rock"],
    "stoner_metal": ["metal", "stoner_rock", "rock"],
    "sludge_metal": ["metal", "rock"],
    "glam_metal": ["metal", "rock"],
    "groove_metal": ["metal", "rock"],
    "melodic_death_metal": ["metal", "rock"],
    "progressive_metal": ["metal", "progressive_rock", "rock"],
    "folk_metal": ["metal", "folk", "rock"],
    "greek_metal": ["metal", "greek"],
    "stoner_rock": ["rock"],
    "psychedelic_rock": ["rock"],
    "post_rock": ["rock", "alternative"],
    "greek_psychedelic_rock": ["psychedelic_rock", "greek", "rock"],
    "greek_indie_rock": ["greek_indie", "rock"],
    "greek_shoegaze": ["shoegaze", "rock"],
    "metalcore": ["metal", "hardcore"],
    "emocore": ["hardcore", "emo"],
    "nu_metal": ["metal"],
    "classic_greek_rock": ["greek_rock", "rock"],
    "post_grunge": ["grunge", "rock"],
    "greek_punk": ["punk", "greek"],
    
    # === Greek/Folk/Other Core Genres ===
    "entehno": ["greek"],
    "lako": ["greek"],
    "classic_greek_pop": ["greek_pop", "pop", "greek"],
    "neo_kyma": ["entehno", "greek"],
    "greek_indie": ["indie", "greek"],
    "greek_swing": ["swing", "greek"],
    "greek_downtempo": ["downtempo", "greek"],
    "vocal_jazz": ["jazz", "vocal"],
    "dark_jazz": ["jazz"],
    "jazz_blues": ["jazz", "blues"],
    "blues_rock": ["blues", "rock"],
    "soul_blues": ["blues", "soul"],
    "jazz_fusion": ["jazz", "fusion"],
    "modern_blues": ["blues"],
    "cypriot_pop": ["pop", "greek"],
    "afrobeat": ["afro", "world"],
    "electrocumbia": ["latin", "electronic"],
    "latin_alternative": ["latin", "alternative"],
    "nu_jazz": ["jazz", "electronic"],
    "trip_hop": ["electronic", "hip_hop"],
    "downtempo": ["electronic"],
    "indie_pop": ["pop", "indie"],
    "synth_pop": ["pop", "electronic"],
    "darkwave": ["post_punk", "electronic"],
    "cold_wave": ["post_punk", "darkwave", "electronic"],
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