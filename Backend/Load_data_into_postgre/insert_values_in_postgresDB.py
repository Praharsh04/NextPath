#!/usr/bin/env python
"""This script inserts data from a CSV file into a PostgreSQL database."""

import psycopg2
import pandas as pd
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv
import argparse

def insert_data(csv_file, db_credentials):
    """Reads data from a CSV file and inserts it into a PostgreSQL database.

    Args:
        csv_file (str): The path to the CSV file.
        db_credentials (dict): A dictionary containing the database credentials.
    """
    # ------------------------
    # 1️⃣ CSV & Column Mapping
    # ------------------------
    column_mapping = {
        "ID": "ID",
        "Age": "Age",
        "Gender": "Gender",
        "Education Level": "Education",
        "Openness": "Openness",
        "Conscientiousness": "Conscientiousness",
        "Extraversion": "Extraversion",
        "Agreeableness": "Agreeableness",
        "Neuroticism": "Neuroticism",
        "Emotional Intelligence": "Emotional",
        "Risk Tolerance": "Risk_Tolerance",
        "Stress Resilience": "Stress_Resilience",
        "Decision-Making Style": "Decision_Making_Style",
        "Motivation Type": "Motivation_Type",
        "Logical Reasoning": "Logical_Reasoning",
        "Verbal Ability": "Verbal_Ability",
        "Numerical Ability": "Numerical_Ability",
        "Creativity": "Creativity",
        "Memory/Attention Span": "Memory_Attention_span",
        "Learning Style": "Learning_style",
        "Analytical Thinking": "Analytical",
        "Communication": "Communication",
        "Leadership": "Leadership",
        "Problem-Solving": "Proble_solving",
        "Technical/Programming": "Technical_Programming",
        "Artistic/Design": "Artistic_Design",
        "Empathy & Counseling Ability": "Empathy_and_Counciling_Ability",
        "Negotiation/Persuasion": "Negotiation_Persuation",
        "Entrepreneurial Drive": "Entrepreneurial_Drive",
        "Domain-Specific Skill": "Domain_specefic_skills",
        "Interests": "Interests",
        "Preferred Work Environment": "Prefered_work_environment",
        "Values & Motivators": "Values_and_motivators",
        "Career Recommendation": "Career_Choice"
    }

    # Load CSV
    df = pd.read_csv(csv_file)
    df.rename(columns=column_mapping, inplace=True)

    # Ensure column order matches DB
    columns = list(column_mapping.values())
    df = df[columns]

    # ------------------------
    # 2️⃣ Connect to PostgreSQL
    # ------------------------
    conn = None
    try:
        conn = psycopg2.connect(**db_credentials)
        cur = conn.cursor()

        # ------------------------
        # 3️⃣ Create Table if Not Exists
        # ------------------------
        cur.execute("DROP TABLE IF EXISTS psychometry_data;")
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS psychometry_data (
            ID INT PRIMARY KEY,
            Age INT,
            Gender TEXT,
            Education TEXT,
            Openness INT,
            Conscientiousness INT,
            Extraversion INT,
            Agreeableness INT,
            Neuroticism INT,
            Emotional INT,
            Risk_Tolerance INT,
            Stress_Resilience INT,
            Decision_Making_Style TEXT,
            Motivation_Type TEXT,
            Logical_Reasoning TEXT,
            Verbal_Ability TEXT,
            Numerical_Ability TEXT,
            Creativity TEXT,
            Memory_Attention_span TEXT,
            Learning_style TEXT,
            Analytical TEXT,
            Communication TEXT,
            Leadership TEXT,
            Proble_solving TEXT,
            Technical_Programming TEXT,
            Artistic_Design TEXT,
            Empathy_and_Counciling_Ability TEXT,
            Negotiation_Persuation TEXT,
            Entrepreneurial_Drive INT,
            Domain_specefic_skills TEXT,
            Interests TEXT,
            Prefered_work_environment TEXT,
            Values_and_motivators TEXT,
            Career_Choice TEXT
        );
        """
        cur.execute(create_table_query)
        conn.commit()

        # ------------------------
        # 4️⃣ Insert CSV Rows
        # ------------------------
        
        # Convert dataframe to a list of tuples
        data_to_insert = [tuple(x) for x in df.to_numpy()]
        
        # Use execute_values for efficient insertion
        insert_query = f"INSERT INTO psychometry_data ({', '.join(columns)}) VALUES %s"
        
        execute_values(cur, insert_query, data_to_insert)
        
        conn.commit()
        
        print("CSV successfully imported into PostgreSQL!")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")

    finally:
        if conn is not None:
            cur.close()
            conn.close()

import argparse

def main():
    parser = argparse.ArgumentParser(description='Insert CSV data into PostgreSQL.')
    parser.add_argument('csv_file', type=str, help='The path to the CSV file.')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()

    load_dotenv(dotenv_path='D:/Academics/Reserch projects/Quetionaire model/.env')

    db_credentials = {
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT")
    }

    insert_data(args.csv_file, db_credentials)

if __name__ == "__main__":
    main()
