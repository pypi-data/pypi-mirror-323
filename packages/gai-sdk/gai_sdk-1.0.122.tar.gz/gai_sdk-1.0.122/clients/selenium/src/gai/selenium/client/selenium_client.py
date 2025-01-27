from gai.lib.common.http_utils import http_post_async
from ..dtos.search_dto import SearchRequest, SearchResponse

class SeleniumClient:
    
    async def search(self, query:str, n_results:int=10, period=None) -> SearchResponse:
        # curl -X POST "http://localhost:12028/api/v1/googler" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"query\":\"python\",\"n_results\":5}"
        
        url = 'http://localhost:12028/api/v1/search'
        params = SearchRequest(query=query, n_results=n_results, period=period).model_dump(exclude_none=True)
        results = await http_post_async(url, data=params)
        return SearchResponse(**results)