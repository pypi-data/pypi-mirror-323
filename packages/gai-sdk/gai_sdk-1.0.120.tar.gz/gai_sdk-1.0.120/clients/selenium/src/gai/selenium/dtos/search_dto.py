from pydantic import BaseModel
from typing import Optional

class SearchRequest(BaseModel):
    query: str
    n_results: int = 10
    period: str = None

class SearchResponseItem(BaseModel):
    title: str
    link: str
    snippet: Optional[str]=""

class SearchResponse(BaseModel):
    result: list[SearchResponseItem]
