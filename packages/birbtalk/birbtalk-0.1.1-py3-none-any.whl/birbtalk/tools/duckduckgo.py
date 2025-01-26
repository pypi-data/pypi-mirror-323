import os
from duckduckgo_search import DDGS
from ..models import BirbTool

PROXY = os.getenv("PROXY")
MAX_RESULTS = os.getenv("MAX_SEARCH_RESULTS")
if not MAX_RESULTS: MAX_RESULTS = 5

def duckduckgo(query: str, **kwargs):
    # Search
    try:
        ddgs = DDGS(proxy=PROXY.replace("socks5", "socks5h") if PROXY else None)
        results = ddgs.text(query, region='wt-wt', safesearch='off', timelimit='y', max_results=MAX_RESULTS)
    except:
        return "Nothing found!"
    # Format texts
    texts = []
    for x in results:
        texts.append(f'Title: {x["title"]}\nSource: [{x["href"]}]({x["href"]})\nText: {x["body"]}')
    return "\n\n".join(texts)

DuckDuckGoTool = BirbTool(
    name = "web_search",
    description = "Search for information on the web",
    function = duckduckgo,
    arguments = {
        "query": {
            "type": "string",
            "description": "Short query for search engine that reflects the user's intentions. Should be rich with keywords."
        }
    },
    required = ["query"]
)
