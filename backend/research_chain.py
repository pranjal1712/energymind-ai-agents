import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch


from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


load_dotenv()

# =========================
# LLM (Gemini)
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
# 1️⃣ Researcher
# =========================
research_prompt = PromptTemplate.from_template(
    """
You are an Energy Industry Researcher.

Using ONLY the web search results below,
write 5–7 factual bullet points about:

Topic: {query}

Web Results:
{search_results}
"""
)

research_chain = research_prompt | llm

def research_step(query: str) -> str:
    search_results = search_tool.run(query)
    return research_chain.invoke(
        {
            "query": query,
            "search_results": search_results
        }
    ).content

# =========================
# 2️⃣ Analyst
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

analysis_chain = analysis_prompt | llm

def analysis_step(research: str) -> str:
    return analysis_chain.invoke(
        {"research": research}
    ).content

# =========================
# 3️⃣ Writer
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
"""
)

writing_chain = writing_prompt | llm

def writing_step(analysis: str) -> str:
    return writing_chain.invoke(
        {"analysis": analysis}
    ).content

# =========================
# 🚀 Orchestrator
# =========================
# =========================
# 4️⃣ Suggestions Generator
# =========================
suggestions_prompt = PromptTemplate.from_template(
    """
    Based on the following energy report, generate 3 short, relevant follow-up questions that a user might ask next.
    Return ONLY the 3 questions, separated by newlines. No numbering or bullets.

    Report:
    {report}
    """
)

suggestions_chain = suggestions_prompt | llm

def generate_suggestions(report: str) -> list[str]:
    result = suggestions_chain.invoke({"report": report}).content
    # Clean and split
    questions = [q.strip() for q in result.strip().split('\n') if q.strip()]
    return questions[:3]

# =========================
# 🚀 Orchestrator
# =========================
def run_full_research(query: str) -> dict:
    research = research_step(query)
    analysis = analysis_step(research)
    report = writing_step(analysis)
    suggestions = generate_suggestions(report)
    
    return {
        "report": report,
        "suggestions": suggestions
    }
