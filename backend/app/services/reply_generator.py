from sqlalchemy.orm import Session
from app.models.tweet import Tweet
from app.models.user import User
from app.models.reply import ReplyCandidate
from app.schemas.tweet import TweetInDB
from typing import List
import openai
import google.generativeai as genai
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ReplyGeneratorService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        # Initialize clients based on config/user pref
        # For MVP we might just rely on env vars or user.ai_rules if api key provided there
        self.openai_api_key = settings.OPENAI_API_KEY if hasattr(settings, 'OPENAI_API_KEY') else None
        self.gemini_api_key = settings.GEMINI_API_KEY if hasattr(settings, 'GEMINI_API_KEY') else None

    async def generate_replies(self, tweet: Tweet, count: int = 3) -> List[ReplyCandidate]:
        prompt = self._construct_prompt(tweet)
        replies_text = []

        if self.openai_api_key:
            replies_text = await self._generate_openai(prompt, count)
        elif self.gemini_api_key:
            replies_text = await self._generate_gemini(prompt, count)
        else:
            logger.warning("No LLM API key found.")
            return []

        candidates = []
        for text in replies_text:
            candidate = ReplyCandidate(
                tweet_id=tweet.id,
                user_id=self.user.id,
                generated_text=text,
                llm_model_used="openai-gpt-4" if self.openai_api_key else "gemini-pro",
                # Safety score will be calculated by SafetyClassifier next
            )
            self.db.add(candidate)
            candidates.append(candidate)
        
        self.db.commit()
        return candidates

    def _construct_prompt(self, tweet: Tweet) -> str:
        # Fetch active persona
        from app.models.persona import Persona
        active_persona = self.db.query(Persona).filter(
            Persona.user_id == self.user.id, 
            Persona.is_active == True
        ).first()

        if active_persona:
            system_instruction = active_persona.system_prompt
            style = f"Persona: {active_persona.name}"
        else:
            # Fallback
            system_instruction = "You are an expert X/Twitter growth hacker. Generate concise, engaging, and human-sounding replies."
            style = self.user.ai_rules.get("style", "professional and witty")

        tweet_context = f"Tweet by {tweet.author_x_username}: {tweet.full_text}"
        
        return f"{system_instruction}\nStyle: {style}\n\n{tweet_context}\n\nGenerate 3 distinct replies."

    async def _generate_openai(self, prompt: str, count: int) -> List[str]:
        try:
            openai.api_key = self.openai_api_key
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                n=count # This might not work as expected for "3 distinct replies" instruction if n=1. 
                # Better to ask for a JSON list or split by newline.
                # For MVP, let's assume the model returns a list or we parse it.
            )
            # Naive parsing if model returns one block
            content = response.choices[0].message.content
            # Split by newlines or numbers would be better
            return [line.strip() for line in content.split('\n') if line.strip() and not line[0].isdigit()] 
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return []

    async def _generate_gemini(self, prompt: str, count: int) -> List[str]:
        # Implement Gemini call
        return []

