# 🚀 Deployment Guide (Railway)

This guide shows you how to deploy the **EnergyMind AI** agent to [Railway](https://railway.app/).

## Prerequisites
- A [GitHub account](https://github.com/) with this repository pushed.
- A [Railway account](https://railway.app/) (Login with GitHub).

## Steps

### 1. Create a New Project on Railway
1.  Go to your Railway Dashboard.
2.  Click **"+ New Project"** > **"Deploy from GitHub repo"**.
3.  Select your repository (`energymind-ai-agents`).
4.  Click **"Deploy Now"**.

### 2. Configure Services
Railway will try to detect the app. Since we have both a Backend and Frontend, we need to configure them.

#### A. Configure the Backend (FastAPI)
1.  Click on the service card in the Railway canvas.
2.  Go to **Settings**.
3.  Scroll down to **Relational Database** (skip if not using Postgres yet) or just **Start Command**.
4.  **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5.  Go to **Variables** tab.
6.  Add your API Keys:
    - `GROQ_API_KEY`: (Your Key)
    - `TAVILY_API_KEY`: (Your Key)
7.  Go to **Networking**.
8.  Click **Generate Domain**. You will get a URL like `backend-production.up.railway.app`. **Copy this URL.**

#### B. Configure the Frontend (Streamlit)
*Currently, Railway deploys one service per repo by default. To deploy the frontend, you might need to add a second service from the same repo.*

1.  In the same project canvas, click **"+ New"** > **"GitHub Repo"**.
2.  Select the **SAME** repo again.
3.  Click on this new service card (it might be named differently).
4.  Go to **Settings**.
5.  **Start Command**: `streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0`
6.  Go to **Variables**.
7.  Add the Backend URL you copied earlier:
    - `API_URL`: `https://backend-production.up.railway.app` (Replace with actual URL)
8.  Go to **Networking** and **Generate Domain**.
9.  This is your App URL! 🚀

## Troubleshooting
- **Build Failed?** Check `Build Logs`. Ensure `requirements.txt` has everything.
- **App Crashes?** Check `Deploy Logs`.
