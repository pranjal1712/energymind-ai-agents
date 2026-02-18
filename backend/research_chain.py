import os
from typing import TypedDict, List, Annotated
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# =========================
# LLM (Groq)
# =========================
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# =========================
# Web Search Tool
# =========================
search_tool = TavilySearch(max_results=5)

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

# =========================
# 0️⃣ Gatekeeper Node (Domain Check)
# =========================
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

gatekeeper_chain = gatekeeper_prompt | llm | StrOutputParser()

def gatekeeper_node(state: AgentState):
    print("--- 🛡️ Node: Gatekeeper ---")
    query = state["query"]
    
    try:
        result = gatekeeper_chain.invoke({"query": query}).strip().upper()
    except:
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

    Using ONLY the web search results below,
    write 5–7 factual bullet points about:

    Topic: {query}

    Web Results:
    {search_results}
    """
)

research_chain = research_prompt | llm | StrOutputParser()

def research_node(state: AgentState):
    print("--- 🔄 Node: Researcher ---")
    query = state["query"]
    history = state.get("history", [])
    
    history_text = "\n".join(history[-3:]) if history else "No previous context."
    
    try:
         results = search_tool.run(query) 
    except:
         results = str(search_tool.invoke(query))
    
    summary = research_chain.invoke({
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

    From the research below, extract:
    - Key trends
    - Market opportunities
    - Risks

    Research:
    {research}
    """
)

analysis_chain = analysis_prompt | llm | StrOutputParser()

def analysis_node(state: AgentState):
    print("--- 🔄 Node: Analyst ---")
    research_summary = state["research_check"]
    analysis = analysis_chain.invoke({"research": research_summary})
    return {"analysis": analysis}

# =========================
# 3️⃣ Writer Node
# =========================
writing_prompt = PromptTemplate.from_template(
    """
    You are a Senior Energy Reporter.

    Write a structured report with:
    1. Executive Summary
    2. Key Trends
    3. Market Impact
    4. Future Outlook
    5. Sources

    Analysis:
    {analysis}
    
    FEEDBACK FROM PREVIOUS VERSION (If any):
    {feedback}
    
    If there is feedback, you MUST adjust the report to address it.
    """
)

writing_chain = writing_prompt | llm | StrOutputParser()

def writing_node(state: AgentState):
    print("--- 🔄 Node: Writer ---")
    analysis_text = state["analysis"]
    feedback = state.get("reviewer_feedback", "")
    
    current_rev = state.get("revision_number", 0)
    if current_rev > 0:
        print(f"--- 📝 Revision #{current_rev} (Feedback: {feedback}) ---")
    
    report = writing_chain.invoke({
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
    
    Check for:
    1. Structure (Does it have Executive Summary, Trends, Impact, Outlook?)
    2. Depth (Is it detailed enough?)
    
    Output format:
    If the report is good, reply with just "PASS".
    If the report needs improvement, reply with "FAIL: <Brief Feedback/Reason>".
    """
)

reviewer_chain = reviewer_prompt | llm | StrOutputParser()

def reviewer_node(state: AgentState):
    print("--- 🔄 Node: Reviewer ---")
    report_text = state["report"]
    try:
        result = reviewer_chain.invoke({"report": report_text})
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

suggestions_chain = suggestions_prompt | llm | StrOutputParser()

def suggestions_node(state: AgentState):
    print("--- 🔄 Node: Suggestions & History Update ---")
    report_text = state["report"]
    query = state["query"]
    
    # Generate suggestions
    result = suggestions_chain.invoke({"report": report_text})
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
def run_full_research(query: str, thread_id: str = None) -> dict:
    """
    Entry point for the backend logic.
    """
    config = {
        "configurable": {"thread_id": thread_id if thread_id else "default_thread"}
    }

    
    initial_state = {"query": query}
    
    result = app.invoke(initial_state, config=config)
    
    return {
        "report": result.get("report", "No report generated."),
        "suggestions": result.get("suggestions", [])
    }
