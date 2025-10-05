from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import subprocess
import threading

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

roadmap_generation_status = {}

# --- Helper Functions ---

def get_roadmap_path(user_id):
    return f"users_data/Roadmap_data/{user_id}.json"

def get_adaptive_roadmap_path(user_id):
    return f"users_data/Adaptive_Roadmaps_data/{user_id}_Adaptive.json"

def get_test_data_path(user_id):
    return f"users_data/Test_data/{user_id}_Tests.json"

def get_test_scores_path(user_id):
    return f"users_data/Test_scores_data/{user_id}_Scores.json"

# --- Roadmap Endpoints ---

@app.route('/api/roadmap/check/<user_id>', methods=['GET'])
def check_roadmap(user_id):
    """Check if user's roadmap exists"""
    if os.path.exists(get_adaptive_roadmap_path(user_id)) or os.path.exists(get_roadmap_path(user_id)):
        return jsonify({"exists": True, "status": "completed"})
    
    status = roadmap_generation_status.get(user_id, "not_found")
    return jsonify({"exists": False, "status": status})

def run_roadmap_generation(user_id):
    try:
        subprocess.run(["python", "Roadmap_generator.py", user_id], check=True)
        roadmap_generation_status[user_id] = "completed"
    except subprocess.CalledProcessError as e:
        roadmap_generation_status[user_id] = f"error: {e}"

@app.route('/api/roadmap/generate', methods=['POST'])
def generate_roadmap():
    """Trigger roadmap generation"""
    data = request.get_json()
    user_id = data.get("userId")
    if not user_id:
        return jsonify({"error": "userId is required"}), 400

    roadmap_generation_status[user_id] = "generating"
    thread = threading.Thread(target=run_roadmap_generation, args=(user_id,))
    thread.start()

    return jsonify({"status": "generating", "userId": user_id})

@app.route('/api/roadmap/<user_id>', methods=['GET'])
def get_roadmap(user_id):
    """Get original roadmap JSON"""
    roadmap_path = get_roadmap_path(user_id)
    if not os.path.exists(roadmap_path):
        return jsonify({"error": "Roadmap not found"}), 404
    
    with open(roadmap_path, "r") as f:
        roadmap_data = json.load(f)
    
    return jsonify(roadmap_data)

@app.route('/api/roadmap/adaptive/<user_id>', methods=['GET'])
def get_adaptive_roadmap(user_id):
    """Get adaptive roadmap if exists, otherwise original"""
    adaptive_path = get_adaptive_roadmap_path(user_id)
    if os.path.exists(adaptive_path):
        with open(adaptive_path, "r") as f:
            return jsonify(json.load(f))
    
    return get_roadmap(user_id)

# --- Test Endpoints ---

@app.route('/api/test/check/<user_id>/<topic_id>', methods=['GET'])
def check_test(user_id, topic_id):
    """Check if test exists for topic"""
    test_file = get_test_data_path(user_id)
    if not os.path.exists(test_file):
        return jsonify({"exists": False})
    
    with open(test_file, "r") as f:
        tests_data = json.load(f)
    
    # This logic needs to be adapted based on the actual structure of Test_data files
    # For now, we assume a simple check if the topic_id is a key somewhere
    def find_topic(data, topic_id):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == topic_id:
                    return True
                if find_topic(value, topic_id):
                    return True
        elif isinstance(data, list):
            for item in data:
                if find_topic(item, topic_id):
                    return True
        return False

    if find_topic(tests_data, topic_id):
        return jsonify({"exists": True, "testId": topic_id})
    else:
        return jsonify({"exists": False})

@app.route('/api/test/<user_id>/<phase>/<milestone>/<subtopic>', methods=['GET'])
def get_test(user_id, phase, milestone, subtopic):
    """Get test questions"""
    test_file = get_test_data_path(user_id)
    if not os.path.exists(test_file):
        return jsonify({"error": "Tests not found for this user"}), 404
    
    with open(test_file, "r") as f:
        tests_data = json.load(f)
        
    try:
        questions = tests_data[phase][milestone][subtopic]
        return jsonify({"questions": questions.get("mcqs", [])})
    except KeyError:
        return jsonify({"error": "Test not found for this topic"}), 404

@app.route('/api/test/submit', methods=['POST'])
def submit_test():
    """Submit test answers and trigger adaptive model"""
    data = request.get_json()
    user_id = data.get("userId")
    answers = data.get("answers")

    if not user_id or not answers:
        return jsonify({"error": "userId and answers are required"}), 400

    scores_file = get_test_scores_path(user_id)
    
    with open(scores_file, "w") as f:
        json.dump(answers, f, indent=4)
    
    # Trigger the adaptive model
    try:
        subprocess.run(["python", "Adaptive_Model.py", user_id], check=True)
        # This is a simplified response. A real implementation would calculate score and passed status.
        return jsonify({"score": 80, "passed": True, "feedback": "Great job!"})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Failed to update adaptive model: {e}"}), 500

# --- Recommendations Endpoint ---

@app.route('/api/recommendations/<user_id>', methods=['GET'])
def get_recommendations(user_id):
    """Get personalized recommendations"""
    roadmap_path = get_roadmap_path(user_id)
    if not os.path.exists(roadmap_path):
        return jsonify({"error": "Roadmap not found"}), 404
    
    with open(roadmap_path, "r") as f:
        roadmap_data = json.load(f)
    
    try:
        # This assumes a specific structure of the roadmap JSON
        recommendations = roadmap_data["roadmap"]["phases"][0]["personalized_recommendations"]
        return jsonify({"recommendations": recommendations})
    except (KeyError, IndexError):
        return jsonify({"error": "Recommendations not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)