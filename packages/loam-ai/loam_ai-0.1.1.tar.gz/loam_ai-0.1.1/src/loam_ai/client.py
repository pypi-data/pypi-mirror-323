import boto3
import json
import os
from typing import Any, Dict, Generator, List, Optional
from rich.console import Console
from .models import MODEL_CONFIGS
import logging

console = Console()
logger = logging.getLogger(__name__)


class BedrockClient:
    def __init__(
        self,
        profile_name: Optional[str] = None,
        region_name: Optional[str] = None,
        session: Optional[boto3.Session] = None,
    ):
        self.session = session or boto3.Session(
            profile_name=profile_name,
            region_name=region_name or os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        )

        self.profile = self.session.profile_name
        self.region = self.session.region_name
        self.credentials = self.session.get_credentials()

        self.runtime = self.session.client("bedrock-runtime")
        self.bedrock = self.session.client("bedrock")

        self.account_id = self.get_account_id()

    def get_account_id(self) -> str:
        """Retrieve the AWS account ID using STS."""
        try:
            sts_client = self.session.client("sts")
            identity = sts_client.get_caller_identity()
            return identity["Account"]
        except Exception as e:
            raise Exception(f"Failed to retrieve AWS account ID: {str(e)}")

    def _stream_response(
        self, stream_response, debug=False
    ) -> Generator[str, None, None]:
        """Process a streaming response from Bedrock"""
        try:
            for event in stream_response["body"]:
                raw_bytes = event.get("chunk", {}).get("bytes")
                if not raw_bytes:
                    continue

                chunk = json.loads(raw_bytes)

                if debug:
                    console.print("[bold cyan]DEBUG chunk:[/bold cyan]", chunk)

                # If it's the "contentBlockDelta" style, yield the text
                content_delta = chunk.get("contentBlockDelta", {})
                if "delta" in content_delta:
                    text_segment = content_delta["delta"].get("text", "")
                    # Might be empty for "contentBlockStop" or other events
                    if text_segment:
                        yield text_segment

        except Exception as e:
            raise Exception(f"Error processing stream: {str(e)}")

    """
    Invoke a Bedrock model using streaming by default.
    
    from src.bedrock_cli.client import BedrockClient
    bedrock = BedrockClient(profile_name="default", region_name="us-east-1")
    model_id = "amazon.nova-micro-v1:0"
    prompt = "What is the capital of France?"
    
    gen = bedrock.invoke_model(
        model_id=model_id,
        prompt=prompt,
        temperature=0.7,
        max_tokens=200,
        stream=True,
    )
    
    for chunk in gen:
        print(chunk, end="")
    """

    def invoke_model(
        self,
        model_id: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = True,
        debug: bool = False,
    ) -> Generator[str, None, None]:
        """Invoke a Bedrock model using streaming by default"""
        try:
            provider = model_id.split(".")[0]
            config = MODEL_CONFIGS.get(provider)
            if not config:
                raise ValueError(f"Unsupported model provider: {provider}")

            request_params = config.request_formatter(prompt, temperature, max_tokens)
            response = self.runtime.invoke_model_with_response_stream(
                modelId=model_id, **request_params
            )

            # Stream the response
            if stream:
                yield from self._stream_response(response, debug=debug)
            else:
                # For non-streaming, collect all chunks into a single string
                return "".join(self._stream_response(response, debug=debug))

        except Exception as e:
            raise Exception(f"Model invocation failed: {str(e)}")

    def _stream_converse_response(
        self, stream_response, debug=False
    ) -> Generator[str, None, None]:
        """
        Process a streaming response from converse_stream.
        (Conversation/chat style for some models, including inference profiles.)
        """
        try:
            for event in stream_response["stream"]:
                # Each 'event' is typically a dictionary with a key like "contentBlockDelta"
                if debug:
                    console.print("[bold cyan]DEBUG chunk:[/bold cyan]", event)

                content_block = event.get("contentBlockDelta", {})
                delta = content_block.get("delta", {})
                text_segment = delta.get("text", "")
                if text_segment:
                    yield text_segment
        except Exception as e:
            raise Exception(f"Error processing conversation stream: {str(e)}")

    """
    Conversation-style invocation (using `converse_stream`).
    
    from src.bedrock_cli.client import BedrockClient
    bedrock = BedrockClient(profile_name="staging-superuser", region_name="us-east-1")
    model_id = (
        "arn:aws:bedrock:us-east-1:12345678912345:"
        "inference-profile/us.anthropic.claude-3-5-haiku-20241022-v1:0"
    )
    messages = [
        {
            "role": "user",
            "content": [
                {"text": "What is the capital of France?"}
            ]
        }
    ]

    gen = bedrock.converse_model(
        model_id=model_id,
        messages=messages,
        max_tokens=200,
        temperature=1.0,
        top_p=0.9,
        stream=True,
    )

    for chunk in gen:
        print(chunk, end="")
    """

    def converse_model(
        self,
        model_id: str,
        messages: List[dict],
        max_tokens: int = 200,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stream: bool = True,
        debug: bool = False,
    ) -> Generator[str, None, None]:
        """
        Conversation-style invocation (using `converse_stream`).

        This is often needed for Anthropic or any model behind an inference profile.
        `model_id` can be the foundation-model ID or the ARN of the inference profile.

        :param model_id: e.g. "anthropic.claude-2-v1:0" or
               "arn:aws:bedrock:us-east-1:123456789012:inference-profile/us.anthropic.claude-3-v1:0"
        :param messages: List of message dicts in the format:
            [
              { "role": "system", "content": [{"text": "You are a helpful AI."}] },
              { "role": "user",   "content": [{"text": "What is the capital of France?"}] }
            ]
        """
        try:
            inference_config = {
                "maxTokens": max_tokens,
                "temperature": temperature,
                "topP": top_p,
            }

            response = self.runtime.converse_stream(
                modelId=model_id,
                messages=messages,
                inferenceConfig=inference_config,
            )

            # Stream or collect
            if stream:
                yield from self._stream_converse_response(response, debug=debug)
            else:
                return "".join(self._stream_converse_response(response, debug=debug))

        except Exception as e:
            raise Exception(f"Conversation invocation failed: {str(e)}")

    def generate_embeddings(
        self,
        model_id: str,
        texts: Optional[List[str]] = None,
        image: Optional[str] = None,
        debug: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate embeddings for text, image, or both using the specified Bedrock embedding model.

        Args:
            model_id (str): The model ID to use.
            texts (Optional[List[str]]): List of input texts.
            image (Optional[str]): Base64-encoded image string.
            debug (bool): Flag to enable debug logging.

        Returns:
            Dict[str, Any]: A dictionary containing embeddings for texts and/or image.
        """
        try:
            config = MODEL_CONFIGS.get(model_id)
            if not config:
                raise ValueError(f"Unsupported model ID: {model_id}")

            request_params = {}

            if config.features.supports_images and image:
                # If the model supports images and an image is provided
                request_params = config.request_formatter(texts, image)
            elif texts:
                # If only texts are provided
                request_params = config.request_formatter(texts)
            else:
                raise ValueError("No valid inputs provided for embedding generation.")

            if debug:
                console.print(f"Request Params: {request_params}")

            response = self.runtime.invoke_model(modelId=model_id, **request_params)
            if config.response_parser:
                parsed_response = config.response_parser(response)
            else:
                parsed_response = (
                    response  # Return raw response if no parser is defined
                )

            return parsed_response

        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise Exception(f"Embedding generation failed: {str(e)}")

    def get_session_info(self) -> dict:
        """Get current session information"""
        return {
            "profile": self.profile,
            "region": self.region,
            "credential_type": self._get_credential_type(),
            "available_profiles": self.session.available_profiles,
        }

    def _get_credential_type(self) -> str:
        """Determine the type of credentials being used"""
        if os.getenv("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI"):
            return "ECS Container Role"
        elif os.getenv("AWS_WEB_IDENTITY_TOKEN_FILE"):
            return "Web Identity Token"
        elif self.profile and "sso" in self.profile.lower():
            return "SSO"
        elif os.getenv("AWS_ACCESS_KEY_ID"):
            return "Environment Variables"
        elif self.profile:
            return f"Profile ({self.profile})"
        return "Default Credential Chain"

    def list_models(
        self, provider: Optional[str] = None, output_modality: Optional[str] = None
    ) -> list:
        """List available foundation models"""
        try:
            kwargs = {}
            if provider:
                kwargs["byProvider"] = provider
            if output_modality:
                kwargs["byOutputModality"] = output_modality

            response = self.bedrock.list_foundation_models(**kwargs)
            return response.get("modelSummaries", [])
        except Exception as e:
            raise Exception(f"Failed to list models: {str(e)}")

    def list_inference_profiles(self, next_token: Optional[str] = None) -> list:
        """
        Handle pagination for list_inference_profiles.
        """
        profiles = []
        try:
            kwargs = {}
            if next_token:
                kwargs["nextToken"] = next_token

            response = self.bedrock.list_inference_profiles(**kwargs)
            summaries = response.get("inferenceProfileSummaries", [])
            profiles.extend(summaries)

            if response.get("nextToken"):
                profiles.extend(self.list_inference_profiles(response["nextToken"]))

            return profiles
        except Exception as e:
            raise Exception(f"Failed to list inference profiles: {str(e)}")
