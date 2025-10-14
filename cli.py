import sys
import os
import json
import time
sys.path.append('D:\\Adaptive_Learning_model_V2\\Backend\\Model')
from Roadmap_generator import get_or_generate_roadmap
from utils import spinner_with_timer

def display_roadmap(roadmap_data):
    """Displays the roadmap in a linear format."""
    roadmap_inner = roadmap_data.get('roadmap_data', roadmap_data)
    phases = roadmap_inner.get('phases', [])

    if not phases:
        print("Invalid roadmap format: 'phases' key not found.")
        return

    print("\n--- Your Learning Roadmap ---")
    for phase in phases:
        print(f"\nPhase {phase.get('phase_number')}: {phase.get('phase_name')}")
        for milestone in phase.get('milestones', []):
            print(f"  Milestone {milestone.get('milestone_id')}: {milestone.get('milestone_title')}")
            for subtopic in milestone.get('subtopics', []):
                print(f"    Subtopic {subtopic.get('subtopic_id')}: {subtopic.get('title')}")

def display_results_table(results):
    """Displays the test results in a formatted table."""
    print("\n  You've completed the test! Here's how you did:")
    print("\n")
    print("  ┌───────────────────────┬────────────────┐")
    print(f"  │ Metric                │ Result         │")
    print("  ├───────────────────────┼────────────────┤")
    print(f"  │ Total Questions       │ {results['total_questions']:<14} │")
    print(f"  │ Correct Answers       │ {results['correct_answers']:<14} │")
    print(f"  │ Percentage Score      │ {results['percentage_score']:.2f}%          │")
    print(f"  │ Average Time/Question │ {results['avg_time_per_question']:.2f} seconds   │")
    print("  └───────────────────────┴────────────────┘")

def select_test(user_id):
    """Prompts the user to select a test to take."""
    while True:
        selection = input("\nEnter the [Phase].[Milestone].[Subtopic] ID to take a test (e.g., 1.1.1), or 'q' to quit: ")
        if selection.lower() == 'q':
            break

        try:
            phase_id, milestone_id, subtopic_id = selection.split('.')
            test_id = f"ST{phase_id}.{milestone_id}.{subtopic_id}"
            
            confirm = input(f"You have selected test {test_id}. Take this test? (yes/no): ")
            if confirm.lower() == 'yes':
                run_test(user_id, test_id)
        except ValueError:
            print("Invalid format. Please use the format [Phase].[Milestone].[Subtopic] (e.g., 1.1.1)")

def run_test(user_id, test_id):
    """Runs the selected test."""
    test_data_file = f"D:\\Adaptive_Learning_model_V2\\Backend\\Model\\users_data\\Test_data\\{user_id}_Tests.json"
    if not os.path.exists(test_data_file):
        print("Test data not found for this user.")
        return

    with open(test_data_file, "r") as f:
        all_tests = json.load(f)

    test_questions = None
    for phase in all_tests.values():
        for milestone in phase.values():
            if test_id in milestone:
                test_questions = milestone[test_id]['mcqs']
                break
        if test_questions:
            break

    if not test_questions:
        print("Test not found.")
        return

    score = 0
    total_time = 0
    weak_topics = set()

    for i, question in enumerate(test_questions):
        print(f"\nQuestion {i + 1}/{len(test_questions)}: {question['question']}")
        options = question['options']
        for key, value in options.items():
            print(f"  {key}. {value}")
        
        while True:
            start_time = time.time()
            answer = input(f"Your answer ({', '.join(options.keys())}): ")
            end_time = time.time()
            if answer in options:
                break
            else:
                print(f"Invalid input. Please enter one of the following options: {', '.join(options.keys())}")

        time_taken = end_time - start_time
        total_time += time_taken

        if answer == question['answer']:
            score += 1
        else:
            weak_topics.add(question['topic_label'])

    percentage_score = (score / len(test_questions)) * 100
    avg_time_per_question = total_time / len(test_questions)

    results = {
        'total_questions': len(test_questions),
        'correct_answers': score,
        'percentage_score': percentage_score,
        'avg_time_per_question': avg_time_per_question
    }

    display_results_table(results)

    if percentage_score < 85:
        print("\nYou scored {:.2f}%. Let's strengthen your understanding in these areas.".format(percentage_score))
        print("\nWeak Topics Identified:")
        for topic in weak_topics:
            print(f"- {topic}")
        
        review = input("\nWould you like to review the topics you missed before retaking the test? (yes/no): ")
        if review.lower() == 'yes':
            print("\n(Review functionality would be implemented here.)")
    else:
        print("\n[1m[92m🎉 SUCCESS! You scored {:.2f}% and have mastered this subject![0m".format(percentage_score))
        next_step = input("Would you like to proceed to the next topic or module? (yes/no): ")
        if next_step.lower() == 'yes':
            print("\n(Proceeding to the next topic/module...)")

def main():
    """Main function for the CLI."""
    user_id = input("Enter User ID: ")
    if not user_id:
        print("User ID cannot be empty.")
        return

    print("\nGenerating your personalized roadmap... This may take a moment.")
    stop_spinner = spinner_with_timer()
    roadmap_data = get_or_generate_roadmap(user_id)
    stop_spinner()

    if 'error' in roadmap_data:
        print(f"\nError generating roadmap: {roadmap_data['error']}")
        return

    print("\nDone!")
    display_roadmap(roadmap_data)
    select_test(user_id)

if __name__ == '__main__':
    main()