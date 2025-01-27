from pydantic import BaseModel
from typing import Optional
    
class CrawlJob(BaseModel):
    root_url: str
    max_depth: int
    max_count: int
    include_external: bool
    status: str
    result: Optional[dict]

class CrawlTreeNode(BaseModel):
    title: str
    url: str
    depth: int
    parent: Optional[str]=None
    children: Optional[list]=[]
    
class CrawlRequest(BaseModel):
    root_url: str
    max_depth: int
    max_count: int
    include_external: bool

class UrlRequest(BaseModel):
    url: str
