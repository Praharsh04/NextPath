import json
import os
import time
import re
from datetime import datetime
from tqdm import tqdm
from postgres_data_fuction import career_choice
from utils import spinner_with_timer
from google import genai

'''
def main():
    user_id = int(input("Enter the user ID: "))
    with open(f"D:\\Adaptive_Learning_model_V2\\Backend\\Model\\users_data\\Roadmap_data\\{user_id}.json" , "r") as f:
        data = json.load(f)
    store_questionnaire_data(user_id, data)
    

'''

def generate_quetions(user_id, data, phase_idx, milestone_idx, subtopic_idx):
    
    phases = data.get("roadmap", {}).get("phases")
    if not phases:
        phases = data.get("roadmap_data", {}).get("phases", [])

    if not phases or phase_idx >= len(phases):
        return {"error": "Invalid phase index or no phases found."}

    phase = phases[phase_idx]
    milestone = phase["milestones"][milestone_idx]
    subtopic = milestone["subtopics"][subtopic_idx]

    prompt =f"""
                Generate MCQ-based questions covering all topics in the given subtopic.

                **Input Structure:**
                - phase_number: {phase["phase_number"]}
                - milestone_id: {milestone["milestone_id"]}
                - subtopic_id: {subtopic["subtopic_id"]}
                - subtopic_name: {subtopic["title"]}
                - topics: {subtopic["topic_list"]}

                **Requirements:**
                1. Cover **all topics** with MCQs
                2. **Difficulty distribution**: 50% easy, 30% medium, 20% hard
                3. **Minimum questions needed** to cover all topics (avoid overwhelming users)
                4. Each MCQ must include:
                - `question`: Clear, specific question text
                - `options`: Array of 3-5 choices
                - `answer`: Correct option (exact match from options)
                - `topic_label`: Source topic from input
                - `difficulty`: "easy", "medium", or "hard"

                **Output Format:**
                {{
                    "phase_number": {phase["phase_number"]},
                    "milestone_id": "{milestone["milestone_id"]}",
                    "subtopic_id": "{subtopic["subtopic_id"]}",
                    "subtopic_name": "{subtopic["title"]}",
                    "career_title": "{career_choice(user_id)}",
                    "created_at": "{datetime.now().isoformat()}",
                    "mcqs": [
                        {{
                            "question": "...",
                            "options": {{
                                "1": "...",
                                "2": "...",
                                "3": "...",
                                "4": "..."
                            }},
                            "answer": "1",
                            "topic_label": "...",
                            "difficulty": "easy"
                        }}
                    ]
                }}

                **Output valid JSON only. No explanations.**
            """
    try:
        client = genai.Client(api_key = os.getenv("GOOGLE_GENAI_API_KEY"))
   
        response = client.models.generate_content(model="gemini-2.5-flash-lite",contents=prompt)
        raw_json_output = response.text.replace("```json", "").replace("```", "")
        try:
            gemini_quetionaire = json.loads(raw_json_output)
            return(gemini_quetionaire)
        
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from Gemini response: {e}")
            # Print a snippet of the response around the error
            error_pos = e.pos
            context = 20
            start = max(0, error_pos - context)
            end = error_pos + context
            snippet = raw_json_output[start:end]
            print(f"...context around error...\n{snippet}\n...context around error...")
            return {"error": "Failed to parse Gemini response JSON."}
    except Exception as e:
        
        print(f"Error generating quetions with Gemini: {e}")
        return {"error": str(e)}


def store_questionnaire_data(user_id: str, roadmap_data: dict):
    Test_data_folder = "D:\\Adaptive_Learning_model_V2\\Backend\\Model\\users_data\\Test_data"
    os.makedirs(Test_data_folder, exist_ok=True)
    user_test_data_file = os.path.join(Test_data_folder, f"{user_id}_Tests.json")

    if os.path.exists(user_test_data_file):
        with open(user_test_data_file, "r") as file:
            try:
                all_questionnaires = json.load(file)
            except json.JSONDecodeError:
                all_questionnaires = []
    else:
        all_questionnaires = []

    tasks = []
    pending_subtopics = []
    phases = roadmap_data.get("roadmap", {}).get("phases")
    if not phases:
        phases = roadmap_data.get("roadmap_data", {}).get("phases", [])

    if phases:
        for phase_idx, phase in enumerate(phases):
            for milestone_idx, milestone in enumerate(phase.get("milestones", [])):
                for subtopic_idx, subtopic in enumerate(milestone.get("subtopics", [])):
                    if not any(
                        q.get("subtopic_id") == subtopic.get("subtopic_id")
                        for q in all_questionnaires
                    ):
                        tasks.append(
                            (
                                phase_idx,
                                milestone_idx,
                                subtopic_idx,
                                subtopic.get("title"),
                                subtopic.get("subtopic_id"),
                            )
                        )

    if not tasks:
        print("All questionnaires have already been generated.")
        return all_questionnaires

    print(f"\nStarting test generation for {len(tasks)} subtopics...")

    with tqdm(total=len(tasks), desc="Generating Tests") as pbar:
        for p_idx, m_idx, s_idx, title, subtopic_id in tasks:
            retry_attempts = 5
            backoff_factor = 2
            for attempt in range(retry_attempts):
                try:
                    questionnaire = generate_quetions(
                        user_id, roadmap_data, p_idx, m_idx, s_idx
                    )
                    if questionnaire and "error" not in questionnaire:
                        all_questionnaires.append(questionnaire)
                        with open(user_test_data_file, "w") as file:
                            json.dump(all_questionnaires, file, indent=4)
                        pbar.update(1)
                        print("/n")
                        print(f"Successfully generated test for subtopic: {title}")
                        break
                    else:
                        error_msg = questionnaire.get("error", "Unknown error")
                        if "503" in error_msg or "UNAVAILABLE" in error_msg:
                            print(
                                f"Gemini is overloaded. Retrying in {backoff_factor ** attempt} seconds..."
                            )
                            time.sleep(backoff_factor ** attempt)
                        else:
                            print(
                                f"\nWarning: Failed to generate questionnaire for subtopic '{title}'. Error: {error_msg}"
                            )
                            break
                except Exception as e:
                    error_str = str(e)
                    if "503" in error_str or "UNAVAILABLE" in error_str:
                        print(
                            f"Gemini is overloaded. Retrying in {backoff_factor ** attempt} seconds..."
                        )
                        time.sleep(backoff_factor ** attempt)
                    else:
                        print(
                            f"\nError generating questionnaire for subtopic '{title}': {e}"
                        )
                        break
            else:
                pending_subtopics.append(subtopic_id)
                pbar.update(1)

    if pending_subtopics:
        for subtopic_id in pending_subtopics:
            if not any(
                q.get("subtopic_id") == subtopic_id for q in all_questionnaires
            ):
                all_questionnaires.append(
                    {"subtopic_id": subtopic_id, "status": "pending"}
                )
        with open(user_test_data_file, "w") as file:
            json.dump(all_questionnaires, file, indent=4)

    if all_questionnaires:
        print(
            f"\nSuccessfully generated and stored {len(all_questionnaires)} questionnaires in {user_test_data_file}"
        )
        time.sleep(1)
        print("orgainizing test data")
        organize_tests_by_hierarchy(user_id)
    else:
        print(f"\nNo questionnaires were successfully generated for user {user_id}.")

    return all_questionnaires


def organize_tests_by_hierarchy(user_id):
    """
    Reorganizes flat test data into nested structure by phase > milestone > subtopic
    
    Args:
        tests_data: List of test objects from JSON file
        
    Returns:
        Dictionary with nested structure: {phase_number: {milestone_id: {subtopic_id: test_data}}}
    """
    with open(f"D:\\Adaptive_Learning_model_V2\\Backend\\Model\\users_data\\Test_data\\{user_id}_Tests.json", "r") as f:
        tests_data = json.load(f)
    organized = {}
    
    for test in tests_data:
        phase_num = test.get("phase_number")
        milestone_id = test.get("milestone_id")
        subtopic_id = test.get("subtopic_id")
        
        # Initialize nested structure if doesn't exist
        if phase_num not in organized:
            organized[phase_num] = {}
        
        if milestone_id not in organized[phase_num]:
            organized[phase_num][milestone_id] = {}
        
        # Store the entire test object under its subtopic
        organized[phase_num][milestone_id][subtopic_id] = test
    
    nested_tests = organized
    
    with open(f"D:\\Adaptive_Learning_model_V2\\Backend\\Model\\users_data\\Test_data\\{user_id}_Tests.json", "w") as f:
        json.dump(nested_tests, f, indent=4)
    print("Orgainized the test data")

def manually_store_questionnaire(user_id, phase_idx, milestone_idx, subtopic_idx, subtopic_title=None, questionnaire_data=None):
    """
    Manually store a questionnaire for a user.
    
    Parameters:
    - user_id (str): User ID
    - phase_idx (int): Phase number
    - milestone_idx (int): Milestone number
    - subtopic_idx (int): Subtopic index
    - subtopic_title (str, optional): Title of the subtopic
    - questionnaire_data (dict, optional): Actual questionnaire content
    """
    Test_data_folder = "D:\\Adaptive_Learning_model_V2\\Backend\\Model\\users_data\\Test_data"
    os.makedirs(Test_data_folder, exist_ok=True)
    user_test_data_file = os.path.join(Test_data_folder, f"{user_id}_Tests.json")

    # Load existing questionnaires
    if os.path.exists(user_test_data_file):
        with open(user_test_data_file, "r") as file:
            try:
                all_questionnaires = json.load(file)
            except json.JSONDecodeError:
                all_questionnaires = []
    else:
        all_questionnaires = []

    # Create manual entry
    manual_entry = {
        "subtopic_id": f"manual_{phase_idx}_{milestone_idx}_{subtopic_idx}",
        "phase_idx": phase_idx,
        "milestone_idx": milestone_idx,
        "subtopic_idx": subtopic_idx,
        "title": subtopic_title or f"Manual Entry {phase_idx}-{milestone_idx}-{subtopic_idx}",
        "questionnaire": questionnaire_data or {},
        "status": "manual"
    }

    # Check if already exists
    if any(q.get("subtopic_id") == manual_entry["subtopic_id"] for q in all_questionnaires):
        print(f"⚠️ Entry already exists for subtopic {manual_entry['subtopic_id']}. Skipping.")
    else:
        all_questionnaires.append(manual_entry)
        with open(user_test_data_file, "w") as file:
            json.dump(all_questionnaires, file, indent=4)
        print(f"✅ Successfully stored manual entry for subtopic {manual_entry['subtopic_id']}")


