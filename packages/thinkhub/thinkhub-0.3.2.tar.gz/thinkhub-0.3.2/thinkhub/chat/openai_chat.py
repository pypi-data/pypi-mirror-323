"""
Define the `OpenAIChatService` class, which interacts with the OpenAI API.

to generate chat responses asynchronously. It supports both text and image inputs
and streams responses back to the user in chunks.
"""

import base64
import os
from collections.abc import AsyncGenerator
from typing import Union

import tiktoken
from openai import AsyncOpenAI

from thinkhub.chat.base import ChatServiceInterface
from thinkhub.chat.exceptions import (
    InvalidInputDataError,
    MissingAPIKeyError,
    TokenLimitExceededError,
)


class OpenAIChatService(ChatServiceInterface):
    """
    An implementation of the `ChatServiceInterface` for interacting with the OpenAI API.

    This service provides functionality to:
    - Stream chat responses from OpenAI.
    - Handle both text and image inputs.
    - Manage token limits for the model's context.
    """

    def __init__(self, model: str = "gpt-4o"):
        """
        Initialize the OpenAIChatService with a hypothetical AsyncOpenAI client.

        Args:
            model (str): Model name to use for chat.
        """
        api_key = os.getenv("CHATGPT_API_KEY")

        if not api_key:
            # Raise the custom MissingAPIKeyError
            raise MissingAPIKeyError("CHATGPT_API_KEY environment variable is missing.")

        self.openai = AsyncOpenAI(api_key=api_key)
        self.model = model

        # Initialize the message context
        self.messages: list[dict[str, str]] = []

        # Token management
        self.model_encoding = tiktoken.encoding_for_model(model)
        self.MAX_TOKENS = 4096

    def _check_and_manage_token_limit(self):
        """
        Ensure that the total tokens in the messages context do not exceed.

        the model's maximum token limit.
        Raises a TokenLimitExceededError if the context cannot be reduced further.
        """
        total_tokens = sum(
            len(self.model_encoding.encode(m["content"]))
            for m in self.messages
            if "content" in m
        )

        # Continuously remove the second message (oldest user message) if over the limit.
        while total_tokens > self.MAX_TOKENS and len(self.messages) > 1:
            self.messages.pop(1)
            total_tokens = sum(
                len(self.model_encoding.encode(m["content"]))
                for m in self.messages
                if "content" in m
            )

        # If still over the limit but cannot remove any more messages, raise an error.
        if total_tokens > self.MAX_TOKENS:
            raise TokenLimitExceededError(
                "Cannot reduce the message context further; token limit exceeded."
            )

    def encode_image(self, image_path: str) -> str:
        """
        Encode an image file as a base64 string.

        Args:
            image_path (str): Path to the image file.

        Returns:
            str: Base64-encoded image string.
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            raise InvalidInputDataError(f"Failed to encode image: {e}")

    async def stream_chat_response(
        self,
        input_data: Union[str, list[dict[str, str]]],
        system_prompt: str = "You are a helpful assistant.",
    ) -> AsyncGenerator[str, None]:
        """
        Stream the ChatGPT response given input data.

        It supports both text and image (as base64) inputs, yielding partial
        responses (tokens) as they arrive.

        Args:
            input_data (Union[str, list[dict[str, str]]]): The user input,
                either as plain text or a list of dicts each containing an
                'image_path' key.
            system_prompt (str): The system's initial prompt to guide the
                assistant's behavior.

        Yields:
            AsyncGenerator[str, None]: Partial response tokens.
        """
        if not input_data:
            return  # Empty input, so stop immediately.

        # Add system prompt if this is the first interaction
        if not self.messages:
            self.messages.append({"role": "system", "content": system_prompt})

        # Prepare the API call payload
        api_payload = {
            "model": self.model,
            "stream": True,
            # Ensure context remains intact for text inputs
            "messages": self.messages.copy(),
        }

        # Check the input type
        if isinstance(input_data, str):
            # Add user text input to context and API payload
            self.messages.append({"role": "user", "content": input_data})
            api_payload["messages"] = self.messages
        elif isinstance(input_data, list) and all(
            isinstance(item, dict) and "image_path" in item for item in input_data
        ):
            # Process each dictionary in the list and encode images as base64
            image_messages = []
            for item in input_data:
                image_path = item["image_path"]  # Extract image path
                base64_image = self.encode_image(image_path)  # Encode image to base64
                image_messages.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    }
                )

            # Add image content to API payload
            api_payload["messages"].append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze the following images and provide a response.",
                        },
                        *image_messages,
                    ],
                }
            )
        else:
            # Raise InvalidInputDataError for incorrect input type
            raise InvalidInputDataError(
                "Invalid input_data type. Must be a string or a list of dictionaries "
                "with 'image_path' keys."
            )

        # Manage token limits
        self._check_and_manage_token_limit()

        try:
            response_aiter = await self.openai.chat.completions.create(**api_payload)

            # To collect chunks for constructing full_response
            full_response_chunks = []
            async for chunk in response_aiter:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    content = delta.content
                    full_response_chunks.append(content)
                    yield content  # Stream the chunk

            # Construct the full response from collected chunks
            full_response = "".join(full_response_chunks)
            self.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            yield f"[Error streaming response: {e}]"
