import requests
import json
from typing import List, Dict, Union, Iterator

class AI_Client:
    """
    Python library for interacting with the Gpt4Zero chat API (Blackbox.ai).
    """
    API_URL = "https://www.blackbox.ai/api/chat"
    DEFAULT_HEADERS = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/json",
        "origin": "https://www.blackbox.ai",
        "referer": "https://www.blackbox.ai/",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }
    AVAILABLE_MODELS = {
    "claude-sonnet-3.5": "claude-sonnet-3.5",
    "gpt-4o": "gpt-4o",
    "gemini-1.5": "gemini-pro",
    "deepseek-r1": "deepseek-r1"  # Добавленная модель
    }
    DEFAULT_MODEL = "claude-sonnet-3.5"
    REQUEST_TIMEOUT = 15  # seconds

    def __init__(self):
        """
        Initializes the AI_Client with default headers.
        """
        self.headers = self.DEFAULT_HEADERS.copy()

    def list_models(self) -> List[str]:
        """
        Returns a list of available models.
        """
        return list(self.AVAILABLE_MODELS.keys())

    def chat(self, messages: List[Dict], model: str = DEFAULT_MODEL, stream: bool = False) -> Union[str, Iterator[str]]:
        """
        Sends messages to the Blackbox.ai chat API and returns the response.

        Args:
            messages (list[dict]): A list of message dictionaries.
                                   Each dictionary should have 'role' and 'content' keys.
                                   For example: [{'role': 'user', 'content': 'Hello'}]
            model (str, optional): The model to use. Defaults to 'claude-sonnet-3.5'.
                                    Available models can be obtained using list_models().
            stream (bool, optional): Whether to stream the response. Defaults to False.

        Returns:
            str: The full response text if stream=False.
            iter: A generator that yields response chunks if stream=True.

        Raises:
            ValueError: If the model is invalid or messages are not a list.
            requests.exceptions.HTTPError: For HTTP errors (status codes >= 400).
            requests.exceptions.RequestException: For other request-related issues.
            Exception: For unexpected errors during response processing.
        """
        if model not in self.AVAILABLE_MODELS:
            raise ValueError(f"Invalid model: {model}. Available models are: {self.list_models()}")
        if not isinstance(messages, list):
            raise ValueError("Messages must be a list.")
        if not messages:
            raise ValueError("Messages list cannot be empty.")
        for msg in messages:
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                raise ValueError("Each message must be a dictionary with 'role' and 'content' keys.")

        processed_messages = []
        for msg in messages:
            message_copy = msg.copy() # Avoid modifying the original message
            if message_copy.get('role') == 'user':
                message_copy['content'] = f"@{model} {message_copy['content']}"
            processed_messages.append(message_copy)

        blackbox_model = self.AVAILABLE_MODELS[model]

        request_data = {
            "messages": processed_messages,
            "agentMode": {},
            "clickedAnswer2": False,
            "clickedAnswer3": False,
            "clickedForceWebSearch": False,
            "codeModelMode": True,
            "deepSearchMode": False,
            "domains": None,
            "githubToken": "",
            "id": "3JAO5pr",
            "imageGenerationMode": False,
            "isChromeExt": False,
            "isMicMode": False,
            "maxTokens": 1024,
            "mobileClient": False,
            "playgroundTemperature": None,
            "playgroundTopP": None,
            "previewToken": None,
            "trendingAgentMode": {},
            "userId": None,
            "userSelectedModel": blackbox_model,
            "userSystemPrompt": None,
            "validated": "00f37b34-a166-4efb-bce5-1312d87f2f94", 
            "visitFromDelta": False,
            "vscodeClient": False,
            "webSearchModePrompt": False,
        }

        try:
            response = requests.post(
                self.API_URL,
                headers=self.headers,
                json=request_data,
                stream=stream,
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status() 

            if stream:
                def generate():
                    for line in response.iter_lines(decode_unicode=True): 
                        if line:
                            yield line
                return generate()
            else:
                return response.text

        except requests.exceptions.HTTPError as http_err:
            raise requests.exceptions.HTTPError(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as req_err:
            raise requests.exceptions.RequestException(f"Request error occurred: {req_err}")
        except Exception as e:
            raise Exception(f"Unexpected error occurred during chat: {e}")