import requests
import streamlit as st

API_URL = "http://localhost:8000"

def login_user(username, password):
    try:
        response = requests.post(
            f"{API_URL}/token",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def signup_user(username, email, password):
    try:
        response = requests.post(
            f"{API_URL}/signup",
            json={"username": username, "email": email, "password": password}
        )
        if response.status_code == 200:
            return response.json()
        return {"error": response.json().get("detail", "Signup failed")}
    except Exception as e:
        return {"error": str(e)}

def get_current_user_info(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/me", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_user_history(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/history", headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []
