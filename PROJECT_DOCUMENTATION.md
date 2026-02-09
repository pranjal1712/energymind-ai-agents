# 📘 Autonomous Energy Researcher Agent - Project Documentation

## 1. Project Overview
**Project Name:** EnergyMind AI
**Objective:** To build an autonomous AI agent capable of researching, analyzing, and writing high-quality reports specifically for the **Energy Industry**.

This system is not just a chatbot; it is an intelligent **Agentic Workflow** that acts like a team of experts (Researcher, Analyst, Writer, Editor) working together to produce a final report.

---

## 2. Technology Stack & Why We Used Them

| Technology | Role | Why we used it? | Benefit |
| :--- | :--- | :--- | :--- |
| **Python** | Core Language | Industry standard for AI/ML. | Huge library support (LangChain, FastAPI). |
| **FastAPI** | Backend API | Modern, fast web framework for Python. | Easy integration with AI models, auto-docs (Swagger). |
| **Streamlit** | Frontend UI | Rapid UI development for data apps. | Interactive, python-based, no HTML/CSS knowledge needed. |
| **LangChain** | LLM Framework | Tools to connect LLMs with data. | Standard interface for Prompts, Chains, and Tools. |
| **LangGraph** | Orchestration | **Crucial Upgrade:** Manages complex workflows (Loops, Memory). | Allows the bot to "think", "review", and "refine" its work. |
| **Groq (Llama-3)** | AI Model | The "Brain" of the agent. | Extremely fast inference speed (essential for agent loops). |
| **Tavily AI** | Search Tool | Optimized search API for LLMs. | Returns clean text data instead of messy HTML (better than Google for bots). |

---

## 3. High-Level Architecture
The project follows a **Client-Server Architecture**:

1.  **Frontend (Streamlit)**: 
    *   User types a query (e.g., "Hydrogen Market Trends").
    *   Generates a unique `session_id`.
    *   Sends request to Backend via API.
2.  **Backend (FastAPI)**:
    *   Receives request.
    *   Activates the **LangGraph Workflow**.
3.  **AI Workflow (The Brain)**:
    *   Gatekeeper -> Researcher -> Analyst -> Writer -> Reviewer -> Suggestions.

---

## 4. Key Features & Implementation Details

### A. LangGraph Workflow (The "Brain")
Instead of a simple linear chain (A -> B -> C), we used a **State Graph**.

*   **Why?** Real-world tasks need feedback. If a report is bad, we need to rewrite it.
*   **Nodes:**
    1.  **Gatekeeper**: Checks *"Is this about Energy?"*. If NO -> Stop.
    2.  **Researcher**: Searches the web using Tavily.
    3.  **Analyst**: extracting trends and risks from raw data.
    4.  **Writer**: Writes the draft report.
    5.  **Reviewer**: **(Quality Check Loop)** Evaluation of the report. If "FAIL", sends it back to Writer.
    6.  **Suggester**: Generates follow-up questions.

**Benefit:** Ensures high quality. The bot "self-corrects" before showing the answer.

### B. Session Memory (Short-Term)
*   **What?** The bot remembers what you said *in the current session*.
*   **How?** We use `MemorySaver` in LangGraph and pass a `thread_id` (Session ID).
*   **Example:**
    *   User: "Who is CEO of Tesla?" -> AI: "Elon Musk."
    *   User: "How old is he?" -> AI: "He is 52." (Understands "He" = Musk).
*   **Privacy:** When you refresh the page, a new `session_id` is generated, and memory is wiped.

### C. Domain Restriction (Gatekeeper)
*   **What?** Restricts the bot to ONLY answer Energy-related queries.
*   **How?** A dedicated LLM node checks relevance before researching.
*   **Example:**
    *   "Solar Panel stats" -> ✅ Process.
    *   "Cricket match score" -> ⛔ Refuse.

### D. Modern UI (Frontend)
*   **What?** A professional, clean interface.
*   **Features:**
    *   Dark Mode / Glassmorphism aesthetics.
    *   Hidden Streamlit branding (Footer, Hamburger menu) for a custom look.
    *   Chat interface with history.

---

## 5. Workflow Example (Step-by-Step)

**User Query:** *"Current status of Solid State Batteries"*

1.  **Frontend**: Generates `session_id: 12345`, sends to Backend.
2.  **Backend (Gatekeeper)**: Checks query. "Yes, it is Energy related." -> Proceed.
3.  **Researcher**: Searches Tavily. Finds "Toyota plans 2027 launch", "Samsung SDI updates".
4.  **Analyst**: Extracts point: "Key trend is commercialization by 2027".
5.  **Writer**: Drafts a report.
6.  **Reviewer**: Checks draft.
    *   *Scenario A*: Report is too short. -> feedback: "Add more details." -> **Loop back to Writer**.
    *   *Scenario B*: Report is good. -> **PASS**.
7.  **Suggester**: Adds questions like "What are the costs vs Li-ion?".
8.  **Frontend**: Displays final report to user.

---

## 6. Project Structure

```
PROJECT_ROOT/
├── backend/
│   ├── main.py             # FastAPI App (API Endpoints)
│   ├── research_chain.py   # The AI Brain (LangGraph, Nodes, Logic)
│   ├── models.py           # Data structures (Pydantic)
│   └── database.py         # SQLite DB for history
├── frontend/
│   ├── app.py              # Streamlit App (UI, State Management)
│   └── auth.py             # Login/Signup Logic
├── knowledge_base/         # Automatic saving of reports (.txt)
├── requirements.txt        # Python dependencies
└── README.md               # Setup instructions
```


---

## 8. Scalability & Performance

### How it handles load?
*   **Async Functionality**: FastAPI is asynchronous, meaning it can handle multiple requests concurrently without blocking.
*   **Stateless Backend**: The server doesn't store session data in memory indefinitely; it relies on the database and LangGraph state, making it easy to scale horizontally (add more servers).

### How to scale further?
*   **Redis for Caching**: Implement Redis to cache frequent search results (e.g., "Solar Price 2024") to save API costs and speed up responses.
*   **Vector Database (RAG)**: Integrate Pinecone or Weaviate to store millions of documents, allowing the bot to search internal company data, not just the web.

---

## 9. Security Measures
1.  **Environment Variables**: API keys (Groq, Tavily) are stored in `.env` and never exposed in code.
2.  **Input Sanitation**: The `Gatekeeper` node prevents prompt injection or irrelevant queries.
3.  **Session Isolation**: Each user gets a unique `session_id`, ensuring no data leaks between users.

---

## 10. Future Roadmap
*   **Multi-Agent Collaboration**: Add a "Debater" node that challenges the Writer's assumptions for even better analysis.
*   **Chart Generation**: Use Python libraries to generate real charts (matplotlib) based on data, not just text.
*   **User Accounts**: Full login system to save chat history permanently (currently session-based for guests).
*   **Voice Interface**: Add Speech-to-Text to talk to the researcher.

---

## 11. Component Interaction Diagram (Mermaid)

```mermaid
graph TD
    User[User (Frontend)] -->|Query| API[FastAPI Backend]
    API -->|Start Graph| Gatekeeper{Is Energy?}
    Gatekeeper -- No --> Refusal[Refusal Message]
    Gatekeeper -- Yes --> Researcher[Researcher Node]
    Researcher -->|Search Web| Tavily[Tavily API]
    Tavily -->|Results| Analyst[Analyst Node]
    Analyst -->|Insights| Writer[Writer Node]
    Writer -->|Draft Report| Reviewer{Quality Check}
    Reviewer -- Fail --> Writer
    Reviewer -- Pass --> Suggester[Suggester Node]
    Suggester -->|Final Output| API
    API -->|Display| User
```

---
*Generated by EnergyMind AI Team - 2024*
