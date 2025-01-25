"""
This module provides a client for the IronaAI API.
"""

import os
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

import litellm
import requests
from dotenv import load_dotenv

# Constants
BASE_IAI_URL = "https://app.irona.ai/api/v1/model-router"
DEFAULT_MODEL = "openai/gpt-3.5-turbo"
MAX_RETRIES = 3

# Load environment variables from .env file
load_dotenv()

# if model select endpoint not in env, use default
MODEL_SELECT_ENDPOINT = f"{BASE_IAI_URL}/select-model"


class IronaAI:
    def __init__(
        self,
    ):
        self.api_key = os.getenv("IRONAAI_API_KEY")
        if not self.api_key:
            raise ValueError("IRONAAI_API_KEY not found in environment variables")

        self.iai_api_url = DEFAULT_API_URL

    def error_handler(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(MAX_RETRIES):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == MAX_RETRIES - 1:
                        raise e
                    print(f"Error occurred: {e}. Retrying...")

        return wrapper

    def model_select(
        self,
        messages: List[Dict[str, str]],
        metric: str = "accuracy",
        max_model_depth: int = None,
        hash_content: bool = False,
        tradeoff: Optional[str] = None,  # latency, cost, accuracy
    ) -> tuple:
        url = MODEL_SELECT_ENDPOINT
        payload = {
            "messages": messages,
            "llm_providers": [
                {
                    "provider": model.split("/", 1)[0],
                    "model": model.split("/", 1)[1],
                }
                for model in self.model_list
            ],
            "metric": metric,
            "max_model_depth": max_model_depth or len(self.model_list),
            "hash_content": hash_content,
        }
        if tradeoff:
            payload["tradeoff"] = tradeoff
        if preference_id:
            payload["preference_id"] = preference_id
        if previous_session:
            payload["previous_session"] = previous_session

        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        best_model = (
            f"{data['providers'][0]['provider']}/{data['providers'][0]['model']}"
        )
        return best_model, data["session_id"]

    @error_handler
    def completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        metric: str = "accuracy",
        max_model_depth: Optional[int] = None,
        hash_content: bool = False,
        tradeoff: Optional[str] = None,
        preference_id: Optional[str] = None,
        previous_session: Optional[str] = None,
        stream: bool = False,
        functions: Optional[List[Dict]] = None,
        **kwargs,
    ) -> Any:

        start_time = time.time()
        selected_model, session_id = self._model_select(
            messages,
            metric,
            max_model_depth,
            hash_content,
            tradeoff,
            preference_id,
            previous_session,
        )

        completion_kwargs = {
            "model": selected_model,
            "messages": messages,
            "stream": stream,
            **kwargs,
        }

        if functions:
            completion_kwargs["functions"] = functions
            completion_kwargs["function_call"] = "auto"

        # Pass the API key for the selected model to LiteLLM
        provider = selected_model.split("/")[0]
        api_key_env_var = f"{provider.upper()}_API_KEY"
        api_key = os.getenv(api_key_env_var)
        if not api_key:
            raise ValueError(f"{api_key_env_var} not found in environment variables")

        completion_kwargs["api_key"] = api_key

        response = litellm.completion(**completion_kwargs)

        end_time = time.time()
        tokens_completed = len(response.choices[0].message.content.split())
        tokens_per_second = tokens_completed / (end_time - start_time)

        # TODO: Report latency

        return response

    def stream_completion(self, *args, **kwargs):
        kwargs["stream"] = True
        return self.completion(*args, **kwargs)
