from dotenv import load_dotenv
from pathlib import Path
import json
import os

import psycopg2


load_dotenv()

DB_CONFIG = {
    "dbname": "llm_pipeline",
    "user": "postgres",
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": "localhost",
    "port": 5432,
}


conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS json_records (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    source_file TEXT,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
""")

json_folder = Path("json_data")

for file_path in json_folder.glob("*.json"):
    print(f"Loading {file_path.name}...")

    with open(file_path, "r") as f:
        data = json.load(f)

    name = data.get("name")

    cur.execute("""
        INSERT INTO json_records (name, source_file, data)
        VALUES (%s, %s, %s)
        ON CONFLICT (name)
        DO UPDATE SET
            source_file = EXCLUDED.source_file,
            data = EXCLUDED.data,
            updated_at = NOW();
    """, (
        name,
        file_path.name,
        json.dumps(data),
    ))

    print(f"Stored {name}")

conn.commit()
cur.close()
conn.close()

print("JSON files stored successfully.")
