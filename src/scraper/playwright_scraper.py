import re
from typing import Optional

from readability import Document
from bs4 import BeautifulSoup

import random
from playwright.async_api import async_playwright, Browser, BrowserContext, TimeoutError

from .base_scraper import BaseScraper, ScrapedContent
from loguru import logger

class PlaywrightScraper(BaseScraper):
    """ 基于 Playwright 的高级网页爬虫，支持反检测功能
    """

    def __init__(
        self,
        headless: bool = True,
        browser_type: str = "chromium",
        user_agent: Optional[str] = None,
        timeout: int = 6000,
    ):
        """
        初始化浏览器配置类。

        参数:
        - headless: 是否以无头模式运行浏览器。默认值为True。
        - browser_type: 浏览器类型，可选值为"chromium"、"firefox"或"webkit"。默认值为"chromium"。
        - user_agent: 用户代理字符串。如果不需要设置用户代理，此参数可省略。
        - timeout: 操作的超时时间，默认为6000毫秒。
        """
        self.headless = headless
        self.browser_type = browser_type.lower()
        self.user_agent = user_agent
        self.timeout = timeout
        self.browser = None         # 浏览器实例
        self.context = None         # 浏览器上下文实例

    async def setup(self):
        """初始化浏览器"""
        # 启动 Playwright 实例
        self.playwright = await async_playwright().start()

        # 动态获取浏览器启动方法（根据 browser_type 选择）
        browser_method = getattr(self.playwright, self.browser_type)

        # 启动浏览器进程（含反检测配置）
        self.browser = await browser_method.launch(
            headless=self.headless,
            # Anti-detection measures
            args=[
                "--no-sandbox",     # 禁用沙箱（部分系统需要）
                "--disable-blink-features=AutomationControlled",    # 隐藏自动化标记
                "--disable-infobars",   # 禁用信息栏
                "--disable-background-timer-throttling",    # 禁止后台限流
                "--disable-backgrounding-occluded-windows", # 禁用窗口遮挡优化
                "--disable-renderer-backgrounding", # 禁止渲染进程后台化
                "--disable-window-activation",      # 禁止窗口激活
                "--disable-focus-on-load",          # 禁止自动聚焦
                "--no-first-run",                   # 跳过首次运行向导
                "--no-default-browser-check",       # 禁用默认浏览器检查
                "--no-startup-window",              # 不显示启动窗口
                "--window-position=0,0",            # 固定窗口位置
                "--disable-notifications",          # 禁用通知
                "--disable-extensions",             # 禁用扩展
                "--mute-audio",                     # 静音音频
            ],
        )
        # 创建浏览器上下文（包含反检测配置）
        self.context = await self.setup_context(self.browser)

        logger.info(
            f"Playwright {self.browser_type} browser initialized in {'headless' if self.headless else 'headed'} mode"
        )

    async def setup_context(self, browser: Browser) -> BrowserContext:
        """
        创建反检测浏览器上下文
        """
        # Common user agents
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        ]

        # 用户代理随机化策略
        selected_user_agent = self.user_agent or random.choice(self.user_agents)

        # 创建浏览器上下文（模拟真实设备）
        context = await browser.new_context(
            user_agent=selected_user_agent,     # 随机用户代理
            accept_downloads=True,              # 接受下载
            ignore_https_errors=True,           # 忽略 HTTPS 错误
            has_touch=random.choice([True, False]),  # 随机触控支持
            locale=random.choice(["en-US", "en-GB", "en-CA"]),  # 随机地区
            timezone_id=random.choice(
                ["America/New_York", "Europe/London", "Asia/Tokyo"]
            ),
            permissions=["geolocation", "notifications"],   # 启用地理定位和通知
            java_script_enabled=True,        # 启用 JavaScript
        )

        # 设置全局超时（影响所有操作）
        context.set_default_timeout(self.timeout)

        # 注入反检测脚本（关键反爬措施）
        await context.add_init_script("""
            // 覆盖自动化检测属性
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // 模拟多语言环境
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en', 'es']
            });

            // 伪造插件列表（Chrome特性）
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    return {
                        length: 5,
                        item: function(index) { return this[index]; },
                        refresh: function() {},
                        0: { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
                        1: { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: 'Portable Document Format' },
                        2: { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' },
                        3: { name: 'Widevine Content Decryption Module', filename: 'widevinecdmadapter.dll', description: 'Enables Widevine licenses for playback of HTML audio/video content.' }
                    };
                }
            });

            // 伪造Chrome内部对象
            window.chrome = {
                runtime: {
                    connect: () => {},
                    sendMessage: () => {}
                },
                webstore: {
                    onInstallStageChanged: {},
                    onDownloadProgress: {}
                },
                app: {
                    isInstalled: false,
                },
                csi: function(){},
                loadTimes: function(){}
            };

            // 绕过权限检测
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );

            // 防止Shadow DOM检测
            (function() {
                const originalAttachShadow = Element.prototype.attachShadow;
                Element.prototype.attachShadow = function attachShadow(options) {
                    return originalAttachShadow.call(this, { ...options, mode: "open" });
                };
            })();

            // 伪造WebGL硬件信息
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris Pro Graphics';
                }
                return getParameter.call(this, parameter);
            };
        """)

        return context

    async def teardown(self):
        """清理浏览器资源
        """
        if self.browser:
            await self.browser.close()
        if hasattr(self, "playwright") and self.playwright:
            await self.playwright.stop()
        logger.info("Playwright resources cleaned up")


    async def _clean_content(self, html: str) -> str:
        """内容净化核心方法"""
        # 第一层：使用Readability提取主体
        doc = Document(html)
        summary = doc.summary()

        # 第二层：BeautifulSoup深度清理
        soup = BeautifulSoup(summary, 'lxml')
        
        # 移除非内容标签
        TAGS_TO_REMOVE = ['nav', 'footer', 'aside', 'header', 'form', 
                        'button', 'iframe', 'noscript', 'style']
        for tag in soup(TAGS_TO_REMOVE):
            tag.decompose()

        # 清除广告特征元素（CSS类名正则匹配）
        AD_PATTERNS = re.compile(r'ad|banner|popup|modal|overlay|promo', re.I)
        for element in soup.find_all(class_=AD_PATTERNS):
            element.decompose()

        # 提取优化后的文本
        text = soup.get_text(separator='\n', strip=True)
        return re.sub(r'\n{3,}', '\n\n', text).strip()

    async def _browser_side_cleanup(self, page):
        """浏览器端预清理策略"""
        # 执行JavaScript移除浮动元素
        await page.evaluate("""
            () => {
                // 移除常见广告选择器
                const selectors = [
                    'div[class*="ad"]', 
                    'iframe[src*="ads"]',
                    'div[id^="banner"]',
                    'div[class*="popup"]'
                ];
                
                selectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(element => {
                        element.remove();
                    });
                });

                // 隐藏cookie提示
                const cookieSelectors = [
                    '#cookie-consent',
                    '.cookie-banner',
                    '#gdpr-modal'
                ];
                
                cookieSelectors.forEach(selector => {
                    const element = document.querySelector(selector);
                    if (element) {
                        element.style.display = 'none';
                    }
                });
            }
        """)

    async def scrape(self, url: str, **kwargs) -> ScrapedContent:
        """执行网页抓取
        """
        if not self.browser:
            await self.setup()

        try:
            # 创建新标签页
            page = await self.context.new_page()

            # 浏览器预清理
            await self._browser_side_cleanup(page)

            # 导航到目标页面（等待网络稳定）
            try:
                response = await page.goto(url, wait_until="networkidle", timeout=self.timeout)
            except TimeoutError:
                logger.warning("网络空闲超时，继续处理已加载内容")
                response = None

            # 获取响应状态码
            status_code = response.status if response else 0

            # 提取页面元数据
            title = await page.title()
            html = await page.content()

            # ------- MOST IMPORTANT COMMENT IN THE REPO -------
            # Extract only user-visible text content from the page
            # This excludes: hidden elements, navigation dropdowns, collapsed accordions,
            # inactive tabs, script/style content, SVG code, HTML comments, and metadata
            # Essentially captures what a human would see when viewing the page
            # text = await page.evaluate("document.body.innerText")

            clean_text = await self._clean_content(html)

            # 关闭当前标签页
            await page.close()

            return ScrapedContent(
                url=url,
                html=html,
                title=title.strip(),
                text=clean_text.strip(),
                status_code=status_code,
                metadata={
                    "headers": response.headers if response else {},
                },
            )

        except Exception as e:
            logger.error(f"抓取失败：{url}: {str(e)}")
            return ScrapedContent(
                url=url, html="", text="", title="", status_code=0, metadata={"error": str(e)}
            )