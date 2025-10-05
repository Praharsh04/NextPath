from flask import Flask, request, jsonify
from Roadmap_generator import get_or_generate_roadmap
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/generate_roadmap', methods=['POST'])
def generate_roadmap_endpoint():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    roadmap = get_or_generate_roadmap(user_id)
    if 'error' in roadmap:
        return jsonify(roadmap), 500
    
    return jsonify(roadmap), 200

@app.route('/check_roadmap/<user_id>', methods=['GET'])
def check_roadmap_endpoint(user_id):
    roadmap_file = os.path.join("D:\\Adaptive_Learning_model_V2\\Backend\\Model\\users_data\\Roadmap_data", f"{user_id}.json")
    if os.path.exists(roadmap_file):
        return jsonify({'exists': True}), 200
    else:
        return jsonify({'exists': False}), 200

@app.route('/roadmap/<user_id>', methods=['GET'])
def get_roadmap_data(user_id):
    roadmap_file = os.path.join("D:\\Adaptive_Learning_model_V2\\Backend\\Model\\users_data\\Roadmap_data", f"{user_id}.json")
    try:
        with open(roadmap_file, 'r') as f:
            roadmap_data = json.load(f)
        return jsonify(roadmap_data), 200
    except FileNotFoundError:
        return jsonify({'error': 'Roadmap not found'}), 404
    except json.JSONDecodeError:
        return jsonify({'error': 'Malformed JSON in roadmap file'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)