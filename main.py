from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()  

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

from fastapi import FastAPI, Body
import random, string, os
import google.generativeai as genai

app = FastAPI()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

parties = {}

def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.post("/create_party")
def create_party(name: str = Body(...), num_tables: int = Body(...), seats_per_table: int = Body(...)):
    code = generate_code()
    parties[code] = {"name": name, "num_tables": num_tables, "seats_per_table": seats_per_table, "attendees": []}
    return {"party_code": code}

@app.post("/add_attendee")
def add_attendee(code: str = Body(...), name: str = Body(...), age: int = Body(...), interests: list = Body(...)):
    if code not in parties:
        return {"error": "Invalid code"}
    parties[code]["attendees"].append({"name": name, "age": age, "interests": interests})
    return {"message": "Attendee added!"}


@app.get("/optimize_seating/{code}")
def optimize_seating(code: str):
    if code not in parties:
        return {"error": "Invalid code"}

    model = genai.GenerativeModel("gemini-1.5-flash")
    data = parties[code]
    attendees = data["attendees"]

    prompt = f"""
    You are a social seating optimizer.
    Group these attendees into tables of size {data['seats_per_table']} 
    to maximize social comfort and compatibility based on shared interests and similar ages.
    Output JSON only: {{ "tables": [ [ "name1", "name2", ... ], ... ] }}
    Attendees: {attendees}
    """
    response = model.generate_content(prompt)
    return {"optimized_seating": response.text}


import json

def save_data():
    with open("parties.json", "w") as f:
        json.dump(parties, f)

def load_data():
    global parties
    if os.path.exists("parties.json"):
        with open("parties.json") as f:
            parties = json.load(f)