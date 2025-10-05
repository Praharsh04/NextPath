import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import urllib.parse
import os
from dotenv import load_dotenv

load_dotenv()

"""dbname = os.environ.get("POSTGRES_DB")
user = os.environ.get("POSTGRES_USER")
password = os.environ.get("POSTGRES_PASSWORD")
host = os.environ.get("POSTGRES_HOST")
port = os.environ.get("POSTGRES_PORT")
"""

dbname = "psychometry"
user = "postgres"
password = "Praharsh@2004"
host = "localhost"
port = "5432"

password_encoded = urllib.parse.quote_plus(password)

engine = create_engine(f"postgresql+psycopg2://{user}:{password_encoded}@{host}:{port}/{dbname}")

def fetch_data(individual_id):
    query = "SELECT * FROM psychometry_data WHERE ID=%s;"

    df= pd.read_sql(query, engine, params=(individual_id,))

    psychometry_json = df.to_json(orient="records", indent=2)
    return psychometry_json

def career_choice(id):
    query = "SELECT career_choice FROM psychometry_data WHERE ID=%s"

    df= pd.read_sql(query, engine, params=(id,))

    if not df.empty:
        return df['career_choice'].iloc[0]
    else:
        return None
