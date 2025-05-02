import asyncio
from googlesearch import search
from typing import List, Optional, Dict, Any

from .base_search import BaseSearchEngine, SearchResult
from loguru import logger

class GoogleSearchEngine(BaseSearchEngine):
    def __init__(
        self, 
        proxy: Optional[str] = None,
        lang: str = 'zh-CN',
    ):
        super().__init__(proxy)
        self.lang = lang

    async def search(
        self, 
        query, 
        num_results = 10, 
        **kwargs
    ) -> List[SearchResult]:
        """ 使用Google搜索
        """
        try:
            loop = asyncio.get_event_loop()
            raw_results = await loop.run_in_executor(
                None,
                lambda:list(search(
                    query, 
                    num_results=num_results, 
                    advanced=True,
                    proxy=self.proxy,
                    lang=self.lang
                ))
            )

            results = []
            for i, item in enumerate(raw_results):
                if isinstance(item, str):
                    results.append(
                        SearchResult(
                            title="",
                            url=item,
                            description="",
                            position=i + 1
                        )
                    )
                else:
                    results.append(
                        SearchResult(
                            title=item.title,
                            url=item.url,
                            description=item.description,
                            position=i + 1
                        )
                    )

            return results
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return []



