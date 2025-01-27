# dim-python

A Python binding for dim-rs, providing efficient text and image vectorization using OpenAI models.

## Installation

```bash
pip install dim-for-python
```

## Features

- Async text vectorization using OpenAI's language models
- Async image vectorization using OpenAI's vision models
- Concurrent processing for improved performance
- Custom API endpoint support
- Type hints included

## Requirements

- Python 3.7+
- OpenAI API key
- Rust toolkit (for building from source)

## Usage

### Text Vectorization

```python
import asyncio
from dim_for_python import vectorize_string

async def main():
    # Initialize text and prompts
    text = "The quick brown fox jumps over the lazy dog"
    prompts = [
        "What is the mood of this text?",
        "What actions are described in this text?"
    ]

    # Get vector representation
    vector = await vectorize_string(
        string=text,
        prompts=prompts,
        model="gpt-4",
        api_key="your-api-key"
    )

    print(f"Vector dimension: {len(vector)}")
    print(f"Vector: {vector}")

# Run the async function
asyncio.run(main())
```

### Image Vectorization

```python
import asyncio
from dim_for_python import vectorize_image
from PIL import Image
import io

async def main():
    # Load and prepare image
    image = Image.open("path/to/image.jpg")
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()

    # Define prompts for image analysis
    prompts = [
        "What is the main subject of this image?",
        "Describe the colors in this image"
    ]

    # Get vector representation
    vector = await vectorize_image(
        image_bytes=img_bytes,
        prompts=prompts,
        model="gpt-4-vision-preview",
        api_key="your-api-key"
    )

    print(f"Vector dimension: {len(vector)}")
    print(f"Vector: {vector}")

# Run the async function
asyncio.run(main())
```

### Using Custom API Endpoint

```python
vector = await vectorize_string(
    string="Your text here",
    prompts=["Your prompt"],
    model="gpt-4",
    api_key="your-api-key",
    base_url="https://your-custom-endpoint.com"
)
```

## API Reference

### vectorize_string

```python
async def vectorize_string(
    string: str,
    prompts: List[str],
    model: str,
    api_key: str,
    base_url: Optional[str] = None
) -> List[float]
```

Parameters:
- `string`: The input text to vectorize
- `prompts`: List of prompts to guide the vectorization
- `model`: OpenAI model identifier
- `api_key`: Your OpenAI API key
- `base_url`: Optional custom API endpoint

Returns:
- List of floating-point numbers representing the text vector

### vectorize_image

```python
async def vectorize_image(
    image_bytes: bytes,
    prompts: List[str],
    model: str,
    api_key: str,
    base_url: Optional[str] = None
) -> List[float]
```

Parameters:
- `image_bytes`: Raw bytes of the image
- `prompts`: List of prompts to guide the vectorization
- `model`: OpenAI model identifier
- `api_key`: Your OpenAI API key
- `base_url`: Optional custom API endpoint

Returns:
- List of floating-point numbers representing the image vector

## Development

### Building from source

```bash
# Clone the repository
git clone https://github.com/yourusername/dim-python
cd dim-python

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install development dependencies
pip install maturin pytest pytest-asyncio Pillow

# Build and install in development mode
maturin develop
```

### Running tests

```bash
pytest tests/ -v
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

This project is a Python binding for [dim-rs](link-to-dim-rs), which provides the core functionality for text and image vectorization.