import streamlit as st

# --------- FRONT PAGE ---------
st.title("Welcome to the Party App 🎉")
st.write("Choose an option below:")

# Create two buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("Organize a Party!"):
        st.session_state.page = "host"

with col2:
    if st.button("Join a Party!"):
        st.session_state.page = "join"

# Initialize session state page if not set
if "page" not in st.session_state:
    st.session_state.page = "home"

# --------- PAGE LOGIC ---------
if st.session_state.page == "home":
    st.write("Use the buttons above to navigate.")
elif st.session_state.page == "join":
    st.subheader("Join Party Form")
    code = st.text_input("Party Code")
    name = st.text_input("Your Name")
    age = st.number_input("Age", min_value=1, max_value=120)
    interests = st.multiselect(
        "Select your interests",
        ["Sports", "Music", "Movies", "Travel", "Food", "Tech", "Art", "Books", ""]
    )
    if st.button("Submit"):
        if not code or not name or not age or not interests:
            st.error("Please fill in all fields and select at least one interest.")
        else:
            st.success(f"{name} joined the party with code {code}!")

elif st.session_state.page == "results":
    st.subheader("Results / Attendees")
    st.write("This page could show party attendees or other results.")
    st.table([
        {"Name": "Alice", "Age": 25, "Interests": "Music, Travel"},
        {"Name": "Bob", "Age": 30, "Interests": "Sports, Tech"},
    ])

# Title and description
# st.title("SmartSeat")
# st.write("Welcome! Fill out the form below:")
#
# # User inputs
# name = st.text_input("Your Name")
# age = st.number_input("Your Age", min_value=1, max_value=120)
# interests = st.multiselect("Select your interests",
#                            ["Sports","Music","Movies","Travel","Food","Tech","Art"])
#
# # Button to submit
# if st.button("Submit"):
#     if not name or not age or not interests:
#         st.error("Please fill in all fields.")
#     else:
#         st.success(f"Hello {name}, age {age}, you like {', '.join(interests)}!")
