from pydantic import BaseModel
from typing import Optional

class ScrapeRequest(BaseModel):
    url: str

class ParsedResponse(BaseModel):
    source: str
    title: str
    text: str
    authors: list = []
    summary: Optional[str] = None
    keywords: list = []
    categories: list = []
    publish_date: Optional[str] = None
    length: int
    created_at: str
    links: dict = {}    