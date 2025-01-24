# techv_ai/client.py
import os
from openai import OpenAI

class Techv_client:
    def __init__(self, api_key=None, base_url="https://api.deepseek.com"):
        """
        Initialize the Deepseek AI client using the OpenAI-compatible client.
        
        Args:
            api_key (str): The API key for Deepseek. If not provided, it will be fetched from the DEEPSEEK_API_KEY environment variable.
            base_url (str): The base URL for the Deepseek API (default: "https://api.deepseek.com").
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set in the DEEPSEEK_API_KEY environment variable.")
        self.client = OpenAI(api_key=self.api_key, base_url=base_url)

    def get_client(self):
        """
        Get the OpenAI-compatible Deepseek client instance.
        
        Returns:
            OpenAI: The Deepseek API client.
        """
        return self.client


class Techv_Chat:
    def __init__(self, client):
        """
        Initialize the chat interface for Deepseek.
        
        Args:
            client (OpenAI): The OpenAI-compatible Deepseek API client.
        """
        self.client = client

    def chat(self, messages, model="deepseek-chat", temperature=0.1, max_tokens=1024, top_p=0.9, stream=True):
        """
        Send a chat request to the Deepseek API.
        
        Args:
            messages (list): List of message dictionaries.
            model (str): The model to use (default: "deepseek-chat").
            temperature (float): Sampling temperature (default: 0.1).
            max_tokens (int): Maximum number of tokens to generate (default: 1024).
            top_p (float): Top-p sampling parameter (default: 0.9).
            stream (bool): Whether to stream the response (default: True).
        
        Returns:
            The response from the Deepseek API.
        """
        response_stream = self.client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stream=stream,
        )
        return response_stream


