# Desync Search — "API to the Internet"

> **Motto**: The easiest way to scrape and retrieve web data **without** aggressive rate limits or heavy detection.

[![PyPI version](https://img.shields.io/pypi/v/desync_search.svg)](https://pypi.org/project/desync_search/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Key Features

- **No Rate Limiting**: We allow you to scale concurrency without punishing usage. You can open many parallel searches; we’ll only throttle if the underlying cloud providers themselves are saturated.
- **Extremely Low Detection Rates**: Our “stealth_search” uses advanced methods for a “human-like” page visit. While we cannot guarantee 100% evasion, **most** websites pass under the radar, and CAPTCHAs—when they do appear—are often circumvented by a second pass.
- **Competitive, Pay-as-You-Go Pricing**: No forced subscriptions or huge minimum monthly costs. You pick how much you spend. Our per-search cost is typically half of what big competitors charge (who often require $1,000+ per month).
- **First 1,000 Searches Free**: Not convinced? **Try** it yourself, risk-free. We’ll spot you 1,000 searches when you sign up. Check out [desync.ai](https://desync.ai/) for more info.

---

## Installation

Install via [PyPI](https://pypi.org/project/desync_search/) using:

```bash
pip install desync_search
```

Because we update often, you may want to run:

```bash
pip install --upgrade desync_search
```

This library requires **Python 3.6+** and **requests** (installed automatically).

---

## Basic Usage

You’ll need a **user API key** (e.g. `"totallynotarealapikeywithactualcreditsonit"`). A best practice is to store that key in an environment variable (e.g., `DESYNC_API_KEY`) to avoid embedding secrets in code:

```bash
export DESYNC_API_KEY="YOUR_ACTUAL_KEY"
```

Then in your Python code:

```python
import os
from desync_search import DesyncClient

user_api_key = os.environ.get("DESYNC_API_KEY", "")
client = DesyncClient(user_api_key)
```

Here, the client automatically targets our **production endpoint**:

```
https://nycv5sx75joaxnzdkgvpx5mcme0butbo.lambda-url.us-east-1.on.aws/
```

> **Tip**: Pass `developer_mode=True` to `DesyncClient(...)` if you want to use a testing endpoint (e.g. staging environment).

---

## Searching for Data

### 1) Single-URL Search

By default, `client.search(...)` does a **stealth search** (cost: 10 credits). If you want a **test search** (cost: 1 credit), pass `search_type="test_search"`.

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

Both calls return a `PageData` object. For stealth, you’ll typically see fields like `.text_content`, `.internal_links`, and `.external_links`.

```python
print(page_data)
# <PageData url=https://www.137ventures.com/portfolio search_type=stealth_search timestamp=... complete=True>

print(page_data.text_content[:200])  # first 200 chars
```

Pass `scrape_full_html=True` to get the entire HTML, or `remove_link_duplicates=False` to keep duplicates:

```python
stealth_response = client.search(
    "https://www.137ventures.com/portfolio",
    scrape_full_html=True,
    remove_link_duplicates=False
)
print(len(stealth_response.html_content), "HTML chars")
```

### 2) Bulk Searching Multiple URLs

If you have a large list of URLs, use **`bulk_search`**. This creates an **asynchronous** job on the server side, which processes each URL in parallel. For each URL, it’s typically **10 credits** (stealth). Example:

```python
from desync_search import DesyncClient

# Suppose you have a list of URLs:
example_urls = [
    "https://www.137ventures.com/", 
    "https://www.137ventures.com/portfolio"
]

client = DesyncClient("YOUR_API_KEY")
response = client.bulk_search(
    target_list=example_urls,
    extract_html=False  # If True, returns HTML in each record
)

print(response)
# e.g. {
#   "message": "Bulk search triggered successfully.",
#   "bulk_search_id": "123e4567-e89b-12d3-a456-426614174000",
#   "total_links": 2,
#   "cost_charged": 20,
#   "execution_arn": "arn:aws:states:..."
# }

bulk_id = response["bulk_search_id"]
print("Bulk job started with ID:", bulk_id)
```

Because the scraping happens asynchronously, you’ll typically wait a few seconds (or more) before the results are fully ready.

#### 2a) Manual Polling

You can do a **manual** check using `list_available` to see if those pages appear (and are marked `complete=True`). For example:

```python
import time

# Wait ~8 seconds, then see if the results are ready
time.sleep(8)
found_records = client.list_available(
    url_list=example_urls,
    bulk_search_id=bulk_id
)

for record in found_records:
    print(record.url, record.complete)
```

Once the pages are ready, you can call `pull_data(bulk_search_id=bulk_id)` to retrieve the **full** text/HTML, etc.

#### 2b) Automated Polling with `collect_results`

We provide a **`collect_results`** method to automate this polling. It will:

1. Check periodically (e.g., every 2 seconds) how many of your URLs are “complete.”
2. If 97.5% (or another fraction you choose) are done, or a certain max wait time expires, it retrieves the **full** data.

```python
bulk_search_resp = client.bulk_search(
    target_list=example_urls,
    extract_html=False
)
bulk_id = bulk_search_resp["bulk_search_id"]

# We'll collect results once ~97.5% are done or 30 seconds pass (whichever first).
records = client.collect_results(
    bulk_search_id=bulk_id,
    target_links=example_urls,  # so it knows how many links to expect
    wait_time=30,               # max seconds to wait
    poll_interval=2,            # check every 2 seconds
    completion_fraction=0.975    # 97.5%
)

print(f"Got {len(records)} pages in final result.")
for page in records:
    print(page.url, page.complete)
```

> **Note**: If the job is very large (hundreds of URLs), consider further chunking or splitting. The library and the API can handle up to 1,000 links at once, but results might take longer.

---

## Retrieving Past Results

### 3) Listing Minimal Data

Use `list_available()` to get minimal data (like IDs, URLs, timestamps) for **all** or a subset of your past searches:

```python
all_records = client.list_available()
print("Found", len(all_records), "total records in the database.")

# Or just for certain URLs or a bulk_search_id:
subset_records = client.list_available(
    url_list=["https://www.137ventures.com/"],
    bulk_search_id="123e4567-e89b-12d3-a456-426614174000"
)
for r in subset_records:
    print(r.id, r.url, r.search_type, r.complete)
```

Each returned item is a `PageData` with limited fields (no large text or HTML) to save bandwidth.

### 4) Pulling Full Details

If you want **all** fields (including `text_content`, `html_content`, etc.), call `pull_data(...)`. You can filter by various parameters such as `record_id`, `url`, or `bulk_search_id`.

```python
# Pull by record_id:
detailed_list = client.pull_data(record_id="your_record_id_here")

# Or by bulk_search_id:
bulk_details = client.pull_data(bulk_search_id="123e4567-e89b-12d3-a456-426614174000")

# Now each item in `detailed_list` or `bulk_details` can have text_content, html_content, etc.
for page in detailed_list:
    print(page.url, len(page.text_content), "chars of text")
```

---

## Checking Your Credits Balance

Use `pull_credits_balance()` to see how many credits remain on your account:

```python
balance_info = client.pull_credits_balance()
print("Credits left:", balance_info.get("credits_balance"))
```

Typical response:

```python
{
  "success": True,
  "credits_balance": 240
}
```

---

## Example: Combine Bulk Search + collect_results

Here’s a short end-to-end script you could run:

```python
from desync_search import DesyncClient

def run_bulk_search_example():
    # 1) Provide your user API key
    my_api_key = "YOUR_ACTUAL_KEY"
    client = DesyncClient(my_api_key)

    # 2) Some URLs to crawl
    example_urls = [
        "https://www.137ventures.com/", 
        "https://www.137ventures.com/portfolio"
    ]

    # 3) Trigger bulk search
    resp = client.bulk_search(target_list=example_urls)
    bulk_id = resp["bulk_search_id"]
    print("Bulk Search Response:", resp)

    # 4) Collect results automatically (poll until 97.5% done or 30s)
    results = client.collect_results(bulk_search_id=bulk_id, target_links=example_urls)
    for page in results:
        print(page.url, page.complete)

    print(f"Total pages retrieved = {len(results)}")

if __name__ == "__main__":
    run_bulk_search_example()
```

This snippet:

1. Initiates a bulk job.
2. Waits for it to become “mostly done” (default `completion_fraction=0.975`).
3. Pulls the **full** data for all those pages in a single retrieval call.

---

## Additional Notes

- **Attribution**: Relies on open-source libraries such as [requests](https://pypi.org/project/requests/).
- **Rate Limits**: We do not impose strict concurrency throttles, but large-scale usage could be slowed if the underlying cloud environment is heavily utilized.
- **First 1,000 Searches**: New accounts start with 1,000 free searches. If you do large-scale crawling, keep an eye on your credit usage.
- **Large Bulk**: For >1,000 URLs, break them into multiple `bulk_search` calls, or contact support for special accommodations.

---

## License

This project is licensed under the MIT License.

---

**Happy scraping** with Desync Search—the next-level “API to the Internet”! Let us know how it goes, and feel free to file issues or pull requests.