# File: desync_search/core.py

import requests
import json
import time
from desync_search.data_structures import PageData  # or .core if you keep them in same file
import uuid


API_VERSION = "v0.2.13"

class DesyncClient:
    """
    A high-level client for the Desync Search API.
    This handles search (stealth/test), retrieving previously collected search data,
    and pulling the user's credit balance.
    """

    def __init__(self, user_api_key, developer_mode=False):
        """
        Initialize the client with a user_api_key.
        The base URL is fixed to the current production endpoint.
        """
        self.user_api_key = user_api_key
        if developer_mode:
            self.base_url = "https://prku2ngdahnemmpibutatfr6zm0jazmb.lambda-url.us-east-1.on.aws/"
        else:
            self.base_url = "https://nycv5sx75joaxnzdkgvpx5mcme0butbo.lambda-url.us-east-1.on.aws/"


    def search(
        self,
        url,
        search_type="stealth_search",
        scrape_full_html=False,
        remove_link_duplicates=True
    ) -> PageData:
        """
        Performs a search. By default, does a 'stealth_search' (cost: 10 credits),
        but you can supply 'test_search' for a cheaper test operation (cost: 1 credit).

        :param url: The URL to scrape.
        :param search_type: Either "stealth_search" (default) or "test_search".
        :param scrape_full_html: If True, returns full HTML. Default False.
        :param remove_link_duplicates: If True, deduplicate discovered links. Default True.

        :return: A single PageData object representing the newly scraped page record.
                 Raises RuntimeError if the API returns success=False or on HTTP error.
        """
        payload = {
            "user_api_key": self.user_api_key,
            "timestamp": int(time.time()),
            "operation": "search",
            "flags": {
                "search_type": search_type,
                "target_list": [url],
                "scrape_full_html": scrape_full_html,
                "remove_link_duplicates": remove_link_duplicates
            },
            "metadata": {
                "api_version": API_VERSION
            }
        }
        resp = self._post_and_parse(payload)  # a dict with "data" inside
        # Typically: {"success": True, "data": {...}}
        data_dict = resp.get("data", {})
        return PageData.from_dict(data_dict)

    def bulk_search(
        self,
        target_list,
        extract_html=False
    ) -> dict:
        """
        Initiates a "bulk_search" operation on the Desync API, which:
        1) Checks if user_api_key has enough credits (10 credits/URL).
        2) Charges them in one shot.
        3) Invokes a Step Functions workflow to asynchronously handle all links.

        :param target_list: A list of URLs to process in this bulk search.
        :param bulk_search_id: An optional string to identify this bulk job.
        :param extract_html: If True, includes HTML in the scraper. Default False.

        :return: A dict with keys such as:
            {
            "message": "Bulk search triggered successfully.",
            "bulk_search_id": "...",
            "total_links": 25,
            "cost_charged": 250,
            "execution_arn": "arn:aws:states:..."
            }
        Raises RuntimeError if the API returns success=False or if there's an HTTP error.
        """
        if not isinstance(target_list, list) or len(target_list) == 0:
            raise ValueError("bulk_search requires a non-empty list of URLs.")
        bulk_search_id = uuid.uuid4()
        payload = {
            "user_api_key": self.user_api_key,
            "timestamp": int(time.time()),
            "operation": "bulk_search",
            "flags": {
                "target_list": target_list,
                "bulk_search_id": str(bulk_search_id),
                "extract_html": extract_html
            },
            "metadata": {
                "api_version": API_VERSION
            }
        }

        resp = self._post_and_parse(payload)  # e.g. { "success": True, "data": {...} }
        # 'resp["data"]' might look like:
        # {
        #   "message": "Bulk search triggered successfully.",
        #   "bulk_search_id": "...",
        #   "total_links": 25,
        #   "cost_charged": 250,
        #   "execution_arn": "arn:aws:states:..."
        # }

        data_dict = resp.get("data", {})
        data_dict["bulk_search_id"] = str(bulk_search_id)
        return data_dict


    def list_available(self, url_list=None, bulk_search_id=None) -> list:
        """
        Lists minimal data about previously collected search results (IDs, domain, timestamps, etc.).
        Returns a list of PageData objects (with limited fields).
        
        :param url_list: An optional list of URLs to filter by.
        :param bulk_search_id: An optional bulk search ID to filter by.
        :return: A list of PageData objects containing minimal record fields.
        """
        payload = {
            "user_api_key": self.user_api_key,
            "timestamp": int(time.time()),
            "operation": "retrieval",
            "flags": {
                "retrieval_type": "list_available"
            },
            "metadata": {
                "api_version": API_VERSION
            }
        }

        # If the caller wants to filter by one or more URLs, pass that list along:
        if url_list is not None and isinstance(url_list, list) and len(url_list) > 0:
            payload["flags"]["url_list"] = url_list

        # If the caller wants to filter by bulk_search_id, pass it along:
        if bulk_search_id is not None:
            payload["flags"]["bulk_search_id"] = bulk_search_id

        resp = self._post_and_parse(payload)  # e.g. {"success": True, "data": [ {...}, {...} ]}
        data_list = resp.get("data", [])

        return [PageData.from_dict(item) for item in data_list]


    def pull_data(self, 
                  record_id=None, 
                  url=None, 
                  domain=None, 
                  timestamp=None, 
                  bulk_search_id=None, 
                  search_type=None, 
                  latency_ms=None, 
                  complete=None, 
                  created_at=None) -> list:
        """
        Pulls full data for one or more records (including text_content, html_content, etc.).
        :param record_id: Filter by specific record ID.
        :param url_filter: (Optional) If you want to filter by 'url' instead.
        :return: A list of PageData objects, in case multiple records match the filters.
        """
        flags = {
            "retrieval_type": "pull"
        }
        if record_id is not None:
            flags["id"] = record_id
        if url is not None:
            flags["url"] = url
        if domain is not None:
            flags["domain"] = domain
        if timestamp is not None:
            flags["timestamp"] = timestamp
        if bulk_search_id is not None:
            flags["bulk_search_id"] = bulk_search_id
        if search_type is not None:
            flags["search_type"] = search_type
        if latency_ms is not None:
            flags["latency_ms"] = latency_ms
        if complete is not None:
            flags["complete"] = complete
        if created_at is not None:
            flags["created_at"] = created_at

        payload = {
            "user_api_key": self.user_api_key,
            "timestamp": int(time.time()),
            "operation": "retrieval",
            "flags": flags,
            "metadata": {
                "api_version": API_VERSION
            }
        }
        resp = self._post_and_parse(payload)
        # resp["data"] is a list of dict
        data_list = resp.get("data", [])
        return [PageData.from_dict(d) for d in data_list]

    def pull_credits_balance(self) -> dict:
        """
        Checks the user's own credit balance.
        Returns a dict: e.g. {"success": True, "credits_balance": 240}
        """
        payload = {
            "user_api_key": self.user_api_key,
            "timestamp": int(time.time()),
            "operation": "retrieval",
            "flags": {
                "retrieval_type": "pull_credits_balance"
            },
            "metadata": {
                "api_version": API_VERSION
            }
        }
        return self._post_and_parse(payload)  # e.g. { "success": True, "credits_balance": 240 }

    def _post_and_parse(self, payload):
        """
        Internal helper to POST the payload to self.base_url, parse JSON,
        and raise RuntimeError if success=False or there's an HTTP error.
        """
        try:
            resp = requests.post(self.base_url, json=payload, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("success", False):
                raise RuntimeError(
                    data.get("error", "Unknown error from API"),
                    data
                )
            return data
        except requests.RequestException as e:
            raise RuntimeError(f"HTTP error: {e}")
