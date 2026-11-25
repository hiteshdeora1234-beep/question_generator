from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def db_connection():
    return psycopg2.connect(
        host="localhost",
        user="admin",
        database="question_db",
        password="admin123",
    )

class question(BaseModel):
    topic:str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Question Generation API"}    

@app.post("/generate_question")
def gen_ques(p:question):
    conn = db_connection()
    cursor = conn.cursor()
    prompt=f"you are an expert question generator, Generate 5 questions on the topic {p.topic} write only questions without any explanation or answer, and return the questions in a single string with each question separated by a newline character."

    url="http://localhost:11434/api/generate"
    payload = {
       "model": "llama3:8b",
       "prompt": prompt,
       "stream": False
        } 
    response = requests.post(url, json=payload)
    data = response.json()
    questions_text = data.get("response", "")
    s = "INSERT INTO question(topic, data) VALUES (%s, %s)"
    values = (p.topic, questions_text)
    
    cursor.execute(s, values)
    conn.commit()
    inserted_id = cursor.lastrowid
            
    cursor.close()
    conn.close()
    return {
        "id": inserted_id,
        "topic": p.topic,
        "questions": questions_text,
    }
@app.get("/get_query")
def get_query():
    conn = db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT * FROM question")
    query = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return {"query": query}