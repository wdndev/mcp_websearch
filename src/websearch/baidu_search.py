import asyncio
from baidusearch.baidusearch import search
from typing import List, Optional, Dict, Any

from .base_search import BaseSearchEngine, SearchResult
from loguru import logger

class BaiduSearchEngine(BaseSearchEngine):

    async def search(
        self, 
        query, 
        num_results = 10, 
        **kwargs
    ) -> List[SearchResult]:
        """ 使用百度搜索
        """
        try:
            loop = asyncio.get_event_loop()
            raw_results = await loop.run_in_executor(
                None,
                lambda:list(search(query, num_results=num_results))
            )

            results = []
            for i, item in enumerate(raw_results):
                if isinstance(item, str):
                    results.append(
                        SearchResult(
                            title="",
                            url=item,
                            description="",
                            position=i + 1,
                            metadata={}
                        )
                    )
                elif isinstance(item, dict):
                    results.append(
                        SearchResult(
                            title=item.get("title", ""),
                            url=item.get("url", ""),
                            description=item.get("abstract", ""),
                            position=i + 1,
                            metadata=item,
                        )
                    )
                else:
                    try:
                        results.append(
                            SearchResult(
                                title=item.get("title", ""),
                                url=item.get("url", ""),
                                description=item.get("abstract", ""),
                                position=i + 1,
                                metadata=item,
                            )
                        )
                    except Exception as e:
                        # Fallback to a basic result
                        results.append(
                            SearchResult(
                                url=str(item), 
                            )
                    )

            return results
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return []



