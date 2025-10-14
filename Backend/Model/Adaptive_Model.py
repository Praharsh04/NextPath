import json
import os
from datetime import datetime

import google.generativeai as genai

# Configure Gemini API
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # Replace with your API key
genai.configure(api_key=GEMINI_API_KEY)


def log_adaptation(user_id, adaptation_details):
    """Logs adaptation changes to a JSON file."""
    try:
        log_dir = "D:\\Adaptive_Learning_model_V2\\Backend\\Model\\users_data\\Adaptations"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{user_id}_adapt.json")

        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                log_data = json.load(f)
        else:
            log_data = {"user_id": user_id, "adaptations": []}

        log_data["adaptations"].append(adaptation_details)

        with open(log_file, "w") as f:
            json.dump(log_data, f, indent=4)

    except Exception as e:
        print(f"✗ Error in logging adaptation: {e}")


def adaptive_learning_model(user_id):
    BASE_PATH = "D:\\Adaptive_Learning_model_V2\\Backend\\Model"
    SCORES_PATH = f"{BASE_PATH}\\users_data\\Test_scores_data"
    ROADMAP_PATH = f"{BASE_PATH}\\users_data\\Roadmap_data"
    
    try:
        # Load test scores
        with open(f"{SCORES_PATH}\\{user_id}_Scores.json", "r") as f:
            scores_data = json.load(f)
        
        # Load original roadmap
        roadmap_file = f"{ROADMAP_PATH}\\{user_id}.json"
        with open(roadmap_file, "r") as f:
            roadmap_data = json.load(f)
        
        print(f"✓ Loaded roadmap for user {user_id}")
        
        # Let AI analyze scores and make roadmap changes
        ai_analysis = analyze_with_ai(scores_data, roadmap_data, user_id)
        
        # Apply AI-recommended changes to specific subtopics only
        changes_made = apply_ai_changes(user_id, roadmap_data, ai_analysis)
        
        # Add metadata to track changes
        roadmap_data["adaptive_metadata"] = {
            "user_id": user_id,
            "last_updated": datetime.now().isoformat(),
            "ai_analysis_summary": ai_analysis.get("summary", {}),
            "subtopics_modified": changes_made["modified_subtopics"],
            "total_changes": changes_made["total_changes"]
        }
        
        # Save changes back to the original roadmap file
        with open(roadmap_file, "w") as f:
            json.dump(roadmap_data, f, indent=4)
        
        print(f"✓ Roadmap updated and saved to {roadmap_file}")
        print(f"✓ Modified {changes_made['total_changes']} subtopic(s)")
        
        return {
            "success": True,
            "user_id": user_id,
            "roadmap_file": roadmap_file,
            "changes_summary": changes_made,
            "ai_insights": ai_analysis
        }
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def analyze_with_ai(scores_data, roadmap_data, user_id):
    """
    Uses Gemini AI to analyze test scores and determine which specific 
    subtopics need modification
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Extract subtopics from roadmap for AI context
        subtopics_list = extract_all_subtopics(roadmap_data)
        
        # Prepare scores summary
        scores_summary = prepare_scores_summary(scores_data)
        
        prompt = f"""
You are an AI learning advisor. Analyze the student's test performance and identify which specific subtopics need changes in their learning roadmap.

**User ID:** {user_id}

**Test Performance Data:**
{scores_summary}

**Available Subtopics in Roadmap:**
{json.dumps(subtopics_list, indent=2)}

**Your Task:**
1. Identify subtopics where the student scored below 60% (weak areas)
2. Identify subtopics where the student scored above 85% (mastered areas)
3. For each weak subtopic, suggest specific changes:
   - Learning recommendations
   - Additional study time needed
   - Resources to focus on
   - Practice exercises needed
4. For mastered subtopics, suggest acceleration options

**Output Format (JSON):**
{{
  "summary": {{
    "weak_subtopics": ["subtopic1", "subtopic2"],
    "strong_subtopics": ["subtopic3"],
    "total_analyzed": number
  }},
  "subtopic_changes": [
    {{
      "subtopic_title": "exact subtopic name",
      "current_accuracy": percentage,
      "status": "needs_review" or "mastered",
      "priority": "high", "medium", or "low",
      "recommendations": ["action1", "action2", "action3"],
      "add_study_time": "X days/hours/weeks",
      "block_progression": true/false,
      "ai_notes": "specific guidance for this subtopic"
    }}
  ],
  "overall_strategy": "general learning approach for this student"
}}

Respond ONLY with valid JSON.
"""
        
        response = model.generate_content(prompt)

        
        # Parse AI response
        try:
            response_text = response.text.strip()
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                ai_analysis = json.loads(json_str)
                print("✓ AI analysis completed")
                return ai_analysis
            else:
                raise ValueError("No JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠ Could not parse AI response as JSON: {e}")
            # Fallback to manual analysis
            return fallback_analysis(scores_data, subtopics_list)
        
    except Exception as e:
        print(f"⚠ Gemini API error: {e}")
        return fallback_analysis(scores_data, extract_all_subtopics(roadmap_data))


def extract_all_subtopics(roadmap_data):
    """Extract all subtopic titles from the roadmap structure"""
    subtopics = []
    
    if isinstance(roadmap_data, dict):
        # Navigate nested structure
        if 'roadmap' in roadmap_data and isinstance(roadmap_data['roadmap'], dict):
            roadmap_inner = roadmap_data['roadmap'].get('roadmap_data', {})
        elif 'roadmap_data' in roadmap_data:
            roadmap_inner = roadmap_data['roadmap_data']
        else:
            roadmap_inner = roadmap_data
        
        phases = roadmap_inner.get('phases', [])
        
        for phase in phases:
            if isinstance(phase, dict):
                phase_name = phase.get('phase_name', 'Unknown Phase')
                milestones = phase.get('milestones', [])
                
                for milestone in milestones:
                    if isinstance(milestone, dict):
                        milestone_title = milestone.get('milestone_title', 'Unknown Milestone')
                        milestone_subtopics = milestone.get('subtopics', [])
                        
                        for subtopic in milestone_subtopics:
                            if isinstance(subtopic, dict):
                                subtopics.append({
                                    'title': subtopic.get('title', ''),
                                    'subtopic_id': subtopic.get('subtopic_id', ''),
                                    'phase': phase_name,
                                    'milestone': milestone_title,
                                    'duration': subtopic.get('duration', '')
                                })
    
    return subtopics


def prepare_scores_summary(scores_data):
    """Prepare a concise summary of test scores"""
    summary = []
    tests = scores_data.get("tests", []) if isinstance(scores_data, dict) else []
    
    subtopic_performance = {}
    
    for test in tests:
        if not isinstance(test, dict):
            continue
        
        questions = test.get("questions", [])
        
        for question in questions:
            if not isinstance(question, dict):
                continue
            
            subtopic = question.get("subtopic", "Unknown")
            is_correct = question.get("correct", False)
            
            if subtopic not in subtopic_performance:
                subtopic_performance[subtopic] = {"correct": 0, "total": 0}
            
            subtopic_performance[subtopic]["total"] += 1
            if is_correct:
                subtopic_performance[subtopic]["correct"] += 1
    
    for subtopic, stats in subtopic_performance.items():
        accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        summary.append(f"- {subtopic}: {accuracy:.1f}% ({stats['correct']}/{stats['total']} correct)")
    
    return "\n".join(summary) if summary else "No test data available"


def fallback_analysis(scores_data, subtopics_list):
    """Manual analysis when AI fails"""
    subtopic_changes = []
    weak_subtopics = []
    strong_subtopics = []
    
    tests = scores_data.get("tests", []) if isinstance(scores_data, dict) else []
    subtopic_stats = {}
    
    for test in tests:
        if not isinstance(test, dict):
            continue
        
        for question in test.get("questions", []):
            if not isinstance(question, dict):
                continue
            
            subtopic = question.get("subtopic", "Unknown")
            is_correct = question.get("correct", False)
            
            if subtopic not in subtopic_stats:
                subtopic_stats[subtopic] = {"correct": 0, "total": 0}
            
            subtopic_stats[subtopic]["total"] += 1
            if is_correct:
                subtopic_stats[subtopic]["correct"] += 1
    
    for subtopic, stats in subtopic_stats.items():
        if stats["total"] > 0:
            accuracy = stats["correct"] / stats["total"]
            
            if accuracy < 0.60:
                weak_subtopics.append(subtopic)
                subtopic_changes.append({
                    "subtopic_title": subtopic,
                    "current_accuracy": round(accuracy * 100, 2),
                    "status": "needs_review",
                    "priority": "high",
                    "recommendations": [
                        "Review fundamental concepts",
                        "Complete additional practice exercises",
                        "Take focused quiz on this subtopic"
                    ],
                    "add_study_time": "3 days",
                    "block_progression": True,
                    "ai_notes": "Focus on mastering basics before moving forward"
                })
            elif accuracy > 0.85:
                strong_subtopics.append(subtopic)
                subtopic_changes.append({
                    "subtopic_title": subtopic,
                    "current_accuracy": round(accuracy * 100, 2),
                    "status": "mastered",
                    "priority": "low",
                    "recommendations": [
                        "Proceed to advanced topics",
                        "Explore real-world applications"
                    ],
                    "add_study_time": "0 days",
                    "block_progression": False,
                    "ai_notes": "Great work! Continue to next topics"
                })
    
    return {
        "summary": {
            "weak_subtopics": weak_subtopics,
            "strong_subtopics": strong_subtopics,
            "total_analyzed": len(subtopic_stats)
        },
        "subtopic_changes": subtopic_changes,
        "overall_strategy": "Focus on weak areas while maintaining progress in strong areas"
    }


def apply_ai_changes(user_id, roadmap_data, ai_analysis):
    """
    Apply AI-recommended changes to specific subtopics in the roadmap
    Returns a summary of changes made
    """
    changes_made = {
        "modified_subtopics": [],
        "total_changes": 0
    }
    
    subtopic_changes = ai_analysis.get("subtopic_changes", [])
    
    # Navigate to phases
    if isinstance(roadmap_data, dict):
        if 'roadmap' in roadmap_data and isinstance(roadmap_data['roadmap'], dict):
            roadmap_inner = roadmap_data['roadmap'].get('roadmap_data', {})
        elif 'roadmap_data' in roadmap_data:
            roadmap_inner = roadmap_data['roadmap_data']
        else:
            roadmap_inner = roadmap_data
        
        phases = roadmap_inner.get('phases', [])
        
        # Create lookup for changes by subtopic title
        changes_by_title = {change["subtopic_title"]: change for change in subtopic_changes}
        
        for phase in phases:
            if not isinstance(phase, dict):
                continue
            
            for milestone in phase.get('milestones', []):
                if not isinstance(milestone, dict):
                    continue
                
                for subtopic in milestone.get('subtopics', []):
                    if not isinstance(subtopic, dict):
                        continue
                    
                    subtopic_title = subtopic.get('title', '')
                    
                    # Check if this subtopic needs changes
                    if subtopic_title in changes_by_title:
                        change = changes_by_title[subtopic_title]
                        
                        # Apply changes to this specific subtopic
                        subtopic['adaptive_status'] = change.get('status', 'needs_review')
                        subtopic['adaptive_priority'] = change.get('priority', 'medium')
                        subtopic['performance_accuracy'] = change.get('current_accuracy', 0)
                        subtopic['ai_recommendations'] = change.get('recommendations', [])
                        subtopic['ai_notes'] = change.get('ai_notes', '')
                        subtopic['block_progression'] = change.get('block_progression', False)
                        
                        # Adjust duration if needed
                        add_time = change.get('add_study_time', '0 days')
                        if add_time != '0 days':
                            original_duration = subtopic.get('duration', '')
                            subtopic['original_duration'] = original_duration
                            subtopic['adjusted_duration'] = f"{original_duration} + {add_time}"
                        
                        changes_made["modified_subtopics"].append(subtopic_title)
                        changes_made["total_changes"] += 1
                        
                        # Log the adaptation
                        adaptation_details = {
                            "timestamp": datetime.now().isoformat(),
                            "adaptation_type": "difficulty_adjustment",
                            "affected_section": subtopic_title,
                            "change_description": f"Status changed to {change.get('status')}, priority to {change.get('priority')}",
                            "reason": f"User performance: {change.get('current_accuracy')}% accuracy"
                        }
                        log_adaptation(user_id, adaptation_details)
                        
                        print(f"  ✓ Modified: {subtopic_title} → {change.get('status')}")
    
    return changes_made


# Example usage
if __name__ == "__main__":
    user_id = input("Enter The User ID: ")
    result = adaptive_learning_model(user_id)
    
    if result["success"]:
        print("\n" + "="*60)
        print("AI-POWERED ADAPTIVE LEARNING SYSTEM")
        print("="*60)
        print(f"User ID: {result['user_id']}")
        print(f"\n📁 Files:")
        print(f"  Original: {result['original_file']} (UNCHANGED)")
        print(f"  Adaptive: {result['adaptive_file']} (NEW)")
        
        print(f"\n📊 Changes Made:")
        print(f"  Total subtopics modified: {result['changes_summary']['total_changes']}")
        
        if result['changes_summary']['modified_subtopics']:
            print(f"\n  Modified subtopics:")
            for subtopic in result['changes_summary']['modified_subtopics']:
                print(f"    • {subtopic}")
        
        ai_summary = result['ai_insights'].get('summary', {})
        print(f"\n🤖 AI Analysis Summary:")
        print(f"  Weak areas: {len(ai_summary.get('weak_subtopics', []))}")
        print(f"  Strong areas: {len(ai_summary.get('strong_subtopics', []))}")
        print(f"  Strategy: {result['ai_insights'].get('overall_strategy', 'N/A')[:100]}...")
        
        print(f"\n✓ Process completed successfully!")
    else:
        print(f"\n✗ Failed: {result['error']}")
