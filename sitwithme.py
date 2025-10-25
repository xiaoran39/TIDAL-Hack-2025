import os
import json
import re
import random
import string
import streamlit as st
from google.genai import Client

# -------------------
# Gemini client setup
# -------------------


client = Client(api_key="AIzaSyDIHWpyBgJvR7iN3ywo4ah_VnyQFIwIn2I")

APP_TITLE = "🎉 SitWithMe – Smart Party Planner"

# -------------------
# Initialize session state
# -------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "parties" not in st.session_state:
    st.session_state.parties = {}

# -------------------
# UI: Header + Navigation
# -------------------
st.title(APP_TITLE)

col1, col2 = st.columns(2)
with col1:
    if st.button("🎈 Organize Your Party"):
        st.session_state.page = "host"
with col2:
    if st.button("🪩 Join a Party"):
        st.session_state.page = "join"

with st.sidebar:
    if st.button("🪑 View Seating"):
        st.session_state.page = "results"

# -------------------
# Helpers
# -------------------
def parse_json_lenient(s: str):
    """Extract valid JSON from model text, even if wrapped in code fences."""
    try:
        return json.loads(s)
    except Exception:
        pass
    m = re.search(r"```(?:json)?\s*($begin:math:display$[\\s\\S]*$end:math:display$|\{[\s\S]*\})\s*```", s)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    i, j = s.find("{"), s.rfind("}")
    if i != -1 and j != -1:
        try:
            return json.loads(s[i:j+1])
        except Exception:
            pass
    raise ValueError("Could not parse JSON from model output.")

def generate_ai_interests(event_desc: str):
    """Ask Gemini to extract 5–10 relevant interests based on the event description."""
    try:
        prompt = f"""
        You are a smart event assistant.
        Given the following event description, extract 5–10 interests people at this event would likely have.
        Return ONLY a JSON list of strings (no explanations, no markdown).

        Example output:
        ["Food", "Travel", "Tech", "Music", "Networking"]

        Event description:
        "{event_desc}"
        """
        resp = client.models.generate_content(model="gemini-2.0-flash", contents=[prompt])
        text = getattr(resp, "text", "") or getattr(resp, "output_text", "")
        m = re.search(r"\[.*\]", text, re.S)
        if m:
            return json.loads(m.group(0))
    except Exception as e:
        st.warning(f"⚠️ Could not auto-generate interests: {e}")
    return ["Music", "Food", "Travel", "Tech", "Movies", "Art"]

def gen_seating_json(party):
    """Generate a JSON seating plan based on guests."""
    prompt = f"""
    You are an expert event planner AI.

    Assign guests into {party['tables']} tables, each with {party['seats_per_table']} seats.

    Guests (list of dicts with name, age, interests):
    {party['guests']}

    Rules:
    - Group guests with overlapping interests and similar ages (±5 years).
    - Balance table sizes and don't exceed capacity.
    - If fewer guests than seats, leave empty seats.
    - Reply with valid JSON only.

    JSON format:
    {{
      "tables": [
        {{
          "table_number": 1,
          "guests": [
            {{"name": "Alice", "age": 25, "interests": ["Music","Art"]}},
            {{"name": "Bob", "age": 27, "interests": ["Food","Movies"]}}
          ]
        }}
      ]
    }}
    """
    resp = client.models.generate_content(model="gemini-2.0-flash", contents=[prompt])
    text_out = getattr(resp, "text", None) or getattr(resp, "output_text", None)
    if not text_out:
        raise RuntimeError("Empty response from Gemini.")
    return parse_json_lenient(text_out.strip())

# -------------------
# PAGE LOGIC
# -------------------

# HOME
if st.session_state.page == "home":
    st.write("Welcome to SitWithMe! Create or join a party to get started 🎉")

# HOST PAGE
elif st.session_state.page == "host":
    st.subheader("🎉 Create Your Party")

    event_desc = st.text_area(
        "Describe your event",
        placeholder="e.g. A rooftop dinner for startup founders who love tech, wine, and good food."
    )
    num_tables = st.number_input("Number of Tables", min_value=1, max_value=20, step=1)
    seats_per_table = st.number_input("Seats Per Table", min_value=1, max_value=20, step=1)

    if st.button("Create Party"):
        party_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        ai_interests = generate_ai_interests(event_desc) if event_desc else ["Music", "Food", "Tech"]

        st.session_state.parties[party_code] = {
            "tables": num_tables,
            "seats_per_table": seats_per_table,
            "event_desc": event_desc,
            "ai_interests": ai_interests,
            "guests": [],
            "seating_result": None
        }

        st.success(f"✅ Party created! Share this code with your guests: **{party_code}**")
        st.markdown("**🎯 AI-Suggested Interests:**")
        st.write(", ".join(ai_interests))

# JOIN PAGE
elif st.session_state.page == "join":
    st.subheader("🪩 Join a Party")
    code = st.text_input("Enter Party Code").upper()
    name = st.text_input("Your Name")
    age = st.number_input("Age", min_value=1, max_value=120, step=1)

    # Use AI-generated interests from host’s party if available
    available_interests = ["Sports", "Music", "Movies", "Travel", "Food", "Tech", "Art", "Books"]
    if code in st.session_state.parties and st.session_state.parties[code].get("ai_interests"):
        available_interests = st.session_state.parties[code]["ai_interests"]

    interests = st.multiselect("Select your interests", available_interests)

    if st.button("Join Party"):
        if code not in st.session_state.parties:
            st.error("❌ Invalid party code!")
        elif not name or not age or not interests:
            st.error("⚠️ Please fill in all fields and select at least one interest.")
        else:
            st.session_state.parties[code]["guests"].append(
                {"name": name, "age": age, "interests": interests}
            )
            st.success(f"🎊 {name} joined party {code}!")

# RESULTS PAGE
elif st.session_state.page == "results":
    st.subheader("🪑 Seating Arrangement")
    code = st.text_input("Enter Party Code").upper()

    if st.button("Organize Seating"):
        if code not in st.session_state.parties:
            st.error("❌ Invalid party code!")
        else:
            party = st.session_state.parties[code]
            if not party["guests"]:
                st.warning("⚠️ No guests have joined yet. Share the party code first.")
            else:
                try:
                    seating = gen_seating_json(party)

                    st.markdown("### ✨ AI-Generated Seating Plan")
                    st.caption("Optimized for social connection and compatibility")

                    tables_data = seating.get("tables", [])
                    cols_per_row = 3
                    for i in range(0, len(tables_data), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for j, table in enumerate(tables_data[i:i+cols_per_row]):
                            with cols[j]:
                                tnum = table.get("table_number", i + j + 1)
                                assigned = table.get("guests", [])
                                st.markdown(
                                    f"#### 🪑 Table {tnum} "
                                    f"({len(assigned)}/{party['seats_per_table']} seats)"
                                )
                                for g in assigned:
                                    name = g.get("name", "Unknown")
                                    age = g.get("age", "—")
                                    interests = ", ".join(g.get("interests", []))
                                    st.markdown(f"**{name}**, {age} yrs  \n🧩 *{interests}*")
                                for _ in range(max(0, party["seats_per_table"] - len(assigned))):
                                    st.markdown("▫️ _Empty seat_")

                    st.session_state.parties[code]["seating_result"] = json.dumps(seating)

                except Exception as e:
                    st.error(f"🚨 Error generating seating plan: {e}")