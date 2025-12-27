"""
Web search tools for gathering information from the internet.

This module provides a unified interface for multiple search providers:
- DuckDuckGo (free, no API key required)
- Tavily (AI-optimized, requires API key)
- Serper (Google results, requires API key)
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from src.graph.state import SearchResult
from src.config.settings import settings


class SearchProvider:
    """
    Unified search interface supporting multiple search backends.

    This class provides a consistent API for searching across different
    search providers. DuckDuckGo is used as the default free option.
    """

    def __init__(
        self,
        provider_type: Optional[str] = None,
        api_key: Optional[str] = None,
        max_results: int = 5
    ):
        """
        Initialize the search provider.

        Args:
            provider_type: Type of provider ('duckduckgo', 'tavily', 'serper')
                          If None, uses settings.search_provider
            api_key: API key for the provider (required for tavily and serper)
                    If None, uses settings.search_api_key
            max_results: Maximum number of results to return per query

        Example:
            >>> provider = SearchProvider("duckduckgo")
            >>> results = provider.search("AI in healthcare")
        """
        self.provider_type = provider_type or settings.search_provider
        self.api_key = api_key or settings.search_api_key
        self.max_results = max_results or settings.max_search_results_per_query

        # Validate configuration
        if self.provider_type in ["tavily", "serper"] and not self.api_key:
            raise ValueError(
                f"{self.provider_type} requires an API key. "
                "Set SEARCH_API_KEY in .env or pass api_key parameter."
            )

    def search(
        self,
        query: str,
        max_results: Optional[int] = None
    ) -> List[SearchResult]:
        """
        Execute a search query.

        Args:
            query: The search query string
            max_results: Override default max_results for this query

        Returns:
            List of SearchResult dictionaries

        Example:
            >>> provider = SearchProvider()
            >>> results = provider.search("Python async programming", max_results=3)
            >>> for result in results:
            ...     print(result["title"])
        """
        num_results = max_results or self.max_results

        if self.provider_type == "duckduckgo":
            return self._search_duckduckgo(query, num_results)
        elif self.provider_type == "tavily":
            return self._search_tavily(query, num_results)
        elif self.provider_type == "serper":
            return self._search_serper(query, num_results)
        else:
            raise ValueError(f"Unknown search provider: {self.provider_type}")

    def _search_duckduckgo(self, query: str, max_results: int) -> List[SearchResult]:
        """
        Search using DuckDuckGo (free, no API key required).

        This is the default search provider as it requires no authentication.
        """
        try:
            from duckduckgo_search import DDGS

            results = []
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=max_results)

                for idx, result in enumerate(search_results):
                    if idx >= max_results:
                        break

                    search_result = SearchResult(
                        title=result.get("title", ""),
                        url=result.get("href", ""),
                        snippet=result.get("body", ""),
                        relevance_score=None,  # DuckDuckGo doesn't provide scores
                        source="duckduckgo"
                    )
                    results.append(search_result)

            return results

        except ImportError:
            print("Warning: duckduckgo-search not installed. Install with: pip install duckduckgo-search")
            return []
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []

    def _search_tavily(self, query: str, max_results: int) -> List[SearchResult]:
        """
        Search using Tavily API (AI-optimized search, requires API key).

        Tavily provides AI-optimized search results specifically designed
        for LLM applications.
        """
        try:
            import requests

            url = "https://api.tavily.com/search"
            headers = {"Content-Type": "application/json"}
            payload = {
                "api_key": self.api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": "basic",
                "include_answer": False,
                "include_raw_content": False
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get("results", [])[:max_results]:
                search_result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("content", ""),
                    relevance_score=item.get("score"),
                    source="tavily"
                )
                results.append(search_result)

            return results

        except ImportError:
            print("Warning: requests library not installed. Install with: pip install requests")
            return []
        except Exception as e:
            print(f"Tavily search error: {e}")
            return []

    def _search_serper(self, query: str, max_results: int) -> List[SearchResult]:
        """
        Search using Serper API (Google results, requires API key).

        Serper provides access to Google search results through an API.
        """
        try:
            import requests

            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "num": max_results
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get("organic", [])[:max_results]:
                search_result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    relevance_score=None,  # Serper doesn't provide explicit scores
                    source="serper"
                )
                results.append(search_result)

            return results

        except ImportError:
            print("Warning: requests library not installed. Install with: pip install requests")
            return []
        except Exception as e:
            print(f"Serper search error: {e}")
            return []

    def test_connection(self) -> bool:
        """
        Test if the search provider is accessible and working.

        Returns:
            True if search works, False otherwise

        Example:
            >>> provider = SearchProvider()
            >>> if provider.test_connection():
            ...     print("Search is working!")
        """
        try:
            results = self.search("test query", max_results=1)
            return len(results) > 0
        except Exception as e:
            print(f"Search connection test failed: {e}")
            return False


def search_multiple_queries(
    queries: List[str],
    provider: Optional[SearchProvider] = None,
    max_results_per_query: int = 5
) -> Dict[str, List[SearchResult]]:
    """
    Execute multiple search queries and organize results.

    Args:
        queries: List of search query strings
        provider: SearchProvider instance (creates default if None)
        max_results_per_query: Maximum results per query

    Returns:
        Dictionary mapping query to list of SearchResults

    Example:
        >>> queries = ["AI healthcare", "machine learning diagnosis"]
        >>> results = search_multiple_queries(queries, max_results_per_query=3)
        >>> for query, search_results in results.items():
        ...     print(f"{query}: {len(search_results)} results")
    """
    if provider is None:
        provider = SearchProvider(max_results=max_results_per_query)

    results_by_query = {}

    for query in queries:
        try:
            results = provider.search(query, max_results=max_results_per_query)
            results_by_query[query] = results
        except Exception as e:
            print(f"Error searching for '{query}': {e}")
            results_by_query[query] = []

    return results_by_query


def deduplicate_results(
    results: List[SearchResult],
    by: str = "url"
) -> List[SearchResult]:
    """
    Remove duplicate search results.

    Args:
        results: List of SearchResult dictionaries
        by: Field to deduplicate by ('url' or 'title')

    Returns:
        Deduplicated list of SearchResults

    Example:
        >>> results = search_multiple_queries(["AI", "artificial intelligence"])
        >>> all_results = []
        >>> for r in results.values():
        ...     all_results.extend(r)
        >>> unique_results = deduplicate_results(all_results)
    """
    seen = set()
    unique_results = []

    for result in results:
        key = result.get(by, "")
        if key and key not in seen:
            seen.add(key)
            unique_results.append(result)

    return unique_results
