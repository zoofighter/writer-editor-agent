"""
LM Studio client wrapper for local LLM integration.

This module provides a wrapper around the OpenAI-compatible API
that LM Studio exposes for local language model inference.
"""

from openai import OpenAI
from typing import List, Dict, Optional


class LMStudioClient:
    """
    Wrapper for LM Studio API using OpenAI-compatible interface.

    LM Studio runs locally and provides an OpenAI-compatible endpoint.
    Default endpoint: http://localhost:1234/v1

    Example:
        >>> client = LMStudioClient()
        >>> messages = [{"role": "user", "content": "Hello!"}]
        >>> response = client.generate(messages)
    """

    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        model_name: str = "qwen",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        Initialize the LM Studio client.

        Args:
            base_url: LM Studio API endpoint
            model_name: Model identifier (default: qwen)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
        """
        self.client = OpenAI(
            base_url=base_url,
            api_key="not-needed"  # LM Studio doesn't require authentication
        )
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate completion from LM Studio.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
                     Example: [{"role": "system", "content": "You are a helpful assistant"},
                              {"role": "user", "content": "Hello!"}]
            temperature: Optional override for sampling temperature
            max_tokens: Optional override for max tokens

        Returns:
            Generated text content as a string

        Raises:
            Exception: If the API call fails
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"LM Studio API call failed: {e}")

    def test_connection(self) -> bool:
        """
        Test if LM Studio is accessible and responding.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self.client.models.list()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
