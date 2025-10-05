import absl.logging
import os
os.environ['GRPC_VERBOSITY'] = 'ERROR'
absl.logging.set_verbosity('fatal')  # Only show fatal errors (im using this to remove all the unnecessary cli warnings)
import json
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine
from postgres_data_fuction import career_choice
from urllib.parse import quote_plus
from utils import spinner_with_timer
from google import genai
from Topicwise_Test_generator import store_questionnaire_data

def connect_to_db(host: str, port: str, dbname: str, user: str, password: str) -> Engine | None:
    """Establishes a connection to the PostgreSQL database."""
    try:
        safe_pass = quote_plus(password)
        db_uri = f"postgresql+psycopg2://{user}:{safe_pass}@{host}:{port}/{dbname}"
        engine = create_engine(db_uri)
        return engine
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def get_psychometry_data(connection: Engine, individual_id: str) -> pd.DataFrame | None:
    """Fetches psychometry data for a given individual ID from the database."""
    query = "SELECT * FROM psychometry_data WHERE ID = %s;"
    try:
        df = pd.read_sql_query(query, connection, params=(individual_id,))
        return df if not df.empty else None
    except pd.errors.DatabaseError as e:
        print(f"Database error while fetching psychometry data: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching psychometry data: {e}")
        return None



def generate_career_roadmap(career: str, psychometry_data: pd.DataFrame, user_data: dict | None) -> dict:
    """Generates a career roadmap using the Gemini API."""
    print(f"Generating roadmap for career: {career} using Gemini...")
    stop_spinner = spinner_with_timer()
    client = genai.Client(api_key = os.getenv("GOOGLE_GENAI_API_KEY"))
    prompt = f"""You are an expert career counselor and learning strategist with deep expertise in psychometric analysis, skill development, and career planning. Your role is to create highly personalized, data-driven learning roadmaps in a two-phase approach for any given career path.

**Output must be only one valid JSON object/array, no extra text, no multiple root-level objects.**

## Input Data:
**Individual's Psychometric Profile:**
{psychometry_data.to_json(orient='records', indent=2)}

**Target Career:** {career}

---

## PHASE 1: ROADMAP DATA GENERATION

Generate a comprehensive roadmap structure that covers the complete learning journey from absolute beginner to professional-ready level for the specified career. Research and include all essential skills, knowledge areas, and competencies required for success in this career field.

**IMPORTANT: Ensure the output is strictly valid JSON with no trailing commas, no syntax errors, and only return the final parseable JSON object.**

### Roadmap Requirements:

- **Timeline:** 12-24 months with quarterly phases
- **Progression:** Beginner → Intermediate → Advanced → Professional
- **Coverage:** All technical skills, soft skills, industry knowledge, and certifications relevant to the career
- **Resources:** Include ONLY verified, active, and accessible learning resources with working URLs (verify URLs are current and not deprecated)
- **Assessments:** Practical evaluation methods for each learning component
- **Topic Lists:** Comprehensive, industry-specific topics arranged in logical learning sequence

### Resource URL Requirements (CRITICAL):

1. **Verify All URLs:** Ensure every URL provided is active, accessible, and not returning 404 errors
2. **Use Reliable Sources:** Prioritize official documentation, established platforms (Coursera, Udemy, freeCodeCamp, MDN, official docs)
3. **Current Content:** Resources must reflect current industry standards and practices (published/updated within last 2-3 years)
4. **Accessible Resources:** Include both free and paid options, clearly marked
5. **URL Format:** Use complete, direct URLs (not shortened links or redirects)
6. **Backup Options:** Provide 2-3 resources per subtopic when possible
7. **Quality Over Quantity:** One verified, high-quality resource is better than multiple uncertain links

### Output Phase 1 - Complete Roadmap Data:

The JSON structure should follow this format:

{{
"roadmap_data": {{
    "career_title": "{career}",
    "total_duration": "[X] months",
    "overview": "[Comprehensive description of the complete learning journey]",
    "industry_context": "[Current market demands, trends, and opportunities in this field]",
    "phases": [
    {{
        "phase_number": 1,
        "phase_name": "[Phase Name]",
        "description": "[What this phase accomplishes]",
        "duration": "Months [X]-[Y]",
        "difficulty_level": "[Beginner/Intermediate/Advanced/Professional]",
        "learning_objectives": ["[Objective 1]", "[Objective 2]", "[Objective 3]"],
        "milestones": [
        {{
            "milestone_id": "M[X].[Y]",
            "milestone_title": "[Milestone Title]",
            "description": "[What this milestone achieves in the context of the career]",
            "duration": "[X] weeks",
            "estimated_hours": "[X]-[Y] hours total",
            "prerequisites": ["[Prerequisite 1]", "[Prerequisite 2]"],
            "subtopics": [
            {{
                "subtopic_id": "ST[X].[Y].[Z]",
                "title": "[Subtopic Title]",
                "description": "[Detailed 2-3 sentence description of what will be learned and why it matters]",
                "duration": "[X]-[Y] days",
                "learning_objectives": [
                    "[Specific skill or knowledge learner will gain]",
                    "[Measurable outcome they can achieve]",
                    "[Practical application they can perform]"
                ],
                "topic_list": [
                    "[Topic 1 - Foundational concept with clear context]",
                    "[Topic 2 - Core principle building logically on Topic 1]",
                    "[Topic 3 - Practical application with real examples]",
                    "[Topic 4 - Advanced technique or pattern]",
                    "[Topic 5 - Best practices and industry standards]"
                ],
                "learning_outcomes": ["[Outcome 1]", "[Outcome 2]", "[Outcome 3]"],
                "resources": [
                {{
                    "type": "[tutorial/video_course/documentation/interactive/practice/book/certification]",
                    "title": "[Resource Title]",
                    "url": "[Verified, working URL - ensure it's active and accessible]",
                    "provider": "[Platform/Organization name]",
                    "cost": "[Free/Paid/$X]",
                    "description": "[Description of the resource and why it's valuable for this subtopic]",
                    "estimated_time": "[Hours/Days to complete]"
                }},
                {{
                    "type": "[Resource type]",
                    "title": "[Resource Title]",
                    "url": "[Verified, working URL]",
                    "provider": "[Platform/Organization name]",
                    "cost": "[Free/Paid/$X]",
                    "description": "[Resource description]",
                    "estimated_time": "[Hours/Days to complete]"
                }}
                ],
                "hands_on_projects": [
                    "[Small project 1 - Reinforces early topics]",
                    "[Small project 2 - Applies advanced topics]"
                ],
                "assessment": {{
                "method": "[Assessment approach - quiz/project/peer-review/certification]",
                "criteria": "[Specific success criteria]",
                "deliverable": "[What needs to be produced/demonstrated]"
                }},
                "common_challenges": [
                    "[Challenge 1 learners typically face and quick solution]",
                    "[Challenge 2 and mitigation strategy]"
                ]
            }}
            ],
            "capstone_project": {{
            "title": "[Project Title]",
            "description": "[Comprehensive project description that applies milestone learning]",
            "duration": "[X]-[Y] days",
            "skills_demonstrated": ["[Skill 1]", "[Skill 2]", "[Skill 3]"],
            "deliverables": ["[Deliverable 1]", "[Deliverable 2]", "[Deliverable 3]"],
            "evaluation_criteria": ["[Criterion 1]", "[Criterion 2]"]
            }},
            "success_criteria": [
            "[Measurable criterion 1]",
            "[Measurable criterion 2]",
            "[Measurable criterion 3]"
            ]
        }}
        ]
    }}
    ]
}}
}}

### Topic List Generation Guidelines:

**Quality Checks:**
- Each topic can be learned in one focused session (1-3 hours)
- Topics follow a logical story/narrative
- No topic is a "nice to have" - all are essential
- Removing any topic would leave a gap in understanding
- Topics are specific, not vague

**Topic Count Decision Tree:**
- **5-6 topics**: Focused, specific subtopic
- **7-9 topics**: Standard subtopic with multiple concepts
- **10-12 topics**: Complex subtopic requiring depth

**Anti-Patterns to Avoid:**
- Generic topics like "Overview" or "Introduction"
- Duplicate concepts across topics
- Topics that are just vocabulary definitions
- "Advanced" topics without clear applicability
- Topics that belong in a different subtopic
- Filler topics to reach a specific count

### Important Guidelines for Topic Lists:

1. **Sequential Learning Order:** Topics must be arranged in the precise order they should be learned, with each topic building upon the previous ones
2. **Industry Specificity:** Include only topics that are directly relevant and currently used in the target career field
3. **Comprehensive Coverage:** Ensure all essential concepts, tools, frameworks, and practices for each subtopic are included
4. **Granular Detail:** Break down complex concepts into specific, learnable topics
5. **Current Relevance:** Include only up-to-date topics that reflect current industry standards (2023-2025)
6. **Logical Progression:** Follow natural learning flow: Foundation → Core Concepts → Practical Application → Best Practices → Integration
7. **Practical Focus:** Prioritize topics that have direct application in real-world career scenarios

### Topic List Research Requirements:

- Research current industry job descriptions and requirements
- Analyze skills mentioned in recent job postings for the target career
- Include topics from relevant professional certifications and training programs
- Consider emerging trends and technologies in the field (2024-2025)
- Reference academic curricula from top institutions offering related programs
- Include industry-standard tools, frameworks, and methodologies
- Account for soft skills and business knowledge specific to the career

---

## PHASE 2: PERSONALIZED ANALYSIS & RECOMMENDATIONS

Analyze the individual's psychometric profile and provide personalized recommendations that complement the roadmap data generated in Phase 1.

Analysis Framework:

1. **Personality-Career Alignment Assessment:** Evaluate compatibility between personality traits and chosen career
2. **Learning Style Analysis:** Determine optimal learning approaches based on psychological profile  
3. **Personalization & Adaptations:** Tailor the roadmap to individual strengths and challenges

Output Phase 2 - Complete Integrated Response:

The final JSON structure should be:

{{
"career_title": "{career}",
"created_at": "{datetime.now().isoformat()}",
"summary": "[Personalized summary of the learning journey for this individual]",

"psychometric_analysis": {{
    "career_alignment_score": "[X.X]/10",
    "alignment_explanation": "[Why this score was given based on personality traits]",
    "personality_strengths": ["[Strength 1 relevant to career]", "[Strength 2]", "[Strength 3]"],
    "potential_challenges": ["[Challenge 1 based on personality]", "[Challenge 2]"],
    "learning_style_profile": {{
    "primary_style": "[Dominant learning preference identified]",
    "secondary_style": "[Secondary preference]",
    "recommended_approaches": ["[Learning method 1]", "[Learning method 2]"],
    "learning_preferences": "[Visual/Auditory/Kinesthetic/Reading-Writing - based on profile]"
    }},
    "psychological_considerations": "[Key insights from psychometric data affecting learning approach]"
}},

"roadmap": {{
        "Insert complete roadmap_data structure from Phase 1 here"
}},

"personalized_recommendations": {{
    "study_schedule": {{
    "recommended_pattern": "[Optimal study timing based on personality - morning/evening/night]",
    "session_length": "[Ideal session duration - 25/45/60/90 minutes]",
    "break_frequency": "[Break patterns - Pomodoro/90-min cycles]",
    "weekly_structure": "[Suggested weekly learning schedule with specific days and hours]",
    "intensity_level": "[High intensity daily / Moderate steady / Flexible pace]"
    }},
    "resource_preferences": {{
    "primary_resources": ["[Resource types aligned with learning style - videos/text/interactive]"],
    "supplementary_resources": ["[Additional resources for reinforcement]"],
    "avoid": ["[Resource types that may not suit this individual]"]
    }},
    "motivation_strategies": [
    "[Technique 1 based on personality type - gamification/progress tracking/accountability]",
    "[Technique 2 for maintaining engagement]",
    "[Method to overcome procrastination tendencies]",
    "[Reward system aligned with personality]"
    ],
    "potential_obstacles": {{
    "identified_challenges": ["[Challenge 1 from psychometric analysis]", "[Challenge 2]"],
    "mitigation_strategies": ["[Strategy to overcome challenge 1]", "[Strategy for challenge 2]"],
    "early_warning_signs": ["[Warning sign 1]", "[Warning sign 2]"],
    "support_systems": ["[Type of support needed - community/mentor/accountability partner]"]
    }},
    "networking_advice": {{
    "personality_aligned_approaches": ["[Networking strategy suited to personality - online/in-person/one-on-one]"],
    "communities_to_join": ["[Specific communities for this career with links]"],
    "mentorship_approach": "[How this individual should find and work with mentors]",
    "social_learning": "[Group study recommendations based on personality]"
    }},
    "career_development": {{
    "job_search_timeline": "[When to start applying - after X months]",
    "portfolio_building": "[How to document learning journey]",
    "interview_preparation": "[When and how to prepare for interviews]",
    "certification_priorities": ["[Cert 1 - timing]", "[Cert 2 - timing]"]
    }},
    "alternative_paths": [
    "[Backup career option 1 if original doesn't align]",
    "[Related specialization 1]",
    "[Transition strategy if pivoting needed]"
    ]
}},

"success_metrics": {{
    "quarterly_checkpoints": {{
    "Q1": ["[Measurable goal 1 for months 1-3]", "[Goal 2]", "[Goal 3]"],
    "Q2": ["[Goal 1 for months 4-6]", "[Goal 2]", "[Goal 3]"], 
    "Q3": ["[Goal 1 for months 7-9]", "[Goal 2]", "[Goal 3]"],
    "Q4": ["[Goal 1 for months 10-12]", "[Goal 2]", "[Goal 3]"]
    }},
    "skill_assessments": {{
    "technical_evaluations": ["[Method 1 to test technical skills]", "[Method 2]"],
    "soft_skill_measures": ["[Way to assess interpersonal skills]", "[Method 2]"],
    "industry_readiness": ["[Benchmark 1 for job readiness]", "[Benchmark 2]"]
    }},
    "portfolio_requirements": {{
    "beginner_projects": ["[Project type 1]", "[Project type 2]"],
    "intermediate_projects": ["[Project type 1]", "[Project type 2]"],
    "advanced_projects": ["[Capstone project type]", "[Portfolio piece]"],
    "presentation_format": "[How to showcase work effectively for this career - GitHub/website/portfolio]",
    "minimum_projects": "[X projects needed for job applications]"
    }},
    "industry_benchmarks": {{
    "entry_level_standards": ["[What employers expect from new hires]"],
    "competitive_advantages": ["[Skills that set candidates apart]"],
    "continuous_learning": ["[Post-roadmap learning priorities]"],
    "salary_expectations": "[Entry-level salary range for this career]"
    }}
}}
}}

### Final Validation Checklist:

Before submitting the JSON response, verify:
- All URLs are tested and working (no 404 errors)
- No trailing commas in JSON arrays or objects
- All JSON syntax is valid and parseable
- Topic lists are between 5-12 items per subtopic
- Resources include provider, cost, and estimated time
- Personalization is based on actual psychometric data provided
- Timeline is realistic (12-24 months total)
- All required fields are populated with meaningful content
- No placeholder text like "[X]" remains in the final output
- Response starts with {{ and ends with }} (pure JSON, no markdown)
"""
    try:
        response = client.models.generate_content(model="gemini-2.5-flash-lite",contents=prompt)
        stop_spinner()
        # To-Do: The model is not giving the output in the desired format, so this temporary fix is applied.
        # Will be removed once the model is updated.
        raw_json_output = response.text.replace("```json", "").replace("```", "")
        try:
            gemini_roadmap = json.loads(raw_json_output)
            print("Roadmap generated successfully by Gemini.")
            return gemini_roadmap
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
        stop_spinner()
        print(f"Error generating roadmap with Gemini: {e}")
        return {"error": str(e)}

def get_or_generate_roadmap(user_id: str) -> dict:
    """Gets a roadmap from the file system or generates a new one."""
    roadmaps_folder = "D:\\Adaptive_Learning_model_V2\\Backend\\Model\\users_data\\Roadmap_data"
    os.makedirs(roadmaps_folder, exist_ok=True)
    user_roadmap_file = os.path.join(roadmaps_folder, f"{user_id}.json")
    print(f"Checking for roadmap at: {os.path.abspath(user_roadmap_file)}")
    if os.path.exists(user_roadmap_file):
        print(f"Welcome User: {user_id}")
        with open(user_roadmap_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Invalid JSON in {user_roadmap_file}, regenerating.")
    else:
        print(f"No roadmap found for user {user_id}. Generating a new one.")
    
    load_dotenv()
    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = os.environ.get("DB_PORT")
    DB_NAME = os.environ.get("DB_NAME")
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    
    db_connection = connect_to_db(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS)
    if db_connection:
        data = get_psychometry_data(db_connection, user_id)
        if data is not None:
            career = career_choice(user_id)
            if career:
                career_roadmap = generate_career_roadmap(career, data, None)
                with open(user_roadmap_file, 'w') as f:
                    json.dump(career_roadmap, f, indent=4)
                print(f"Roadmap for user {user_id} saved to {user_roadmap_file}")
                try:
                    print(f"Triggering questionnaire generation for user: {user_id}")
                    store_questionnaire_data(user_id, career_roadmap)
                    print(f"✅ Test generation completed for user_id: {user_id}")
                except Exception as q_e:
                    print(f"❌ Error generating questionnaires for user {user_id}: {q_e}")
                return career_roadmap
            else:
                return {"error": f"Career choice not found for ID: {user_id}"}
        else:
            return {"error": f"No data found for ID: {user_id}"}
    else:
        return {"error": "Database connection failed"}