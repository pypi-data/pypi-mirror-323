import json
from typing import Annotated

import serpapi
from arcade.sdk import tool

from arcade_search.tools.utils import get_secret


@tool
async def search_google(
    query: Annotated[str, "Search query"],
    n_results: Annotated[int, "Number of results to retrieve"] = 5,
) -> str:
    """Search Google using SerpAPI and return organic search results."""

    api_key = get_secret("SERP_API_KEY")
    if not api_key:
        raise ValueError("SERP_API_KEY is not set")

    client = serpapi.Client(api_key=api_key)
    params = {"engine": "google", "q": query}

    search = client.search(params)
    results = search.as_dict()
    organic_results = results.get("organic_results", [])

    return json.dumps(organic_results[:n_results])
