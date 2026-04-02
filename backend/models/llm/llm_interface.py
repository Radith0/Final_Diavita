"""Groq AI LLM interface."""
import os
from typing import Dict, Any, Optional
import aiohttp
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class GroqLLMInterface:
    """Interface for Groq AI API."""

    def __init__(self):
        """Initialize Groq LLM interface."""
        self.api_key = Config.GROQ_API_KEY
        self.model = Config.GROQ_MODEL
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.enabled = bool(self.api_key)

        if not self.api_key:
            logger.warning("GROQ_API_KEY not found - LLM will use default responses")
        else:
            logger.info(f"Groq LLM initialized with model: {self.model}")

    async def generate(self, prompt: str, temperature: float = None,
                      max_tokens: int = None) -> str:
        """
        Generate text using Groq AI.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        # If LLM is not enabled, return empty string (will trigger default responses)
        if not self.enabled:
            logger.debug("LLM not enabled, returning empty response")
            return ""

        try:
            temperature = temperature or Config.LLM_TEMPERATURE
            max_tokens = max_tokens or Config.LLM_MAX_TOKENS

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a diabetes prevention health advisor. Provide evidence-based, personalized advice. Be concise, actionable, and empathetic."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Groq API error: {error_text}")
                        raise Exception(f"Groq API request failed: {response.status}")

                    result = await response.json()
                    generated_text = result['choices'][0]['message']['content']

                    logger.debug(f"Generated {len(generated_text)} characters")
                    return generated_text

        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            return ""  # Return empty string instead of raising

    async def generate_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """
        Generate with retry logic.

        Args:
            prompt: Input prompt
            max_retries: Maximum retry attempts

        Returns:
            Generated text
        """
        for attempt in range(max_retries):
            try:
                return await self.generate(prompt)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Retry {attempt + 1}/{max_retries} after error: {str(e)}")
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
