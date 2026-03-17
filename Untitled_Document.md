# Low Level Design (LLD) Report: EnergyMind AI Agents

**Project Name:** EnergyMind AI Agents  
**Version:** 1.0  
**Date:** March 17, 2026

---

## 1. Introduction

### 1.1. Scope of the document
This document provides a low-level technical design of the EnergyMind AI Agents system. It covers the internal architecture, data flow, component definitions, database schema, and API specifications. It serves as a blueprint for developers to understand and maintain the system.

### 1.2. Intended Audience
- **Developers:** For implementation and maintenance.
- **System Architects:** To review technical decisions.
- **QA Engineers:** To design test cases based on process flows.

### 1.3. System overview
EnergyMind AI Agents is an autonomous energy research assistant. It uses a multi-agent system (coordinated by LangGraph) to process user queries, perform web research using Tavily, analyze data using Groq LLMs (Llama 3.1), and generate professional reports. The system includes a FastAPI backend and a Streamlit-based frontend dashboard.

---

## 2. System Design

### 2.1. Application Design
The application follows a decoupled client-server architecture:
- **Frontend Layer:** Streamlit application providing the UI, handling user authentication (via JWT), and displaying research results.
- **API Layer:** FastAPI server acting as the orchestrator.
- **Intelligence Layer:** LangGraph-based state machine that coordinates specialized agent nodes.
- **Data Layer:** SQLite database for user sessions, chat history, and research caching.

### 2.2. Process Flow
The research process follows a directed graph logic:
1. **Gatekeeper:** Validates if the query is energy-related.
2. **Researcher:** Fetches live data via Tavily Search.
3. **Analyst:** Breaks down the research into trends, risks, and opportunities.
4. **Writer:** Drafts a structured professional report.
5. **Reviewer:** A quality-check loop that ensures the report meets standards; if fails, it sends back to the Writer with feedback.
6. **Suggester:** Generates follow-up questions for the user.

### 2.3. Information Flow
1. **User Input:** Query sent from Streamlit via HTTPS.
2. **Auth Verification:** Backend validates the JWT token.
3. **State Initialization:** A new LangGraph state is created with the user query.
4. **Tool Execution:** Agent nodes call external LLM (Groq) and Search (Tavily) tools.
5. **Persistence:** The final state and report are saved to `users.db`.
6. **Response:** The formatted JSON result is sent back to the frontend.

### 2.4. Components Design
#### 2.4.1. Database Schema (SQLite)
- **`users` Table:** Stores `username`, `email`, and `hashed_password`.
- **`chat_history` Table:** Stores `user_id`, `query`, `response`, and `timestamp`.
- **`knowledge_base` Table:** Stores query cache (slugified) and full report content to optimize repeated searches.

#### 2.4.2. Core Logic (LangGraph)
- **State Definition:** `AgentState` TypedDict containing query, search results, analysis, report, and revision feedback.
- **Gatekeeper Node:** LLM-based binary classifier (Relevant/Irrelevant).
- **Reviewer Node:** Conditional edge logic `should_continue` based on "PASS/FAIL" status.

### 2.5. Containerization Design (Docker)
The system is fully containerized using Docker to ensure environment consistency across development and production (AWS EC2).

#### 2.5.1. Dockerfile Logic
- **Base Image:** `python:3.10-slim` for a lightweight runtime.
- **Layer Optimization:** Dependencies are installed separately from the source code to leverage Docker layer caching.
- **Startup Orchestration:** Uses a `start.sh` script to launch both the FastAPI backend and Streamlit frontend as background/foreground processes within a single container.

#### 2.5.2. Port Mapping & Networking
- **Internal Ports:** Backend listens on `8000`, Frontend on `7860`.
- **Host Mapping:** Container is deployed with `-p 8501:7860` (UI) and `-p 8000:8000` (API) to allow external access via the EC2 Public IP.

#### 2.5.3. Environment & Security
- **Dynamic Configuration:** Sensitive credentials (GROQ/TAVILY API Keys) are injected via Docker Environment Variables (`-e`) at runtime, preventing hardcoding in the image.

#### 2.5.4. System Monitoring (Portainer)
A dedicated Portainer container is deployed on port `9000` to provide a Web-based GUI for:
- **Container Lifecycle:** Monitoring health (Running/Stopped status), CPU usage, and memory consumption.
- **Log Management:** Real-time access to application logs for debugging without SSH terminal access.
- **Inventory:** Managing all saved images and volumes.

### 2.6. Key Design Considerations
- **Modularity:** Each agent node is independent and can be swapped or upgraded without breaking other nodes.
- **Quality Control:** The Reviewer/Writer loop ensures high-quality output before the user sees it.
- **Scalability:** Dockerized deployment allows for easy scaling on AWS EC2 or ECS.
- **Performance:** SQLite caching avoids redundant LLM and Search API calls for identical queries.

### 2.7. API Catalogue
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/signup` | Registers a new user. |
| `POST` | `/token` | Authenticates user and returns JWT. |
| `POST` | `/research` | Main endpoint to trigger the AI research agent. |
| `GET` | `/history` | Fetches the last 10 research queries for the logged-in user. |
| `GET` | `/me` | Returns current user profile info. |
 
 ### 2.8. Technology Stack Summary
 | Category | Technology Used |
 | :--- | :--- |
 | **Language** | Python 3.10 |
 | **Backend Framework** | FastAPI |
 | **Frontend Framework** | Streamlit |
 | **Agent Orchestration** | LangGraph, LangChain |
 | **Database** | SQLite (SQLAlchemy ORM) |
 | **Search Engine** | Tavily API |
 | **LLM Provider** | Groq (Llama 3.1) |
 | **Environment** | Docker, AWS EC2 |
 
 ### 2.9. Resilience & Error Handling
 - **API Failures:** The system catches LLM and Search API exceptions and returns user-friendly error messages.
 - **State Persistence:** LangGraph's MemorySaver ensures research state is maintained throughout the agent lifecycle.
 - **Retry Mechanism:** The Reviewer-Writer loop acts as a logical retry for quality improvement.
 
 ### 2.10. Detailed Security Design
 - **JWT Authentication:** Secure stateless session management for all protected API routes.
 - **CORS Policies:** Middleware prevents unauthorized cross-origin requests.
 - **Credential Safety:** Uses Docker Environment Variables to keep API keys separate from the build image.

---

## 3. References
- **LangChain/LangGraph Documentation:** For agent orchestration patterns.
- **FastAPI Documentation:** For async API structure.
- **Docker Documentation:** For containerization best practices.
- **Medicaps University & Datagami:** Internal LLD standard templates.