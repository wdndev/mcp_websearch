from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

@dataclass
class SearchResult:
    """搜索结果类
    """
    url: str
    title: Optional[str] = None
    position: Optional[int] = None
    description: Optional[str] = None
    metadata: Optional[Any] = None

class BaseSearchEngine(ABC):
    """搜索引擎基类
    """
    def __init__(self, proxy: Optional[str] = None):
        self.proxy = proxy

    @abstractmethod
    async def search(
        self, 
        query: str, 
        num_results: int = 10,
        **kwargs
    ) -> List[SearchResult]:
        """执行搜索并返回结果列表
        """
        pass

