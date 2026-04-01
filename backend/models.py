from pydantic import BaseModel
from typing import List, Optional

class ResearchRequest(BaseModel):
    query: str
    thread_id: Optional[str] = None


class ResearchResponse(BaseModel):
    query: str
    result: str
    suggestions: Optional[List[str]] = []
    file_path: Optional[str] = None
    file_path: str
    suggestions: list[str] = []
