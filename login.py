# login.py - Streamlit-based login system that authenticates users using predefined credentials,
# manages session states, and allows users to log out.

import streamlit as st

# Load users securely from Streamlit secrets
USERS = st.secrets["USERS"]

def login_page():
    st.title("🔐 EchoPal Login")
    st.write("Please log in to continue.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_data = USERS.get(username)
        if user_data and password == user_data.get("password"):
            st.session_state["authenticated"] = True
            st.session_state["role"] = user_data.get("role", "user")
            st.session_state["email"] = username
            st.success(f"Welcome, {user_data.get('role', 'user').capitalize()}!")
            st.rerun()
        else:
            st.error("Invalid email or password.")

def logout_button():
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
