## Modelhub Client

This is a Python client for the Modelhub API. It is a simple wrapper around the Modelhub API, which is a RESTful API for managing virtual deep learning models.

## Quick Start

```bash
pip install puyuan_modelhub --user
```

Usage

```python
from modelhub import Modelhub

mh = Modelhub()

# List models
print(mh.supported_models)

# Generate text
mh.generate("hello", model="gpt-4o")

# Streaming text
for t in mh.stream("hello", model="gpt-4o"):
    print(t.token, end="")

# Embedding
mh.embedding("hello", model="m3e")

# Rerank
mh.rerank([["hello", "world"], ["good", "morning"]], model="bge-reranker-base")
```
