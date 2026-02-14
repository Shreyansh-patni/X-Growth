import httpx
from typing import List, Dict, Any, Optional
from app.models.user import User
from app.core import config

class XAPIClient:
    BASE_URL = "https://api.twitter.com/2"

    def __init__(self, user: User):
        self.user = user
        self.headers = {
            "Authorization": f"Bearer {user.access_token}",
            "Content-Type": "application/json"
        }

    async def fetch_home_timeline(self, since_id: Optional[str] = None, max_results: int = 10) -> Dict[str, Any]:
        params = {
            "max_results": max_results,
            "tweet.fields": "id,text,author_id,created_at,conversation_id,public_metrics",
            "expansions": "author_id",
            "user.fields": "username,name"
        }
        if since_id:
            params["since_id"] = since_id

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/users/{self.user.x_user_id}/timelines/reverse_chronological", # V2 endpoint
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()

    async def fetch_list_tweets(self, list_id: str, since_id: Optional[str] = None, max_results: int = 10) -> Dict[str, Any]:
        params = {
            "max_results": max_results,
            "tweet.fields": "id,text,author_id,created_at,conversation_id,public_metrics",
            "expansions": "author_id",
            "user.fields": "username,name"
        }
        if since_id:
            params["since_id"] = since_id
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/lists/{list_id}/tweets",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()

    async def post_reply(self, reply_text: str, reply_to_tweet_id: str) -> Dict[str, Any]:
        payload = {
            "text": reply_text,
            "reply": {
                "in_reply_to_tweet_id": reply_to_tweet_id
            }
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/tweets",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()

    async def search_tweets(self, query: str, since_id: Optional[str] = None, max_results: int = 10) -> Dict[str, Any]:
        """
        Search for recent tweets (last 7 days).
        """
        params = {
            "query": query,
            "max_results": max_results,
            "tweet.fields": "id,text,author_id,created_at,conversation_id,public_metrics",
            "expansions": "author_id",
            "user.fields": "username,name"
        }
        if since_id:
            params["since_id"] = since_id

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/tweets/search/recent",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()

    async def fetch_user_me(self) -> Dict[str, Any]:
        """
        Fetch current user details including metrics.
        """
        params = {
            "user.fields": "public_metrics"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/users/me",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
