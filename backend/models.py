from pydantic import BaseModel

class ResearchRequest(BaseModel):
    query: str

class ResearchResponse(BaseModel):
    query: str
    result: str
    file_path: str
    suggestions: list[str] = []
