# Project Replication Guide: GitHub Actions to AWS ECR/EC2

This guide explains how to set up the exact same CI/CD pipeline for a new project.

---

## Step 1: AWS Infrastructure Setup

### 1.1 Create ECR Repository
1. Go to **AWS Console** -> **Elastic Container Registry (ECR)**.
2. Click **Create repository**.
3. Name it (e.g., `new-project`).
4. Copy the **URI** (e.g., `123456789.dkr.ecr.eu-north-1.amazonaws.com/new-project`).

### 1.2 Create EC2 Instance
1. Go to **EC2** -> **Launch Instance**.
2. Select **Amazon Linux 2023**.
3. In **Security Groups**, allow:
   - **SSH (Port 22)**
   - **Custom TCP (Your App Port, e.g., 7860 & 8000)**.

### 1.3 Create IAM Access Keys
1. Go to **IAM** -> **Users** -> Your User.
2. **Security Credentials** -> **Create Access Key**.
3. Copy the **Access Key ID** and **Secret Access Key**.

---

## Step 2: Project Configuration

Add these 3 files to the new project's root folder:

### 2.1 `Dockerfile`
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# Add a startup script if running multiple services
CMD ["python", "main.py"] 
```

### 2.2 `start.sh` (Optional for Multi-service)
```bash
#!/bin/bash
# Start Backend
uvicorn main:app --host 0.0.0.0 --port 8000 &
# Start Frontend
streamlit run app.py --server.port 7860
```

### 2.3 `.github/workflows/ci-cd.yml`
Copy your existing `ci-cd.yml` content and update the `REPOSITORY` name:
```yaml
env:
  REPOSITORY: new-project # Change this to your ECR repo name
```

---

## Step 3: GitHub Secrets
Go to your **GitHub Repo** -> **Settings** -> **Secrets and variables** -> **Actions**.
Add these Secrets:
1. `AWS_ACCESS_KEY_ID`: Your IAM Key.
2. `AWS_SECRET_ACCESS_KEY`: Your IAM Secret.
3. `AWS_REGION`: e.g., `eu-north-1`.

---

## Step 4: Final Deployment (on EC2 Server)

Run these commands on the EC2 terminal one by one:

### 4.1 Install Docker
```bash
sudo dnf install docker -y
sudo systemctl start docker
sudo usermod -a -G docker $USER
# Logout and login back to apply group changes
```

### 4.2 Configure AWS CLI
```bash
aws configure
# Enter your Access Key, Secret Key, and Region (eu-north-1)
```

### 4.3 Login and Run
```bash
# Login to ECR
aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin <YOUR_ECR_URI>

# Pull Image
docker pull <YOUR_ECR_URI>:latest

# Run Container
docker run -d -p 7860:7860 -p 8000:8000 \
  -e SOME_API_KEY="your_value" \
  <YOUR_ECR_URI>:latest
```

---
**Congratulations!** Your new project is now automated. Every `git push` will update the live server.
