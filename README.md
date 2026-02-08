# Autonomous Energy Researcher Agent

A full-stack AI agent application that researches energy topics using CrewAI, powered by FastAPI (Backend) and Streamlit (Frontend).

## Prerequisites

- Python 3.10+
- Groq API Key (for LLM)
- Tavily API Key (for Search)

## Installation

1.  **Clone/Open the Repository**
2.  **Environment Setup**
    I have already created a virtual environment for you in the `venv` folder.
    
    **Activate it:**
    ```powershell
    .\venv\Scripts\activate
    ```

    **Install Dependencies (if not already installed)**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Environment Variables**
    Copy `.env.example` to `.env` and fill in your keys:
    ```bash
    cp .env.example .env
    # Edit .env file
    ```

## Running the Application

You need to run the Backend and Frontend in separate terminals.

### 1. Start the Backend (FastAPI)
```bash
uvicorn backend.main:app --reload
```
The API will run at `http://localhost:8000`.

### 2. Start the Frontend (Streamlit)
```bash
streamlit run frontend/app.py
```
The UI will open in your browser at `http://localhost:8501`.

## Features
- **Project Structure**: Clean separation of Backend and Frontend.
- **Autonomous Agents**: Uses CrewAI with Research, Analyst, and Writer agents.
- **Persistence**: Saves research results as text files in `backend/knowledge_base/`.
- **API**: FastAPI endpoints for triggering research and retrieving history.
- **UI**: Simple Streamlit interface.

## Tech Stack
- **Backend**: FastAPI, CrewAI, Pydantic
- **Frontend**: Streamlit
- **Tools**: SerperDev (Search), Python-Slugify
