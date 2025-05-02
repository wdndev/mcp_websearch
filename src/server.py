import asyncio
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Literal

from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel, Field
from mcp.server.fastmcp import Context, FastMCP

from src.websearch.base_search import BaseSearchEngine
from src.websearch.baidu_search import BaiduSearchEngine
from src.websearch.bing_search import BingSearchEngine
from src.websearch.ddgs_search import DdgsSearchEngine
from src.websearch.google_search import GoogleSearchEngine
from src.scraper.base_scraper import BaseScraper
from src.scraper.playwright_scraper import PlaywrightScraper

load_dotenv()

class SearchEngineType(Enum):
    """Search services type.
    """
    DDGS = "ddgs"
    BING = "bing"
    BAIDU = "baidu"
    GOOGLE = "google"

class WebSearchResult(BaseModel):
    """Data model representing a web search result.
    """
    title: Optional[str] = None
    url: str = Field(..., description="The URL of the search result")
    text: str = Field(..., description="Extracted text content from the page")
    html: Optional[str] = Field(None, description="Raw HTML content of the page")
    source: Optional[str] = Field(None, description="Search engine used for this result")

@dataclass
class MCPContext:
    """Context container for maintaining scraper instances."""
    scraper_cxt: PlaywrightScraper

@asynccontextmanager
async def mcp_lifespan(server: FastMCP) -> AsyncIterator[MCPContext]:
    """ MCP Lifecycle Manager
    """
    scraper_cxt = None
    try:
        scraper_cxt = PlaywrightScraper(
            headless= True,
            browser_type= "chromium"
        )

        logger.info("Service initialization completed")
        yield MCPContext(
            scraper_cxt=scraper_cxt
        )
    except Exception as e:
        print(f"Initialization failed: {str(e)}")
        raise
    finally:
        if scraper_cxt:
            await scraper_cxt.teardown()
        logger.info("Resources cleaned up successfully")

mcp = FastMCP(
    name="Web Data Scraping Tools",
    instructions="""No API keys required. Provides direct access to web scraping capabilities.
    Converts web page content into clean text for easy processing and analysis.""",
    lifespan=mcp_lifespan
)

_ENGINE_MAP = {
    "bing": BingSearchEngine,
    "baidu": BaiduSearchEngine,
    "google": GoogleSearchEngine,
    "ddgs": DdgsSearchEngine
}

def get_search_engine(search_type: str) -> BaseSearchEngine:
    """Factory function for creating search engine instances."""
    engine_class = _ENGINE_MAP.get(search_type.lower(), DdgsSearchEngine)
    return engine_class()

@mcp.tool(
    name="scrape_web_data_from_url", 
    description="Scrape web content from a specific URL"
)
async def scrape_web_data_from_url(
    url: str, 
    ctx: Context=None
) -> WebSearchResult:
    """Scrape web data from URL
    :param url: The URL to scrape data from
    :param ctx: The context object
    :return: The scraped data as a string
    """
    try:
        scraper_cxt = ctx.request_context.lifespan_context.scraper_cxt
        result = await scraper_cxt.scrape(url)

        return WebSearchResult(
            url=url,
            title=result.title,
            text=result.text,
            html=result.html,
            source="direct_scrape"
        )

    except Exception as e:
        logger.error(f"Failed to scrape {url}: {str(e)}")
        return WebSearchResult(
            url=url,
            text=f"Scraping error: {str(e)}",
            source="direct_scrape"
        )

@mcp.tool(
    name="scrape_web_data_from_query", 
    description="Search and scrape web content using a search engine. Supports: ddgs, bing, baidu, google"
)
async def scrape_web_data_from_query(
    query: str,
    num_results: int = 5,
    search_type: Literal["ddgs", "bing", "baidu", "google"] = "ddgs",
    max_concurrent_scrapes: int = 3,
    ctx: Context = None
) -> List[WebSearchResult]:
    """ Search and scrape results for a given query using specified search engine.
    :param query: The search query
    :param num_results: The number of search results to retrieve
    :param search_type: The search engine to use
    :param max_concurrent_scrapes: The maximum number of concurrent scrap
    :return: A list of WebSearchResult objectss
    """
    
    search_engine = get_search_engine(search_type)
    search_results = await search_engine.search(query, num_results)
    scraper = ctx.request_context.lifespan_context.scraper_cxt

    results = []
    if not search_results:
        return results
    

    semaphore = asyncio.Semaphore(max_concurrent_scrapes)
    async def safe_scrape(url):
        try:
            async with semaphore:
                return await scraper.scrape(url)
        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {str(e)}")
            return None
    scrape_tasks = [safe_scrape(result.url) for result in search_results]
    scraped_data = await asyncio.gather(*scrape_tasks)

    for search_result, content in zip(search_results, scraped_data):
        if not content:
            continue
            
        results.append(WebSearchResult(
            url=search_result.url,
            title=content.title,
            text=content.text,
            html=content.html,
            source=search_type
        ))

    return results

if __name__ == "__main__":
    mcp.run(transport='stdio')

