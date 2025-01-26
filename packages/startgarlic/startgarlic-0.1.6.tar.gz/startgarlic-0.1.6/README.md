# MVP

# Garlic

A RAG-based company information retrieval system that provides intelligent company recommendations based on natural language queries.

## Installation

```bash
pip install startgarlic
```

## Quick Start

```python
from startgarlic import Garlic

# Initialize the system
garlic = Garlic()

# Get a response for a query
response = garlic.generate_response("Tell me about AI companies")
```

## Features

- Company information retrieval using RAG (Retrieval-Augmented Generation)
- Semantic search using sentence transformers
- Built-in company database
- Natural language query processing
- Context-aware responses
- Chat history support

## Usage Examples

### Basic query

```python
response = garlic.generate_response("What companies work with computer vision?")
```

### Query with chat history

```python
chat_history = [
    {"role": "user", "content": "I'm looking for AI companies"},
    {"role": "assistant", "content": "What specific area of AI interests you?"},
    {"role": "user", "content": "Computer vision"}
]

response = garlic.generate_response("Show me some examples", chat_history)
```

## Requirements

- Python >= 3.7
- pandas >= 1.3.0
- sentence-transformers >= 2.0.0
- numpy >= 1.19.0
- openpyxl >= 3.0.0

## Authors

- Bogdan Ciolac (bogdan@startgarlic.com)
- May Elshater (may@startgarlic.com)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

