from gai.lib.common.http_utils import http_post_async
class SeleniumClient:
    
    async def google(self, query:str, n_results:int=10, period=None):
        url = 'http://localhost:12028/api/v1/googler'
        params = {
            'query': query,
            'n_results': n_results
        }
        results = await http_post_async(url, data=params)
        return results
