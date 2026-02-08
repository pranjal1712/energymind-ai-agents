# 🚀 Deployment Guide (Railway)

This guide shows you how to deploy the **EnergyMind AI** agent to [Railway](https://railway.app/).

## Prerequisites
- A [GitHub account](https://github.com/) with this repository pushed.
- A [Railway account](https://railway.app/) (Login with GitHub).

## Pricing & Options

### Option 1: Railway (Easiest & Fastest, but PAID)
- **Cost**: ~$5/month after trial (pay for what you use).
- **Pros**: Very easy, always on, fast.
- **Cons**: Not free forever.

### Option 2: Render + Streamlit Cloud (FREE Tier)
- **Backend (Render)**: Free "Web Service" tier. 
  - *Note: It "sleeps" after inactivity, so the first request takes ~50s to wake up.*
- **Frontend (Streamlit Cloud)**: Completely Free.
- **Pros**: $0 cost.
- **Cons**: Slower startup time for backend, slightly more setup (two platforms).

## Steps for Railway (Recommended for Ease)

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
### Option 3: Hugging Face Spaces (Community Favorite & FREE)
- **Cost**: Free CPU tier.
- **Pros**: Designed for AI apps, easy setup, great community.
- **Cons**: Public by default (unless paid), sleeps after 48h inactivity.

## Steps for Railway (Recommended for Ease)
... (Existing Railway Steps) ...

## Steps for Hugging Face Spaces (Best Free Option)

### 1. Create a Space
1.  Go to [huggingface.co/spaces](https://huggingface.co/spaces) and create a new Space.
2.  **SDK**: Select **Docker** (since we have mixed Python/FastAPI/Streamlit).
3.  **Hardware**: Free (CPU basic).

### 2. Configure Dockerfile
Great news! I have already included the `Dockerfile` and `start.sh` in the repository. This setup runs both the Backend and Frontend in a single Space.

### 3. Sync with GitHub
1.  In your Space settings, go to **"Files and versions"**.
2.  Click **"Add file"** > **"Upload files"** OR proceed to connect your GitHub repository if that feature is available to you (Settings > specialized hardware/git logic).
3.  **Easiest Method**: 
    - Clone your Space locally: `git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`
    - Copy all files from this project into that folder.
    - Push to Hugging Face: `git add . && git commit -m " Deploy" && git push`
    
    *Alternatively, you can just manually upload `Dockerfile`, `start.sh`, `requirements.txt` and the `frontend/backend` folders via the Web UI if you prefer.*

4.  **Environment Variables**:
    - Go to **Settings** > **Variables and secrets**.
    - Add `GROQ_API_KEY` and `TAVILY_API_KEY`.

5.  **App runs!** The Space will build (this takes a few minutes) and then your app will be live!

---

## Steps for Render + Streamlit Cloud (Traditional Free)

### A. Deploy Backend on Render
1.  Go to [dashboard.render.com](https://dashboard.render.com/).
2.  Click **New +** > **Web Service**.
3.  Connect your GitHub repo.
4.  **Runtime**: Python 3.
5.  **Build Command**: `pip install -r requirements.txt`
6.  **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
7.  **Environment Variables**: Add `GROQ_API_KEY` and `TAVILY_API_KEY`.
8.  Deploy! Copy the URL (e.g., `https://my-backend.onrender.com`).

### B. Deploy Frontend on Streamlit Cloud
1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Connect your GitHub repo.
3.  Select `frontend/app.py` as the main file path.
4.  Click **Advanced Settings**.
5.  Add Variable `API_URL` with your Render Backend URL.
6.  Deploy!

