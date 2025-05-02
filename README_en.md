# MCP Websearch

MCP Websearch is a web search and content extraction tool based on MCP (Model Context Protocol), which supports direct invocation of web search functions by AI tools such as Claude that support MCP. This tool integrates multiple search engines, has the ability to bypass anti-crawling mechanisms, and is suitable for automated data collection scenarios.

## ✨ Features

- **Multi-engine support**: Integrates mainstream search engines such as DuckDuckGo (DDGS), Bing, Google, and Baidu.
- **Zero API dependency**: Directly scrapes search engine results without the need to configure API keys.
- **Smart anti-crawling**: Built-in request frequency control and browser feature simulation (e.g., User-Agent rotation).
- **Content extraction**: Supports multi-dimensional data extraction, including webpage content, metadata, and raw HTML.
- **Multi-language adaptation**: Perfectly supports search results in Chinese and English, with automatic recognition of webpage encoding.
- **AI-friendly**: Data return format designed specifically for AI tools such as Claude (using Pydantic Models).

## 🚀 Quick Installation

### Environment Requirements

- Python 3.11+
- Playwright (for automatic browser management)

### Clone the Repository

```bash
# Clone the repository
git clone https://github.com/wdndev/mcp_websearch.git
cd mcp_websearch

# Install UV package manager (cross-platform)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/macOS
# Or for Windows PowerShell:
irm https://astral.sh/uv/install.ps1 | iex

# Create a virtual environment and install dependencies
uv venv --python 3.11
uv sync

# Install dependencies
playwright install
```

## 🛠 Usage Guide

### Activate Environment

```bash
# Linux & MAC
source .venv/bin/activate

# Windows
./.venv/Scripts/activate
```

### MCP Service Configuration

1. Locate the MCP configuration file (e.g., `.cursor/mcp.json`).
2. Add server configuration:
```json
{
    "mcpServers": {
        "web_search": {
            "name": "MCP Websearch Service",
            "type": "stdio",
            "description": "Web search and content extraction service",
            "command": "uv",
            "args": [
            "--directory",
            "/<absolute-path>/mcp_websearch",
            "run",
            "search_server.py"
            ]
        },
    },
}
```
3. Now you can use the `fetch_web_data_from_url`, `search_web_data_from_query`, and `fetch_web_data_from_query` tools in the MCP client.

## Supported Tools

### search_web_data_from_query

Retrieve web content based on user query. Supported search engines: ddgs, bing, baidu, google.

Parameters:
- query: User query
- num_results: Number of web content results to retrieve (default is 5)
- search_type: Search type (options: ddgs, bing, baidu, google)

Return value: List of `WebSearchResult` objects

```bash
[
    WebSearchResult(
        url: str
        title: Optional[str] = None
        position: Optional[int] = None
        description: Optional[str] = None
        metadata: Optional[Any] = None
    )
]
```

### fetch_web_data_from_url

Retrieve web content based on user URL.

Parameters:
- url: User URL

Return value: `WebScrapeResult` object

```bash
WebScrapeResult(
    title: str,
    url: str,
    text: str,
    html: Optional[str],
    source: Optional[str]
)
```

### fetch_web_data_from_query

Retrieve web content based on user query. Supported search engines: ddgs, bing, baidu, google.

Parameters:
- query: User query
- num_results: Number of web content results to retrieve (default is 5)
- search_type: Search type (options: ddgs, bing, baidu, google)

Return value: List of `WebScrapeResult` objects

```python
[
    WebScrapeResult(
        title: str,
        url: str,
        text: str,
        html: Optional[str],
        source: Optional[str]
    )
]
```

## Notes

1. **Anti-crawling strategy**:
   - If encountering anti-crawling mechanisms, you can try:
        - Switching search engine types
        - Reducing the number of concurrent requests
        - Enabling Playwright rendering mode in the configuration
2. **Legal use**:
    - This tool is only for legitimate data collection scenarios.
    - Please comply with the robots.txt protocols of each search engine.
    - Do not use for commercial data scraping or other unauthorized purposes.

3. **Performance suggestions**:
    - It is recommended to use the DDGS engine for real-time data.
    - For batch collection, it is advisable to set a request interval of 2-3 seconds.
    - For dynamic web pages, it is recommended to enable HTML caching.

## License

MIT

