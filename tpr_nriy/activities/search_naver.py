import os
import re
import html
import httpx
from typing import List, Dict, Any
from temporalio import activity

@activity.defn
async def search_naver(type: str, keyword: str) -> str:
    """
    Searches content using Naver API.
    
    Args:
        type: Search type (news, blog, web)
        keyword: Search keyword
    
    Returns:
        str: Formatted search results
    """
    # API endpoint and headers
    url = f"https://openapi.naver.com/v1/search/{type}.json"
    headers = {
        "X-Naver-Client-Id": os.environ["NAVER_CLIENT_ID"],
        "X-Naver-Client-Secret": os.environ["NAVER_CLIENT_SECRET"]
    }
    params = {
        "query": keyword,
        "display": 20
    }
    
    # Make API request
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code == 200:
            result = response.json()
        else:
            activity.logger.error(f"Error: {response.status_code}, {response.text}")
            response.raise_for_status()
    
    # Process results
    items = result.get("items", [])
    processed_items = [
        {
            "title": item["title"],
            "description": item["description"]
        }
        for item in items
    ]
    
    # Format results
    context_str = ""
    for item in processed_items:
        context_str += f"- title: {item['title']}\n"
        context_str += f"  description: {item['description']}\n"
    
    # Clean up HTML tags and entities
    context_str = re.sub(r"<[^>]+>", "", context_str)
    context_str = html.unescape(context_str)

    return context_str 