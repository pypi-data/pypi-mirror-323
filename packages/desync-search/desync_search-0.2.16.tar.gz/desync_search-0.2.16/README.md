# Desync Search — "API to the Internet"

> **Motto**: The easiest way to scrape and retrieve web data **without** aggressive rate limits or heavy detection.

[![PyPI version](https://img.shields.io/pypi/v/desync_search.svg)](https://pypi.org/project/desync_search/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Key Features

- **No Rate Limiting**: We allow you to scale concurrency without punishing usage. You can open many parallel searches; we’ll only throttle if the underlying cloud providers themselves are saturated.  
- **Extremely Low Detection Rates**: Our “stealth_search” uses advanced methods for a “human-like” page visit. While we cannot guarantee 100% evasion, **most** websites pass under the radar, and CAPTCHAs—when they do appear—are often circumvented by a second pass.  
- **Competitive, Pay-as-You-Go Pricing**: No forced subscriptions or huge minimum monthly costs. You pick how much you spend. Our per-search cost is typically half of what big competitors charge (who often require \$1,000+ per month).  
- **First 1,000 Searches Free**: Not convinced? **Try** it yourself, risk-free. We’ll spot you 1,000 searches when you sign up. Check out [desync.ai](https://desync.ai/) for more info.

---

## Installation

Install via [PyPI](https://pypi.org/project/desync_search/) using:

```bash
pip install desync_search
```

This library requires **Python 3.6+** and the **requests** package (installed automatically).

---

## Basic Usage

You’ll need a **user API key** (like `"totallynotarealapikeywithactualcreditsonit"`).  
A best practice is to store that key in an **environment variable** (e.g. `DESYNC_API_KEY`) to avoid embedding secrets in code:

```bash
export DESYNC_API_KEY="YOUR_ACTUAL_KEY"
```

Then in your Python code:

```python
import os
from desync_search.core import DesyncClient

user_api_key = os.environ.get("DESYNC_API_KEY", "")
client = DesyncClient(user_api_key)
```

Here, the client automatically targets our **production endpoint**:  
```
https://nycv5sx75joaxnzdkgvpx5mcme0butbo.lambda-url.us-east-1.on.aws/
```

---

## Searching for Data

### 1) Performing a Search

By default, `search(...)` does a **stealth search** (cost: 10 credits). If you want a **test search** (cost: 1 credit), pass `search_type="test_search"`.

```python
# Stealth Search (default)
page_data = client.search("https://www.137ventures.com/portfolio")

print("URL:", page_data.url)
print("Text length:", len(page_data.text_content))

# Test Search
test_response = client.search(
    "https://www.python.org", 
    search_type="test_search"
)
print("Test search type:", test_response.search_type)
```

Both calls return a **`PageData`** object if `success=True`. For stealth, you’ll typically see fields like `.text_content`, `.internal_links`, and `.external_links`. Example:

```python
print(page_data)
# <PageData url=https://www.137ventures.com/portfolio search_type=stealth_search timestamp=... complete=True>

print(page_data.text_content[:200])  # first 200 chars of text
```

You can pass `scrape_full_html=True` to get the entire HTML, or `remove_link_duplicates=False` to keep duplicates:

```python
stealth_response = client.search(
    "https://www.137ventures.com/portfolio",
    scrape_full_html=True,
    remove_link_duplicates=False
)
print(len(stealth_response.html_content), "HTML chars")
```

### Example: Visit All Internal Links

A simple spider approach: after you search a page, you gather internal links, check which ones you haven’t visited, and recursively fetch them. Example pseudo-code:

```python
visited = set()

def crawl(client, url):
    if url in visited:
        return
    visited.add(url)

    page_data = client.search(url)  # stealth by default
    print("Scraped:", url, "Found", len(page_data.internal_links), "internal links")

    # For each new internal link, crawl again
    for link in page_data.internal_links:
        if link not in visited:
            crawl(client, link)

# Start from a seed URL
crawl(client, "https://www.137ventures.com/portfolio")
```

**Note**: Keep an eye on your credit usage if you do large-scale crawling.

---

## Retrieving Past Results

### 2) Listing Available Results

Use `list_available()` to get minimal data for each past search:

```python
records = client.list_available()
for r in records:
    print(r.id, r.url, r.search_type, r.created_at)
```

Each `r` is a `PageData` with minimal fields (omitting large text/html for bandwidth savings).

### 3) Pulling Detailed Data

If you want **all** fields (including text, HTML, links, etc.), call `pull_data(...)`.  
By default, we show:

```python
# e.g. pull by record_id
details = client.pull_data(record_id=10)
if details:
    first = details[0]
    print(first.url, len(first.text_content), "chars of text")
```

You can also pass a `url_filter` if your library method supports it, e.g.:

```python
details = client.pull_data(url_filter="https://example.org")
```

### 4) Checking Your Credits Balance

Get your **current_credits_balance**:

```python
balance_info = client.pull_credits_balance()
print(balance_info)
# e.g. { "success": true, "credits_balance": 240 }
```

We store the user’s credits on our server, so you can see how many searches remain.

---

## Additional Notes

- **Attribution**: This package relies on open-source libraries like [requests](https://pypi.org/project/requests/).  
- **Rate Limits**: We do not impose user-level concurrency throttles, but large-scale usage could be slowed if the underlying cloud environment is heavily utilized.  
- **Your First 1,000 Searches**: On new accounts, we credit 1,000 searches automatically, so you can test stealth or test calls with zero upfront cost.  
- For more advanced usage (like admin ops, account creation, adding credits) see [desync.ai](https://desync.ai/) or contact support.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

**Happy scraping** with Desync Search—the next-level “API to the Internet”! We look forward to your feedback and contributions.

---
**END README CONTENT**  

Simply **replace** all instances of 
```
with the normal Markdown code fence marker (```) in your local `README.md`. Then your code sections and headers will render properly on GitHub (or similar).