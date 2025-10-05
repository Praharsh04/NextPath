"""
We are gonna make functions for,
> User teaking the test
> Analyzing the test score
> Storing the test score in a json string, under test_score_data folder in user_data
"""
import json
import os
from datetime import datetime

def load_test_questions(user_id, phase, milestone, subtopic):
    # Load test questions
    test_file = f"D:\\Adaptive_Learning_model_V2\\Backend\\Model\\users_data\\Test_data\\{user_id}_Tests.json"
    with open(test_file, "r") as f:
        data = json.load(f)
    
    # Convert phase to string if it's an integer (JSON keys are strings)
    questions = data[str(phase)][milestone][subtopic]
    return questions

def store_user_answers(user_id, phase, milestone, subtopic, mcq, user_answer, question_number):
    # Create folder if doesn't exist
    scores_folder = "D:\\Adaptive_Learning_model_V2\\Backend\\Model\\users_data\\Test_scores_data"
    os.makedirs(scores_folder, exist_ok=True)
    
    scores_file = os.path.join(scores_folder, f"{user_id}_Scores.json")
    
    # Load existing scores or create new structure
    if os.path.exists(scores_file):
        with open(scores_file, "r") as f:
            try:
                scores_data = json.load(f)
            except json.JSONDecodeError:
                scores_data = {}
    else:
        scores_data = {}
    
    # Create nested structure if doesn't exist
    phase_key = str(phase)
    if phase_key not in scores_data:
        scores_data[phase_key] = {}
    if milestone not in scores_data[phase_key]:
        scores_data[phase_key][milestone] = {}
    if subtopic not in scores_data[phase_key][milestone]:
        scores_data[phase_key][milestone][subtopic] = {
            "subtopic_name": mcq.get("subtopic_name", ""),
            "attempted_at": datetime.now().isoformat(),
            "answers": []
        }
    
    # Check if answer is correct
    correct_answer = mcq["answer"]
    is_correct = (user_answer == correct_answer)
    
    # Store answer details
    answer_record = {
        "question_number": question_number,
        "question": mcq["question"],
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "is_correct": is_correct,
        "topic_label": mcq.get("topic_label", ""),
        "difficulty": mcq.get("difficulty", ""),
        "answered_at": datetime.now().isoformat()
    }
    
    scores_data[phase_key][milestone][subtopic]["answers"].append(answer_record)
    
    # Save back to file
    with open(scores_file, "w") as f:
        json.dump(scores_data, f, indent=4)
        
    return {"is_correct": is_correct, "correct_answer": correct_answer}
