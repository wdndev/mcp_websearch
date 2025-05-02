import asyncio
from typing import Optional, Dict, Union, List

from loguru import logger

from .websearch.base_search import SearchResult, BaseSearchEngine
from .websearch.ddgs_search import DdgsSearchEngine
from .scraper.base_scraper import BaseScraper, ScrapedContent
from .scraper.playwright_scraper import PlaywrightScraper

class SearchAndScrapeManager:
    """ 搜索和爬虫管理器
    """
    def __init__(
        self,
        search_engine: BaseSearchEngine = None,
        scraper: BaseScraper = None,
        **kwargs
    ):
        self.search_engine = search_engine or DdgsSearchEngine(**kwargs)
        self.scraper = scraper or PlaywrightScraper(**kwargs)

    async def setup(self) -> None:
        """ 初始化搜索引擎和爬虫
        """
        if hasattr(self.scraper, "setup"):
            await self.scraper.setup()
    
    async def teardown(self):
        """ 清理资源
        """
        if hasattr(self.scraper, "teardown"):
            await self.scraper.teardown()

    async def search(
        self, 
        query: str, 
        num_results: int = 10, 
        **kwargs
    ) -> List[SearchResult]:
        """ 搜索
        """
        return await self.search_engine.search(query, num_results, **kwargs)

    async def scrape(self, url: str, **kwargs) -> ScrapedContent:
        """ 爬取网页内容
        """
        return await self.scraper.scrape(url, **kwargs)
    
    async def search_and_scrape(
        self, 
        query: str, 
        num_results: int = 10, 
        scrape_all: bool = True,
        max_concurrent_scrapes: int = 5,
        **kwargs
    ) -> Dict[str, Union[List[SearchResult], Dict[str, ScrapedContent]]]:
        """ 搜索网页并爬取内容
        Args:
            - query: 搜索查询字符串
            - num_results: 最大搜索结果数量
            - scrape_all: 是否爬取所有搜索结果
            - max_concurrent_scrapes: 最大并发爬取数量
            - kwargs: 其他参数
        Returns:
            - List[ScrapedContent]: 爬取的网页内容列表
        """
        # 搜索
        search_results = await self.search(query, num_results, **kwargs)

        scraped_contents = {}

        # 爬取搜索结果
        if scrape_all and search_results:
            # 限制并发爬取数量
            semaphore = asyncio.Semaphore(max_concurrent_scrapes)

            async def scrape_with_semaphore(url):
                async with semaphore:
                    return await self.scrape(url, **kwargs)

            scrape_tasks = [
                scrape_with_semaphore(result.url) for result in search_results
            ]
            # 执行爬取任务
            scraped_results = await asyncio.gather(
                *scrape_tasks, return_exceptions=True
            )

            # 处理结果
            for i, result in enumerate(scraped_results):
                if isinstance(result, Exception):
                    logger.error(f"Error scraping result {i+1}: {str(result)}")
                    continue

                scraped_contents[search_results[i].url] = result

        return {
            "search_results": search_results,
            "scraped_contents": scraped_contents,
        }
            
