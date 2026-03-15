# tools/web_search.py
from typing import List, Dict, Any
from langchain_tavily import TavilySearch
from config.settings import TAVIAL_API_KEY


def get_tavily_client() -> TavilySearch:
    # Minimal config; tweak as needed
    return TavilySearch(
        api_key=TAVIAL_API_KEY,
        max_results=5,
        topic="general",
    )


def run_web_search(queries: List[str]) -> List[Dict[str, Any]]:
    """
    Run Tavily search for a list of queries and return merged results.
    """
    client = get_tavily_client()
    results: List[Dict[str, Any]] = []

    for q in queries:
        # TavilySearch.invoke returns a dict with 'results' and other metadata
        res = client.invoke(q)
        # Normalize to a list of results per query
        items = res.get("results") or []
        for item in items:
            results.append(
                {
                    "query": q,
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "content": item.get("content") or item.get("snippet"),
                }
            )

    return results
