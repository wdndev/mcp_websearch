from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

@dataclass
class ScrapedContent:
    """ 标准化的爬虫内容类
    """
    url: str
    html: str
    title: str
    text: str
    status_code: int
    metadata: Dict[str, Any] = None

class BaseScraper(ABC):
    """ 爬虫类
    """

    @abstractmethod
    async def setup(self) -> None:
        """ 初始化爬虫
        """
        pass

    @abstractmethod
    async def teardown(self) -> None:
        """ 关闭爬虫
        """
        pass

    @abstractmethod
    async def scrape(self, url: str, **kwargs) -> Optional[ScrapedContent]:
        """ 爬取网页内容
        """
        pass

