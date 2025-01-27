from typing import List, Optional

async def vectorize_string(
    string: str,
    prompts: List[str],
    model: str,
    api_key: str,
    base_url: Optional[str] = None
) -> List[float]:
    """Vectorize a string using OpenAI's API.

    Args:
        string: The input text to vectorize
        prompts: List of prompts to use for vectorization
        model: The OpenAI model to use (e.g. "text-embedding-ada-002")
        api_key: OpenAI API key
        base_url: Optional custom API base URL

    Returns:
        List of float values representing the vectorized string
    """
    ...

async def vectorize_image(
    image_bytes: bytes,
    prompts: List[str],
    model: str,
    api_key: str,
    base_url: Optional[str] = None
) -> List[float]:
    """Vectorize an image using OpenAI's API.

    Args:
        image_bytes: Raw bytes of the image to vectorize
        prompts: List of prompts to use for vectorization
        model: The OpenAI model to use (e.g. "gpt-4-vision-preview")
        api_key: OpenAI API key
        base_url: Optional custom API base URL

    Returns:
        List of float values representing the vectorized image
    """
    ...
