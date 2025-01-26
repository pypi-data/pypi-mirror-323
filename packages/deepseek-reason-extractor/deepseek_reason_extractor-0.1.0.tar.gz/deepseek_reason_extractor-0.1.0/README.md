# Deepseek Reason Extractor

A Python package for extracting reasoning patterns using Vaklm models.

## Installation

```bash
pip install deepseek_reason_extractor
```

## Usage

```python
from deepseek_reason_extractor import DeepseekReasonExtractor

# Initialize with default settings
extractor = DeepseekReasonExtractor(
    api_key="your-api-key"  # Optional if endpoint doesn't require auth
)

# Extract reasoning
prompt = "Explain the concept of quantum entanglement"
reasoning = extractor.extract_reasoning(prompt)

print(reasoning)
```

## Configuration

You can customize the endpoint, model, and system prompt:

```python
extractor = DeepseekReasonExtractor(
    endpoint="http://custom.endpoint/v1/chat/completions",
    model_name="custom-model",
    api_key="your-api-key",
    system_prompt="You are a helpful AI assistant"
)
```

## Development

### Building the Package

1. Install build tools:
```bash
pip install build
```

2. Build the package:
```bash
python -m build
```

3. Install locally for testing:
```bash
pip install -e .
```

### Running Tests

```bash
python -m pytest tests/
```

### Deployment

1. Update version in `pyproject.toml` and `__init__.py`
2. Build the package:
```bash
python -m build
```
3. Upload to PyPI:
```bash
python -m twine upload dist/*
```

## Error Handling

The package raises RuntimeError for API failures:

```python
try:
    reasoning = extractor.extract_reasoning(prompt)
except RuntimeError as e:
    print(f"Error: {str(e)}")
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
