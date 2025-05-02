import asyncio
from duckduckgo_search import DDGS
from typing import List, Optional, Dict, Any

from .base_search import BaseSearchEngine, SearchResult
from loguru import logger

class DdgsSearchEngine(BaseSearchEngine):
    def __init__(
        self, 
        proxy: Optional[str] = None,
        region: str = 'cn-zh',
    ):
        super().__init__(proxy)
        self.ddgs = DDGS(proxy=proxy)
        self.region = region

    async def search(
        self, 
        query: str, 
        num_results: int = 10,
        **kwargs
    ) -> List[SearchResult]:
        """ 使用 DDGS 搜索
        """
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, 
                lambda:list(self.ddgs.text(query, region=self.region, max_results=num_results))
            )

            # 转换格式
            search_results = []

            for i, result in enumerate(results):
                search_results.append(
                    SearchResult(
                        title=result.get("title", ""),
                        url=result.get("href", ""),
                        description=result.get("body", ""),
                        position=i + 1,
                        metadata=result,
                    )
                )

            return search_results
        
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return []
        