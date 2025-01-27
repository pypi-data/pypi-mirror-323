from gai.lib.common.http_utils import http_post_async
from ..dtos import SearchRequest, SearchResponse, ScrapeRequest, ParsedResponse

class SeleniumClient:
    
    async def search(self, query:str, n_results:int=10, period=None) -> SearchResponse:
        # curl -X POST "http://localhost:12028/api/v1/googler" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"query\":\"python\",\"n_results\":5}"
        
        url = 'http://localhost:12028/api/v1/search'
        params = SearchRequest(query=query, n_results=n_results, period=period).model_dump(exclude_none=True)
        results = await http_post_async(url, data=params)
        return SearchResponse(**results.json())
    
    async def scrape(self, url:str) -> ParsedResponse:
        # curl -X POST "http://localhost:12028/api/v1/scrape" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"url\":\"https://www.bbc.com/news/world-europe-60575619\"}"
        
        url = 'http://localhost:12028/api/v1/scrape'
        params = ScrapeRequest(url=url).model_dump(exclude_none=True)
        results = await http_post_async(url, data=params)
        return results.json()