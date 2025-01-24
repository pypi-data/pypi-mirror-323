from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
import json

import json


@dataclass
class ModelFeatures:
    supports_streaming: bool = False
    supports_images: bool = False
    max_context_length: Optional[int] = None


@dataclass
class ModelConfig:
    """Configuration for a Bedrock model family"""

    request_formatter: Callable[[str, float, int], Dict[str, Any]]
    provider: str
    features: ModelFeatures
    response_parser: Callable[[Dict[str, Any]], Any] = None
    version: Optional[str] = None


"""
Example from docs:
{
  "modelId": "anthropic.claude-3-5-haiku-20241022-v1:0",
  "contentType": "application/json",
  "accept": "application/json",
  "body": {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 200,
    "top_k": 250,
    "stopSequences": [],
    "temperature": 1,
    "top_p": 0.999,
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "hello world"
          }
        ]
      }
    ]
  }
}
"""


def format_anthropic_request(
    prompt: str, temperature: float, max_tokens: int
) -> Dict[str, Any]:
    return {
        "body": json.dumps(
            {
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": 0.9,
                },
            }
        ),
        "contentType": "application/json",
        "accept": "application/json",
    }


def format_amazon_multimodal_embedding_request(
    texts: Optional[List[str]] = None,
    image: Optional[str] = None,
    dimensions: int = 1024,
) -> Dict[str, Any]:
    """
    Format request specifically for Amazon Titan Multimodal Embeddings.

    Parameters:
    - texts (Optional[List[str]]): The input text(s) for which to generate embeddings.
    - image (Optional[str]): Base64-encoded image string.
    - output_embedding_length (int): The size of the embedding vector. Default is 1024.
    """
    request_body = {"embeddingConfig": {"outputEmbeddingLength": dimensions}}

    if texts:
        if len(texts) != 1:
            raise ValueError(
                "Amazon multimodal embedding models support only a single text input."
            )
        request_body["inputText"] = texts[0]

    if image:
        request_body["inputImage"] = image

    return {
        "body": json.dumps(request_body),
        "contentType": "application/json",
        "accept": "application/json",
    }


def parse_amazon_multimodal_embedding_response(
    response: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Parses the Amazon Titan Multimodal Embedding response and returns embeddings.

    Returns:
        Dict[str, Any]: Contains 'texts' and/or 'image' keys with their respective embeddings.
    """
    body = response.get("body")
    if not body:
        raise ValueError("No body in response.")

    # Read and decode the StreamingBody
    body_content = body.read().decode("utf-8")
    parsed_body = json.loads(body_content)

    return parsed_body["embedding"]


def format_amazon_request(
    prompt: str, temperature: float, max_tokens: int
) -> Dict[str, Any]:
    return {
        "body": json.dumps(
            {
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": 0.9,
                },
            }
        ),
        "contentType": "application/json",
        "accept": "application/json",
    }


def format_amazon_embedding_request(
    texts: List[str],
    dimensions: int = 512,
    normalize: bool = True,
    embedding_types: List[str] = ["float"],
) -> Dict[str, Any]:
    """
    Format request specifically for Amazon embedding models.

    Parameters:
    - text (str): The input text for which to generate embeddings.
    - dimensions (int): The size of the embedding vector.
    - normalize (bool): Whether to normalize the embedding vector.
    - embedding_types (List[str]): The types of embeddings to generate.
    """
    return {
        "body": json.dumps(
            {
                "inputText": texts[0],
                "dimensions": dimensions,
                "normalize": normalize,
                "embeddingTypes": embedding_types,
            }
        ),
        "contentType": "application/json",
        "accept": "application/json",
    }


def format_cohere_embedding_request(
    texts: List[str], input_type: str = "search_document"
) -> Dict[str, Any]:
    """
    Format request specifically for Cohere embedding models.

    Parameters:
    - texts (List[str]): The list of input texts for which to generate embeddings.
    - input_type (str): The type of input, e.g., "search_document".
    """
    return {
        "body": json.dumps({"texts": texts, "input_type": input_type}),
        "contentType": "application/json",
        "accept": "application/json",
    }


def format_cohere_request(
    prompt: str, temperature: float, max_tokens: int
) -> Dict[str, Any]:
    return {"prompt": prompt, "max_tokens": max_tokens, "temperature": temperature}


def format_ai21_request(
    prompt: str, temperature: float, max_tokens: int
) -> Dict[str, Any]:
    return {"prompt": prompt, "maxTokens": max_tokens, "temperature": temperature}


def format_meta_request(
    prompt: str, temperature: float, max_tokens: int
) -> Dict[str, Any]:
    return {"prompt": prompt, "max_gen_len": max_tokens, "temperature": temperature}


def format_mistral_request(
    prompt: str, temperature: float, max_tokens: int
) -> Dict[str, Any]:
    return {"prompt": prompt, "max_tokens": max_tokens, "temperature": temperature}


# Response parsers
def parse_anthropic_response(response: Dict[str, Any]) -> str:
    return response.get("content", [])[0].get("text", "")


def parse_amazon_response(response: Dict[str, Any]) -> str:
    return response.get("results", [{}])[0].get("outputText", "")


def parse_cohere_response(response: Dict[str, Any]) -> str:
    return response.get("generations", [{}])[0].get("text", "")


def parse_embedding_response(response: Dict[str, Any]) -> list:
    """
    Parses the embedding response and returns the embedding vector.
    """
    # Assuming the embedding is returned under 'embedding' key
    embedding = response.get("embedding")
    if not embedding:
        raise ValueError("No embedding found in the response.")
    return embedding


def parse_amazon_embedding_response(response: Dict[str, Any]) -> List[float]:
    """
    Parses the Amazon embedding response and returns the embedding vector.
    """
    body = response.get("body")
    if not body:
        raise ValueError("No body in response.")
    # Read and decode the StreamingBody
    body_content = body.read().decode("utf-8")
    parsed_body = json.loads(body_content)
    embedding = parsed_body.get("embedding")
    if not embedding:
        raise ValueError("No embedding found in the response.")
    return embedding


def parse_cohere_embedding_response(response: Dict[str, Any]) -> List[List[float]]:
    """
    Parses the Cohere embedding response and returns a list of embedding vectors.
    """
    print(f"response: {response}")
    body = response.get("body")
    print(f"body: {body}")
    if not body:
        raise ValueError("No body in response.")
    # Read and decode the StreamingBody
    body_content = body.read().decode("utf-8")
    print(f"body_content: {body_content}")
    parsed_body = json.loads(body_content)
    print(f"parsed_body: {parsed_body}")
    embeddings = parsed_body.get("embeddings")
    print(f"embeddings: {embeddings}")
    if not embeddings:
        raise ValueError("No embeddings found in the response.")
    return embeddings


def parse_ai21_response(response: Dict[str, Any]) -> str:
    return response.get("completions", [{}])[0].get("data", {}).get("text", "")


def parse_meta_response(response: Dict[str, Any]) -> str:
    return response.get("generation", "")


def parse_mistral_response(response: Dict[str, Any]) -> str:
    return response.get("outputs", [{}])[0].get("text", "")


# Model registry
MODEL_CONFIGS = {
    "anthropic": ModelConfig(
        request_formatter=format_anthropic_request,
        provider="Anthropic",
        features=ModelFeatures(
            supports_streaming=True, supports_images=True, max_context_length=200000
        ),
    ),
    "amazon": ModelConfig(
        request_formatter=format_amazon_request,
        provider="Amazon",
        features=ModelFeatures(
            supports_streaming=True, supports_images=False, max_context_length=100000
        ),
    ),
    "amazon.titan-embed-image-v1": ModelConfig(
        request_formatter=format_amazon_multimodal_embedding_request,
        response_parser=parse_amazon_multimodal_embedding_response,
        provider="Amazon",
        features=ModelFeatures(
            supports_streaming=False,
            supports_images=True,
            max_context_length=100000,
        ),
    ),
    "amazon.titan-embed-text-v2:0": ModelConfig(
        request_formatter=format_amazon_embedding_request,
        response_parser=parse_amazon_embedding_response,
        provider="Amazon",
        features=ModelFeatures(
            supports_streaming=False,
            supports_images=False,
            max_context_length=100000,
        ),
    ),
    "cohere.embed-multilingual-v3": ModelConfig(
        request_formatter=format_cohere_embedding_request,
        response_parser=parse_cohere_embedding_response,
        provider="Cohere",
        features=ModelFeatures(
            supports_streaming=False,
            supports_images=False,
            max_context_length=5000,  # Adjust as per model's specification
        ),
    ),
    "cohere.embed-english-v3": ModelConfig(
        request_formatter=format_cohere_embedding_request,
        response_parser=parse_cohere_embedding_response,
        provider="Cohere",
        features=ModelFeatures(
            supports_streaming=False, supports_images=False, max_context_length=5000
        ),
    ),
}
