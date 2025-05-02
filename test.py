import os
import requests
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from dotenv import load_dotenv
from loguru import logger
import asyncio

from mcp.server.fastmcp import Context, FastMCP

from src.websearch.base_search import SearchResult, BaseSearchEngine
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
    """Search result type.
    """
    title: Optional[str] = None
    url: str
    text: str
    html: Optional[str] = None
    source: Optional[str] = None

@dataclass
class MCPContext:
    scraper_cxt: PlaywrightScraper

@asynccontextmanager
async def mcp_lifespan(server: FastMCP) -> AsyncIterator[MCPContext]:
    """ MCP Lifecycle Manager
    """
    try:
        scraper_cxt = PlaywrightScraper(
            headless= True,
            browser_type= "chromium"
        )

        # 进入服务
        yield MCPContext(
            scraper_cxt=scraper_cxt
        )
    except Exception as e:
        print(f"Initialization failed: {str(e)}")
        raise
    finally:
        print("Clean up resources")

mcp = FastMCP(
    name="Web Data Scraping Tools",
    instructions="""No API KEY is required; you can use a web data scraping tool directly.
    This tool can scrape data from web pages and convert it into clean text, making it convenient for further processing and analysis.
    """,
    lifespan=mcp_lifespan
)

def get_search_engine(search_type: SearchEngineType) -> BaseSearchEngine:
    """Get search engine based on type.
    """
    if search_type == SearchEngineType.BING:
        return BingSearchEngine()
    elif search_type == SearchEngineType.BAIDU:
        return BaiduSearchEngine()
    elif search_type == SearchEngineType.GOOGLE:
        return GoogleSearchEngine()
    else:
        return DdgsSearchEngine()

@mcp.tool(
    name="scrape_web_data_from_url", 
    description="Scrape web data from URL"
)
async def scrape_web_data_from_url(
    url: str, 
    ctx: Context=None) -> WebSearchResult:
    """Scrape web data from URL
    :param url: The URL to scrape data from
    :param ctx: The context object
    :return: The scraped data as a string
    """
    try:
        scraper_cxt = ctx.request_context.lifespan_context.scraper_cxt
        scraped_result = await scraper_cxt.scrape(url)
        title = scraped_result.metadata.get("title", "")
        text = scraped_result.text
        print("wwwwwwwwww: ", text)
        html = scraped_result.html

    except Exception as e:
        logger.error(f"Error scraping web data from URL: {e}")
        text = f"Error scraping web data from URL: {e}"
        title = None
        html = None

    return WebSearchResult(
        url = url,
        title = title,
        text = text,
        html = html,
        source = "scraped_web_page"
    )

async def main():
    url = "https://baike.baidu.com/item/%E6%A8%A1%E5%9E%8B%E4%B8%8A%E4%B8%8B%E6%96%87%E5%8D%8F%E8%AE%AE/65540618"
    scraper_cxt =  PlaywrightScraper(
        headless= True,
        browser_type= "chromium"
    )
    scraped_result = await scraper_cxt.scrape(url)
    title = scraped_result.metadata.get("title", "")
    text = scraped_result.text
    print("wwwwwwwwww: ", text)
    html = scraped_result.html


if __name__ == '__main__':
    # main()
    asyncio.run(main())

