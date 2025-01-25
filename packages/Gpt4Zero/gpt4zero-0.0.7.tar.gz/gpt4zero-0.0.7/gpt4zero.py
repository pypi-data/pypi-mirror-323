import requests

class AI_Client:
    """
    Python library for interacting with the Gpt4Zero chat API.
    """
    def __init__(self):
        self.url = "https://www.blackbox.ai/api/chat"
        self.headers = {
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
        self.available_models = {
            "claude-sonnet-3.5": "claude-sonnet-3.5",
            "gpt-4o": "gpt-4o",
            "gemini-1.5": "gemini-pro"
        }

    def list_models(self):
        """
        Returns a list of available models.
        """
        return list(self.available_models.keys())

    def chat(self, messages, model='claude-sonnet-3.5', stream=False):
        """
        Sends messages to the Blackbox.ai chat API and returns the response.

        Args:
            messages (list): A list of message dictionaries.
                               Each dictionary should have 'role' and 'content' keys.
                               For example: [{'role': 'user', 'content': 'Hello'}]
            model (str, optional): The model to use. Defaults to 'claude-sonnet-3.5'.
                                    Available models can be obtained using list_models().
            stream (bool, optional): Whether to stream the response. Defaults to False.

        Returns:
            If stream=False:
                str: The full response text.
            If stream=True:
                generator: A generator that yields response chunks.

        Raises:
            ValueError: If the model is invalid or messages are not a list.
            requests.exceptions.RequestException: If there is an issue with the API request.
            Exception: For other unexpected errors.
        """
        if model not in self.available_models:
            raise ValueError(f"Invalid model: {model}. Available models are: {self.list_models()}")
        if not isinstance(messages, list):
            raise ValueError("Messages must be a list.")

        processed_messages = []
        for msg in messages:
            if msg.get('role') == 'user' and 'content' in msg:
                msg['content'] = f"@{model} {msg['content']}"
            processed_messages.append(msg)

        blackbox_model = self.available_models[model]

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
            "id": "3JAO5pr", # You might want to generate a unique ID for each request if needed
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
            "validated": "00f37b34-a166-4efb-bce5-1312d87f2f94", # Consider if this should be constant or dynamically generated
            "visitFromDelta": False,
            "vscodeClient": False,
            "webSearchModePrompt": False,
        }

        try:
            response = requests.post(self.url, headers=self.headers, json=request_data, stream=stream)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            if stream:
                def generate():
                    buffer = b''
                    for chunk in response.iter_content(chunk_size=1):
                        buffer += chunk
                        try:
                            text = buffer.decode('utf-8')
                            yield text
                            buffer = b''
                        except UnicodeDecodeError:
                            continue
                    if buffer:
                        try:
                            text = buffer.decode('utf-8', errors='ignore')
                            yield text
                        except Exception:
                            pass
                return generate()
            else:
                return response.text

        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"Error during API request: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")