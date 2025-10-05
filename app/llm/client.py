from app.config import settings
from openai import OpenAI, APIError, APITimeoutError, RateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import json
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self) -> None:
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.enabled = bool(self.api_key)
        self.client: Optional[OpenAI] = None
        if self.enabled:
            self.client = OpenAI(api_key=self.api_key)

    def available(self) -> bool:
        return self.enabled

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APITimeoutError, RateLimitError)),
    )
    def eval_json(self, prompt: str, system: str = "", temperature: float | None = None) -> dict:
        """
        Return JSON from the model with retry logic.
        
        Args:
            prompt: User prompt
            system: System message
            temperature: Controls randomness (0.0-1.0). Lower = more deterministic.
        
        Returns:
            Parsed JSON dict from model response
        
        Raises:
            Exception: If API call fails after retries or if response is not valid JSON
        """
        if not self.enabled or not self.client:
            raise Exception("LLM client not available. Check OPENAI_API_KEY configuration.")
        
        # Use configured temperature if not specified
        if temperature is None:
            temperature = settings.openai_temperature
        
        try:
            logger.info(f"Calling OpenAI API with model={self.model}, temp={temperature}")
            
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
            )
            
            content = response.choices[0].message.content
            if not content:
                raise Exception("Empty response from OpenAI")
            
            # Parse JSON response
            result = json.loads(content)
            logger.info(f"Successfully received JSON response with keys: {list(result.keys())}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            raise Exception(f"Invalid JSON response from model: {e}")
        except (APITimeoutError, RateLimitError) as e:
            logger.warning(f"OpenAI API error (will retry): {e}")
            raise
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIError, APITimeoutError, RateLimitError)),
    )
    def complete(self, prompt: str, system: str = "", temperature: float = 0.5, max_tokens: int = 1000) -> str:
        """
        Get a text completion from the model with retry logic.
        
        Args:
            prompt: User prompt
            system: System message
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum tokens in response
        
        Returns:
            Text response from model
        """
        if not self.enabled or not self.client:
            raise Exception("LLM client not available. Check OPENAI_API_KEY configuration.")
        
        try:
            logger.info(f"Calling OpenAI API (text) with model={self.model}")
            
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            content = response.choices[0].message.content
            if not content:
                raise Exception("Empty response from OpenAI")
            
            logger.info(f"Successfully received text response ({len(content)} chars)")
            return content.strip()
            
        except (APIError, APITimeoutError, RateLimitError) as e:
            logger.warning(f"OpenAI API error (will retry): {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in LLM call: {e}")
            raise