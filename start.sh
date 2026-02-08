#!/bin/bash

# Start Backend in background
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# Start Frontend
# We need to tell Streamlit to use the local backend
export API_URL="http://localhost:8000"

# Streamlit runs on port 7860 (Hugging Face default)
streamlit run frontend/app.py --server.port 7860 --server.address 0.0.0.0
