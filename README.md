# Autonomous Energy Researcher Agent

A full-stack AI agent application that researches energy topics using CrewAI, powered by FastAPI (Backend) and Streamlit (Frontend).

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/pranjal1712/Energymind-ai)

## Prerequisites

- Python 3.10+
- Groq API Key (for LLM)
- Tavily API Key (for Search)

## Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/pranjal1712/energymind-ai-agents.git
    cd energymind-ai-agents
    ```

2.  **Create Virtual Environment**
    It's recommended to use a virtual environment to manage dependencies.
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables**
    This project requires API keys for LLM and Search.
    
    - Copy the example environment file:
      ```bash
      # Windows (PowerShell)
      cp .env .env.example

      # Mac/Linux
      cp .env.example .env
      ```
    - Open `.env` and add your API keys:
      ```env
      GROQ_API_KEY=your_key_here
      TAVILY_API_KEY=your_key_here
      ```

## Running the Application

You need to run the **Backend** and **Frontend** in two separate terminals.

### 1. Start the Backend (FastAPI)
Open a new terminal, activate the venv, and run:
```bash
uvicorn backend.main:app --reload
```
The API will start at `http://localhost:8000`.

### 2. Start the Frontend (Streamlit)
Open another terminal, activate the venv, and run:
```bash
streamlit run frontend/app.py
```
The UI will automatically open in your browser at `http://localhost:8501`.

## Features
- **Project Structure**: Clean separation of Backend and Frontend.
- **Autonomous Agents**: Uses CrewAI with Research, Analyst, and Writer agents.
- **Persistence**: Saves research results as text files in `backend/knowledge_base/`.
- **API**: FastAPI endpoints for triggering research and retrieving history.
- **UI**: Simple Streamlit interface.

## Tech Stack
- **Backend**: FastAPI, Langchain, Pydantic
- **Frontend**: Streamlit
- **Tools**: Tavily (Search), Python-Slugify
