from playwright.async_api import async_playwright, Page
import asyncio
from typing import List, Optional
import logging
from app.models.tweet import TweetSource
from app.services.tweet_processor import TweetProcessor
from app.models.user import User

logger = logging.getLogger(__name__)

class BrowserMonitor:
    def __init__(self, user: User, processor: TweetProcessor):
        self.user = user
        self.processor = processor
    
    async def login(self, page: Page):
        # This is a critical and sensitive part. 
        # In a real production system, handling 2FA, cookies, and detection avoidance is complex.
        # This is a simplified placeholder for the MVP logic.
        try:
            await page.goto("https://x.com/i/flow/login")
            # Wait for username input
            await page.wait_for_selector("input[autocomplete='username']")
            await page.fill("input[autocomplete='username']", self.user.x_username)
            await page.click("text=Next")
            
            # Wait for password input
            # Note: Sometimes it asks for phone/email verification first
            await page.wait_for_selector("input[name='password']")
            # We need the user's password here. 
            # IMPORTANT: The current User model stores a hashed password for THE APP, 
            # not for X. The user would need to provide X credentials securel, 
            # or we use an invalid placeholder here for the MVP if we don't have them.
            # For now, we assume we might have them or cookies.
            # logger.warning("Browser automation requires X credentials which are not securely stored yet.")
            return False 
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    async def fetch_tweets(self, url: str, source: TweetSource) -> List[dict]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # In a real implementation, we would load cookies/session here
            # isLoggedIn = await self.login(page)
            # if not isLoggedIn:
            #     await browser.close()
            #     return []

            try:
                await page.goto(url)
                await page.wait_for_selector("article[data-testid='tweet']", timeout=10000)
                
                # Scroll to load more
                for _ in range(3):
                    await page.mouse.wheel(0, 500)
                    await asyncio.sleep(2)

                # Extract tweets
                tweets_data = await page.evaluate('''() => {
                    const tweets = Array.from(document.querySelectorAll("article[data-testid='tweet']"));
                    return tweets.map(t => {
                        const textEl = t.querySelector("div[data-testid='tweetText']");
                        const timeEl = t.querySelector("time");
                        const userEl = t.querySelector("div[data-testid='User-Name'] a");
                        const linkEl = t.querySelector("a[href*='/status/']");
                        
                        return {
                            text: textEl ? textEl.innerText : "",
                            created_at: timeEl ? timeEl.getAttribute("datetime") : new Date().toISOString(),
                            author_handle: userEl ? userEl.getAttribute("href").replace("/", "") : "unknown",
                            tweet_id: linkEl ? linkEl.getAttribute("href").split("/status/")[1] : "unknown",
                            url: linkEl ? linkEl.href : ""
                        };
                    });
                }''')

                # Transform to format expected by TweetProcessor
                raw_tweets = {
                    "data": [],
                    "includes": {"users": []}
                }
                
                processed_tweets = []
                for t in tweets_data:
                    if t["tweet_id"] == "unknown": continue
                    
                    # Mocking the structure to fit TweetProcessor
                    raw_item = {
                        "id": t["tweet_id"],
                        "text": t["text"],
                        "author_id": t["author_handle"], # Using handle as ID for now in fallback
                        "created_at": t["created_at"]
                    }
                    raw_users = {
                        "id": t["author_handle"],
                        "username": t["author_handle"],
                        "name": t["author_handle"]
                    }
                    
                    # We can't use the existing TweetProcessor directly because ID formats might differ
                    # (UUID vs String handle). 
                    # For MVP, we'll do a custom process or adapt TweetProcessor.
                    # Let's adapt the data to match X API response structure as best as possible
                    raw_tweets["data"].append(raw_item)
                    raw_tweets["includes"]["users"].append(raw_users)

                # Use the processor
                new_tweets = self.processor.process_tweets(
                    raw_tweets,
                    source=source,
                    user_id=self.user.id
                )
                return new_tweets

            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                return []
            finally:
                await browser.close()

    async def monitor_home_timeline(self):
         return await self.fetch_tweets("https://x.com/home", TweetSource.home_timeline)

    async def monitor_list(self, list_id: str):
        # We need the actual list URL, or construct it
        return await self.fetch_tweets(f"https://x.com/i/lists/{list_id}", TweetSource.x_list)
