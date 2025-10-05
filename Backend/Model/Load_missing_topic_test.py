
from Topicwise_Test_generator import  manually_store_questionnaire

def main():

    user_id = input("Enter User ID: ")
    phase_idx = input("Enter phase Number: ")
    milestone_idx = input("Enter milestone idx: ")
    subtopic_idx = input("Enter subtopic idx: ")
    with open (f"Backend\\Model\\users_data\\Roadmap_data\\{user_id}.json" , "r") as f:
        data = f.read()
    subtopic_title = data["roadmap"]["phases"][phase_idx]["milestones"][milestone_idx]["subtopics"][subtopic_idx]["title"]
    questionnaire_data = data

    manually_store_questionnaire(user_id, phase_idx, milestone_idx, subtopic_idx, subtopic_title, questionnaire_data)

main()