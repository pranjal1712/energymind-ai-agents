# 🚀 Deployment Guide (Hugging Face Spaces)

This guide shows you how to deploy the **EnergyMind AI** agent to [Hugging Face Spaces](https://huggingface.co/spaces) using Docker. This is a **Free** and robust option that runs both the Backend and Frontend together.

## Prerequisites
- A [GitHub account](https://github.com/) with this repository pushed.
- A [Hugging Face account](https://huggingface.co/join).

## Deployment Steps

### 1. Create a Space
1.  Go to [huggingface.co/spaces](https://huggingface.co/spaces) and click **"Create new Space"**.
2.  **Name**: Give your space a name (e.g., `energymind-ai`).
3.  **License**: Open Source (e.g., MIT) or blank.
4.  **SDK**: Select **Docker** (Crucial step!).
5.  **Hardware**: Select **Free** (CPU basic).
6.  Click **"Create Space"**.

### 2. Upload Code
Hugging Face needs your code to build the app. The easiest way is to sync it with your computer or upload files directly.

#### Option A: Clone and Push (Recommended)
1.  On your Space page, follow the instructions to clone the repo:
    ```bash
    git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
    ```
2.  Copy **all files** from your local `energymind-ai-agents` project into this new folder.
3.  Push the files to Hugging Face:
    ```bash
    git add .
    git commit -m "Deploy App"
    git push
    ```

#### Option B: Drag and Drop
1.  In your Space, go to **"Files"**.
2.  Click **"Add file"** > **"Upload files"**.
3.  Upload `Dockerfile`, `start.sh`, `requirements.txt`, `readme.md`, `.env.example`, and the `backend` & `frontend` folders.
4.  Commit changes.

### 3. Environment Variables
Your app needs API keys to work.

1.  In your Space, click on **Settings**.
2.  Scroll down to **"Variables and secrets"**.
3.  Click **"New Secret"** (Secrets are hidden, Variables are public - use Secrets for keys).
4.  Add the following secrets:
    - `GROQ_API_KEY`: Paste your Groq API Key.
    - `TAVILY_API_KEY`: Paste your Tavily API Key.

### 4. Build and Run
- Once files are uploaded, Hugging Face will automatically start **Building** your app.
- Click on **"App"** tab to see the logs.
- After a few minutes, your status will change to **Running**, and your app will be live! 🚀

## Troubleshooting
- **Build Failed?** Check the **Logs** tab in your Space.
- **Application Error?** Ensure you added the API Keys in Settings correctly.
- **"Sleep"?** Free Spaces "sleep" after 48 hours of inactivity. Just open the URL to wake it up (takes a few seconds).

## Steps for Render + Streamlit Cloud (Option 4)

This method splits the app: **Backend on Render** and **Frontend on Streamlit Cloud**.

### Part A: Deploy Backend to Render
1.  Sign up at [render.com](https://render.com).
2.  Click **"New +"** -> **"Web Service"**.
3.  Connect your GitHub repo.
4.  Settings:
    - **Name**: `energymind-backend` (or unique name)
    - **Runtime**: Python 3
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5.  **Environment Variables** (Add these in "Advanced" section):
    - `PYTHON_VERSION`: `3.10.12`
    - `GROQ_API_KEY`: (Your key)
    - `TAVILY_API_KEY`: (Your key)
6.  Click **"Create Web Service"**.
7.  Wait for deploy. Copy the **Service URL** (e.g., `https://energymind-backend.onrender.com`).

### Part B: Deploy Frontend to Streamlit Cloud
1.  Sign up at [share.streamlit.io](https://share.streamlit.io).
2.  Click **"New app"**.
3.  Select your GitHub repo.
4.  Settings:
    - **Main file path**: `frontend/app.py`
5.  **Advanced Settings** -> **Secrets**:
    Add your Backend URL here like this:
    ```toml
    API_URL = "https://energymind-backend.onrender.com"
    ```
6.  Click **"Deploy"**.

Your frontend will now talk to your Render backend!
