from flask import Flask, request, jsonify
from collections import Counter
import json 
import ast # We need this for safe evaluation

# --- GENRE HIERARCHY & UTILITY FUNCTIONS ---

GENRE_HIERARCHY = {
    # === Electronic/Techno/House Tree ===
    "techno_rave": ["techno", "rave"],
    "hard_techno": ["techno"],
    "acid_techno": ["techno"],
    "minimal_techno": ["techno"],
    "hardcore_techno": ["techno"],
    "melodic_techno": ["techno"],
    "dub_techno": ["techno"],
    "tech_house": ["house", "techno"],
    "afro_house": ["house"],
    "melodic_house": ["house"],
    "deep_house": ["house"],
    "progressive_house": ["house"],
    "afro_tech": ["techno", "afro_house"],
    "latin_house": ["house", "latin"],
    "minimal_deep_tech": ["minimal_techno", "tech_house"],
    "groovy_house": ["house"],
    "turkish_deep_house": ["deep_house", "house"],
    "turkish_edm": ["edm"],
    "indie_electronic": ["electronic", "indie"],
    "hypertechno": ["techno"],
    "hyper_techno": ["techno"],
    "melodic_house_techno": ["house", "techno"],
    "raw_techno": ["techno"],
    "experimental_techno": ["techno"],
    "industrial_techno": ["techno", "industrial"],
    "ukrainian_electro": ["electro"],
    "uk_garage_bassline": ["house"],
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
    "laiko": ["greek"],
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
    "electrocumbia": ["latin"],
    "latin_alternative": ["latin", "alternative"],
    "nu_jazz": ["jazz"],
    "trip_hop": ["electronic", "hip_hop"],
    "downtempo": ["downtempo"],
    "indie_pop": ["pop", "indie"],
    "synth_pop": ["pop"],
    "darkwave": ["post_punk"],
    "cold_wave": ["post_punk", "darkwave"],
}


def get_related_genres(top_parent_genres):
    """
    Expands a list of core parent genres to include all relevant subgenres.
    """
    final_genre_list = set()
    
    # 1. Add the parent genres themselves
    for parent_id in top_parent_genres:
        final_genre_list.add(parent_id)

    # 2. Iterate through the hierarchy to find associated subgenres
    for subgenre_id, parent_ids in GENRE_HIERARCHY.items():
        if any(p_id in top_parent_genres for p_id in parent_ids):
            final_genre_list.add(subgenre_id)
            
    return list(final_genre_list)

def score_genres(raw_genres_list):
    """
    Calculates genre scores based on hierarchy and returns the top 5 parent genre IDs.
    """
    genre_scores = Counter()

    for genre_id in raw_genres_list:
        normalized_id = genre_id.lower().strip()
        print(genre_id)
        # 1. Score the genre itself
        genre_scores[normalized_id] += 1

        # 2. Score parent genres
        # Find all keys where this normalized_id is a parent
        for subgenre_id, parent_ids in GENRE_HIERARCHY.items():
             if normalized_id in parent_ids:
                 # This logic is inverted here for simplicity: we score the input genre, 
                 # and only count the parents if the input genre is a SUBGENRE key.
                 # The core scoring logic is based on: 'If input is X, what parent(s) does X trigger?'
                 # Since input genres are *always* counted, we only care about upstream scoring.
                 pass
        
        # If the input genre is a subgenre (a key), score its parents too
        if normalized_id in GENRE_HIERARCHY:
            for parent_id in GENRE_HIERARCHY[normalized_id]:
                genre_scores[parent_id] += 1

    # 3. Get the top 5 genres (usually the parents now dominate)
    top_5_tuples = genre_scores.most_common(5)
    return [genre_id for genre_id, count in top_5_tuples]

app = Flask(__name__)
# --- VERCEL/FLASK HANDLER (Simplified for Clean JSON Input) ---
@app.route('/api/scorer', methods=['POST'])
def handle_genres():
    # --- 1. READ RAW TEXT DATA ---
    # request.data contains the raw bytes of the request body (for any content type).
    # .decode('utf-8') converts the bytes to a Python string.

    raw_text = request.get_data(as_text=True)
    
    # Check for empty data immediately
    if not raw_text.strip():
        return jsonify({"error": "Request body is empty"}), 400

    # --- 2. PREPARE INPUT FOR SCORING ---
    raw_genres_input = raw_text.strip()
    
    # 3. CRITICAL STEP: PARSE STRING LIST INTO PYTHON LIST
    # Since MoEngage sends the list as a string (e.g., "['genre1', 'genre2']"), 
    # we must use ast.literal_eval on the text input.
    if isinstance(raw_genres_input, str):
        try:
            # Safely evaluate the string to turn it into a usable Python list
            # We assume the content is a string representation of a Python list
            raw_genres = ast.literal_eval(raw_genres_input)
        except (ValueError, SyntaxError) as e:
            # If the string is malformed or invalid Python list syntax, handle the error
            return jsonify({"error": f"Invalid genre list format in body: {e}"}), 400
    
    elif isinstance(raw_genres_input, list):
        # This path is highly unlikely if content-type is text/plain, but kept for robustness
        raw_genres = raw_genres_input
    else:
        return jsonify({"error": "Genres payload must be a string representation of a list."}), 400
    
    print(str(raw_genres))
    print(str(raw_genres_input))
    # Ensure the result is an iterable list before proceeding
    if not isinstance(raw_genres, list):
        return jsonify({"error": "Parsed content is not a list."}), 400
    
    # --- 4. EXECUTE SCORING (rest of logic remains the same) ---
    top_5_parents = score_genres(raw_genres)
    expanded_list = get_related_genres(top_5_parents)

    return jsonify({
        "top_genres": top_5_parents,
        "expanded_genres": expanded_list,
    })