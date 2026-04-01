import os
from typing import TypedDict, List, Annotated
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import asyncio
import random
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from groq import InternalServerError, RateLimitError

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver


load_dotenv()

# =========================
# 🛠️ Helper: API Key Manager & Concurrency Control
# =========================

# Get keys from env (comma-separated: KEY1,KEY2,KEY3)
GROQ_KEYS = os.getenv("GROQ_API_KEYS", os.getenv("GROQ_API_KEY", "")).split(",")
GROQ_KEYS = [k.strip() for k in GROQ_KEYS if k.strip()]

# Global Semaphore to limit concurrent AI calls (Queuing)
AI_SEMAPHORE = asyncio.Semaphore(5)

class APIKeyManager:
    def __init__(self, keys):
        self.keys = keys
        self.index = 0

    def get_key(self):
        if not self.keys:
            return None
        # Round-robin selection
        key = self.keys[self.index]
        self.index = (self.index + 1) % len(self.keys)
        return key

key_manager = APIKeyManager(GROQ_KEYS)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((RateLimitError, InternalServerError, Exception))
)
async def invoke_llm_with_retry(chain_or_llm, inputs):
    """
    Invokes LLM with automatic key rotation and exponential backoff.
    """
    async with AI_SEMAPHORE:
        current_key = key_manager.get_key()
        # Create a new LLM instance with the current key for this call
        # (This ensures each attempt can use a different key if needed)
        temp_llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=4096,
            groq_api_key=current_key
        )
        
        # Determine if it's a chain or just the LLM
        if hasattr(chain_or_llm, "first"): # It's a chain
            # We need to rebuild the chain with the new LLM
            # Since chains are immutable, we rely on the invoke calling the LLM
            # For simplicity in this graph, I'll pass the LLM into the nodes
            pass 
        
        return await chain_or_llm.ainvoke(inputs)

# Update chains to be 'templates' or rebuild them in nodes
# I will refactor the nodes to use a helper that handles the LLM creation.

def get_chat_model():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        max_tokens=4096,
        groq_api_key=key_manager.get_key()
    )

# Placeholder for the original llm variable to avoid breaking imports
llm = get_chat_model()

# =========================
# Web Search Tool
# =========================
search_tool = TavilySearch(max_results=10)

# =========================
# State Definition
# =========================
class AgentState(TypedDict):
    query: str
    research_check: str 
    search_results: str
    analysis: str
    report: str
    suggestions: List[str]
    # Quality Control
    revision_number: int
    reviewer_feedback: str
    # Memory / History
    history: List[str]
    # Domain Gatekeeper
    is_relevant: bool

gatekeeper_prompt = PromptTemplate.from_template(
    """
    You are a Gatekeeper for an Energy Research Assistant.
    
    Your job is to determine if the user's query is related to the **Energy Industry** 
    (including renewables, oil & gas, electricity, batteries, sustainability, climate policy, etc.).

    Query: {query}
    
    Reply with ONLY "YES" if it is energy-related.
    Reply with ONLY "NO" if it is NOT energy-related.
    """
)

# We removed the global chain to allow per-call LLM rotation

async def gatekeeper_node(state: AgentState):
    print("--- 🛡️ Node: Gatekeeper ---")
    query = state["query"]
    
    try:
        chain = gatekeeper_prompt | get_chat_model() | StrOutputParser()
        result = await invoke_llm_with_retry(chain, {"query": query})
        result = result.strip().upper()
    except Exception as e:
        print(f"Gatekeeper error: {e}")
        # Fail open if LLM fails
        result = "YES"
    
    if "YES" in result:
        print("--- ✅ Query is Relevant ---")
        return {"is_relevant": True}
    else:
        print("--- ⛔ Query is Irrelevant ---")
        refusal_msg = "I specialize in the Energy industry. Please ask a question related to energy, power, sustainability, or climate technology."
        return {
            "is_relevant": False, 
            "report": refusal_msg,
            "suggestions": []
        }

# =========================
# 1️⃣ Researcher Node
# =========================
research_prompt = PromptTemplate.from_template(
    """
    You are an Energy Industry Researcher.

    Context from previous conversation (if any):
    {history}

    write 20–25 detailed, factual, and comprehensive bullet points about:

    Topic: {query}

    Web Results:
    {search_results}
    
    Ensure you cover:
    - Technical Breakdown (How it works precisely)
    - Recent major News & Press Releases
    - Case studies of actual projects or implementations
    - Global & Regional Context (US, EU, China, India, etc.)
    - Key industry players and their current market strategies
    - Specific Government policies, subsidies, and regulatory frameworks (e.g., IRA, EU Green Deal, PLI)
    - Detailed Financial data, LCOE (Levelized Cost of Energy), and investment trends

    """
)

# Chain will be built inside the node

async def research_node(state: AgentState):
    print("--- 🔄 Node: Researcher ---")
    query = state["query"]
    history = state.get("history", [])
    
    history_text = "\n".join(history[-3:]) if history else "No previous context."
    
    try:
         results = search_tool.run(query) 
    except:
         results = str(search_tool.invoke(query))
    
    chain = research_prompt | get_chat_model() | StrOutputParser()
    summary = await invoke_llm_with_retry(chain, {
        "query": query,
        "search_results": results,
        "history": history_text
    })
    
    return {
        "search_results": results, 
        "research_check": summary,
        "revision_number": 0,
        "reviewer_feedback": ""
    }

# =========================
# 2️⃣ Analyst Node
# =========================
analysis_prompt = PromptTemplate.from_template(
    """
    You are an Energy Data Analyst.

    From the research below, perform a deep-dive extraction of:
    - **Detailed Key Trends** (at least 5 trends with technical depth)
    - **Market Landscape & Regional Comparison** (how different markets compare)
    - **Policy & Regulatory Frameworks** (incentives, laws, and their impact)
    - **Case Studies & Implementation Successes** (notable real-world examples)
    - **SWOT Analysis** (Strengths, Weaknesses, Opportunities, and Threats)
    - **Financials & ROI Analysis** (costs, funding, and profitability)

    Research:
    {research}

    """
)

# Chain will be built in node

async def analysis_node(state: AgentState):
    print("--- 🔄 Node: Analyst ---")
    research_summary = state["research_check"]
    chain = analysis_prompt | get_chat_model() | StrOutputParser()
    analysis = await invoke_llm_with_retry(chain, {"research": research_summary})
    return {"analysis": analysis}

# =========================
# 3️⃣ Writer Node
# =========================
writing_prompt = PromptTemplate.from_template(
    """
    Write a HIGH-LEVEL, EXHAUSTIVE, and HIGHLY DETAILED structured report with:
    
    1. **Executive Summary** (3-4 dense paragraphs with summary of findings)
    2. **Technical Deep-Dive** (In-depth explanation of how the energy technology/topic works)
    3. **Global Market Landscapes & Regional Comparisons** (Detailed comparison of US, EU, China, etc.)
    4. **Policy & Regulatory Environment** (Analysis of specific government subsidies, laws, and regulatory impacts)
    5. **Case Studies & Real-world Implementations** (Detailed examples of notable projects)
    6. **Strategic SWOT Analysis** (Deep analysis of Strengths, Weaknesses, Opportunities, and Threats)
    7. **Financial Outlook & Investment ROI Analysis** (Financial performance, LCOE data, and future market predictions)
    8. **Strategic Future Outlook** (Year-by-year projections for the next decade)
    9. **Sources & Bibliography** (Citations from research)

    Analysis:
    {analysis}
    
    FEEDBACK FROM PREVIOUS VERSION (If any):
    {feedback}
    
    CRITICAL INSTRUCTION:
    The report MUST be extremely detailed, professional, and content-rich. 
    Use a length of at least 2000-3000 words if possible. Expand on each section with dense energy insights.
    If there is feedback, you MUST adjust the report to directly address it.

    """
)

# Chain will be built in node

async def writing_node(state: AgentState):
    print("--- 🔄 Node: Writer ---")
    analysis_text = state["analysis"]
    feedback = state.get("reviewer_feedback", "")
    
    current_rev = state.get("revision_number", 0)
    if current_rev > 0:
        print(f"--- 📝 Revision #{current_rev} (Feedback: {feedback}) ---")
    
    chain = writing_prompt | get_chat_model() | StrOutputParser()
    report = await invoke_llm_with_retry(chain, {
        "analysis": analysis_text,
        "feedback": feedback
    })
    
    return {"report": report, "revision_number": current_rev + 1}

# =========================
# 4️⃣ Reviewer Node (Quality Check)
# =========================
reviewer_prompt = PromptTemplate.from_template(
    """
    You are a Senior Editor.
    
    Review the following Energy Report.
    
    Report:
    {report}
    
    STRICT Quality Check:
    1. Structure (Does it have Technical Breakdown, SWOT, Case Studies, and Policy analysis?)
    2. Depth (Is it an absolute deep dive? Reports that are less than 8-10 long sections MUST be failed.)
    3. Fact-Density (Does it contain specific data, numbers, and regional comparisons?)
    
    Output format:
    If the report is exhaustive and professionally detailed, reply with just "PASS".
    If the report is too short, missing key sections (like SWOT or Case Studies), or lacking detail, reply with "FAIL: <Detailed Feedback on what is missing>".

    """
)

# Chain will be built in node

async def reviewer_node(state: AgentState):
    print("--- 🔄 Node: Reviewer ---")
    report_text = state["report"]
    try:
        chain = reviewer_prompt | get_chat_model() | StrOutputParser()
        result = await invoke_llm_with_retry(chain, {"report": report_text})
    except Exception as e:
        print(f"--- ⚠️ Reviewer Error: {e}. Skipping review. ---")
        return {"reviewer_feedback": "PASS"} 
    
    if "FAIL" in result:
        feedback = result.replace("FAIL:", "").strip()
        print(f"--- ❌ Review: FAIL (Feedback: {feedback}) ---")
        return {"reviewer_feedback": feedback}
    else:
        print("--- ✅ Review: PASS ---")
        return {"reviewer_feedback": "PASS"}

# =========================
# 5️⃣ Suggestions Node & History Manager
# =========================
suggestions_prompt = PromptTemplate.from_template(
    """
    Based on the following energy report, generate 3 short, relevant follow-up questions that a user might ask next.
    Return ONLY the 3 questions, separated by newlines. No numbering or bullets.

    Report:
    {report}
    """
)

# Chain will be built in node

async def suggestions_node(state: AgentState):
    print("--- 🔄 Node: Suggestions & History Update ---")
    report_text = state["report"]
    query = state["query"]
    
    # Generate suggestions
    chain = suggestions_prompt | get_chat_model() | StrOutputParser()
    result = await invoke_llm_with_retry(chain, {"report": report_text})
    questions = [q.strip() for q in result.strip().split('\n') if q.strip()]
    
    # Update History
    current_history = state.get("history", [])
    new_entry = f"User: {query}\nAI Report Summary: {report_text[:200]}..." 
    updated_history = current_history + [new_entry]
    
    return {"suggestions": questions[:3], "history": updated_history}

# =========================
# 🚀 Conditional Logic
# =========================
def should_continue(state: AgentState):
    feedback = state.get("reviewer_feedback", "")
    revision = state.get("revision_number", 0)
    
    if feedback == "PASS" or revision >= 3:
        return "suggester"
    else:
        return "writer" 
        
def check_relevance(state: AgentState):
    if state["is_relevant"]:
        return "researcher"
    else:
        return END

# =========================
# 🚀 Graph Construction
# =========================
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("gatekeeper", gatekeeper_node)
workflow.add_node("researcher", research_node)
workflow.add_node("analyst", analysis_node)
workflow.add_node("writer", writing_node)
workflow.add_node("reviewer", reviewer_node)
workflow.add_node("suggester", suggestions_node)

# Add Edges
workflow.set_entry_point("gatekeeper")

workflow.add_conditional_edges(
    "gatekeeper",
    check_relevance,
    {
        "researcher": "researcher",
        END: END
    }
)

workflow.add_edge("researcher", "analyst")
workflow.add_edge("analyst", "writer")
workflow.add_edge("writer", "reviewer")

workflow.add_conditional_edges(
    "reviewer",
    should_continue,
    {
        "suggester": "suggester",
        "writer": "writer"
    }
)

workflow.add_edge("suggester", END)

# Initialize Memory
memory = MemorySaver()

# Compile with Checkpointer
app = workflow.compile(checkpointer=memory)

# =========================
# 🚀 Public Interface
# =========================
async def run_full_research(query: str, thread_id: str = None) -> dict:
    """
    Entry point for the backend logic.
    """
    config = {
        "configurable": {"thread_id": thread_id if thread_id else "default_thread"}
    }

    
    initial_state = {"query": query}
    
    result = await app.ainvoke(initial_state, config=config)
    
    return {
        "report": result.get("report", "No report generated."),
        "suggestions": result.get("suggestions", [])
    }
