from pydantic import BaseModel

class ResearchRequest(BaseModel):
    query: str
    thread_id: str = None


class ResearchResponse(BaseModel):
    query: str
    result: str
    file_path: str
    suggestions: list[str] = []
