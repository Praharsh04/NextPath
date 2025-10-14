import json
import os
import random
import numpy as np
from datetime import datetime, timedelta

# User Personas
USER_PERSONAS = {
    "U1": {"name": "High Achiever", "base_accuracy": 0.85, "motivation_factor": 1.2, "fatigue_factor": 0.01, "content_preference": "text"},
    "U2": {"name": "Struggling Learner", "base_accuracy": 0.5, "motivation_factor": 0.8, "fatigue_factor": 0.05, "content_preference": "visual"},
    "U3": {"name": "Inconsistent Learner", "base_accuracy": 0.7, "motivation_factor": 1.0, "fatigue_factor": 0.02, "fluctuation": 0.2, "content_preference": "text"},
    "U4": {"name": "Average Learner", "base_accuracy": 0.75, "motivation_factor": 1.0, "fatigue_factor": 0.02, "content_preference": "visual"},
    "U5": {"name": "Fatigued Learner", "base_accuracy": 0.8, "motivation_factor": 1.0, "fatigue_factor": 0.08, "content_preference": "text"},
    "U6": {"name": "Motivated but Slow", "base_accuracy": 0.6, "motivation_factor": 1.3, "fatigue_factor": 0.03, "content_preference": "visual"},
    "U7": {"name": "Quick but Careless", "base_accuracy": 0.9, "motivation_factor": 1.1, "fatigue_factor": 0.01, "carelessness": 0.15, "content_preference": "text"},
    "U8": {"name": "Visual Learner", "base_accuracy": 0.7, "motivation_factor": 1.0, "fatigue_factor": 0.02, "content_preference": "visual"},
    "U9": {"name": "Text-based Learner", "base_accuracy": 0.7, "motivation_factor": 1.0, "fatigue_factor": 0.02, "content_preference": "text"},
    "U10": {"name": "Comeback Kid", "base_accuracy": 0.4, "motivation_factor": 0.9, "fatigue_factor": 0.04, "improvement_rate": 0.05, "content_preference": "visual"},
}

# Subtopics with difficulty and content type
SUBTOPICS = [
    {"id": f"ST1.1.{i}", "difficulty": random.uniform(0.3, 0.9), "type": random.choice(["text", "visual"])} for i in range(1, 21)
]

def generate_synthetic_data(adaptive_logic_enabled=True):
    """Generates a deep synthetic dataset for 10 users over 20 sessions."""
    if adaptive_logic_enabled:
        output_suffix = "_adaptive"
    else:
        output_suffix = "_no_adaptive"

    output_dir = "D:\\Adaptive_Learning_model_V2\\Test\\synthetic_data"
    os.makedirs(output_dir, exist_ok=True)

    for user_id, persona in USER_PERSONAS.items():
        user_data = {
            "user_id": user_id,
            "persona": persona["name"],
            "sessions": [],
            "journey_metrics": {}
        }
        
        previous_accuracy = persona["base_accuracy"]
        base_accuracy = persona["base_accuracy"]
        motivation_factor = persona["motivation_factor"]
        engagement_levels = []
        adaptation_timestamps = []
        feedback_reactions = []

        for session_id in range(1, 21):
            subtopic = SUBTOPICS[session_id - 1]
            subtopic_id = subtopic["id"]
            difficulty_level = subtopic["difficulty"]
            content_type = subtopic["type"]

            # --- Simulate Metrics ---
            # Accuracy
            accuracy = base_accuracy
            accuracy *= motivation_factor
            accuracy -= session_id * persona["fatigue_factor"]
            if persona["content_preference"] != content_type:
                accuracy -= 0.1 # Penalty for non-preferred content
            if "fluctuation" in persona:
                accuracy += random.uniform(-persona["fluctuation"], persona["fluctuation"])
            if "carelessness" in persona:
                accuracy -= random.uniform(0, persona["carelessness"])
            if "improvement_rate" in persona:
                accuracy += session_id * persona["improvement_rate"]
            accuracy = max(0, min(1, accuracy))

            # System-driven metrics
            learning_rate = accuracy - previous_accuracy
            feedback_quality = random.uniform(0.5, 0.9) # Simulated feedback quality

            # User-driven metrics
            motivation = (motivation_factor - (session_id * 0.01) + (learning_rate * 2)) / 2
            motivation = max(0.1, min(1.5, motivation))
            engagement_level = (accuracy * motivation) - (persona["fatigue_factor"] * session_id)
            engagement_level = max(0.1, min(1.0, engagement_level))
            engagement_levels.append(engagement_level)
            cognitive_load = difficulty_level * (1 - accuracy)
            reaction_to_feedback = feedback_quality * motivation
            feedback_reactions.append(reaction_to_feedback)

            # Derived metrics
            growth_index = learning_rate
            retention_rate = previous_accuracy * random.uniform(0.8, 1.0) # Simplified retention

            # --- Adaptation ---
            adaptation = {}
            adaptations_triggered = 0
            if adaptive_logic_enabled:
                if accuracy < 0.6:
                    adaptation = {
                        "adaptive_status": "needs_review",
                        "adaptive_priority": "high",
                        "block_progression": True,
                        "add_study_time": f"{random.randint(2,4)} days",
                        "reason": f"User performance: {accuracy:.2f}% accuracy"
                    }
                    adaptations_triggered = 1
                    adaptation_timestamps.append(session_id)
                    base_accuracy += 0.1 # Improvement from adaptation
                elif accuracy > 0.85:
                    adaptation = {
                        "adaptive_status": "mastered",
                        "adaptive_priority": "low",
                        "block_progression": False,
                        "add_study_time": "0 days",
                        "reason": f"User performance: {accuracy:.2f}% accuracy"
                    }
                    adaptations_triggered = 1
                    adaptation_timestamps.append(session_id)
                    motivation_factor *= 1.05 # Confidence boost

            adaptation_efficiency = (learning_rate / adaptations_triggered) if adaptations_triggered > 0 else 0

            # --- Session Data ---
            session_data = {
                "session_id": session_id,
                "subtopic_id": subtopic_id,
                "system_metrics": {
                    "difficulty_level": difficulty_level,
                    "adaptations_triggered": adaptations_triggered,
                    "feedback_quality": feedback_quality,
                    "learning_rate": learning_rate,
                    "content_type_preference": persona["content_preference"]
                },
                "user_metrics": {
                    "score": accuracy,
                    "engagement_level": engagement_level,
                    "motivation": motivation,
                    "cognitive_load": cognitive_load,
                    "reaction_to_feedback": reaction_to_feedback
                },
                "derived_metrics": {
                    "growth_index": growth_index,
                    "retention_rate": retention_rate,
                    "adaptation_efficiency": adaptation_efficiency,
                    "stability_score": np.std([s["user_metrics"]["score"] for s in user_data["sessions"] + [{"user_metrics": {"score": accuracy}}]])
                },
                "adaptation": adaptation
            }
            user_data["sessions"].append(session_data)
            previous_accuracy = accuracy

        # --- Journey Metrics ---
        scores = [s["user_metrics"]["score"] for s in user_data["sessions"]]
        user_data["journey_metrics"] = {
            "average_performance_change": np.mean([s["derived_metrics"]["growth_index"] for s in user_data["sessions"]]),
            "engagement_consistency": np.std(engagement_levels),
            "adaptation_frequency_trend": len(adaptation_timestamps) / len(user_data["sessions"]),
            "feedback_responsiveness_over_time": np.mean(feedback_reactions)
        }

        # Save user data
        with open(os.path.join(output_dir, f"{user_id}_deep_data{output_suffix}.json"), "w") as f:
            json.dump(user_data, f, indent=4)

if __name__ == "__main__":
    # Run with adaptive logic enabled
    generate_synthetic_data(adaptive_logic_enabled=True)
    print("Deep synthetic data generation with adaptive logic complete.")
    # Run with adaptive logic disabled
    generate_synthetic_data(adaptive_logic_enabled=False)
    print("Deep synthetic data generation without adaptive logic complete.")