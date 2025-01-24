# embedding-utils

A lightweight Python library providing a convenient wrapper around [Sentence Transformers](https://www.sbert.net/) for generating text embeddings with caching. Perfect for projects that need repeated embeddings of the same texts without re-computation, or that want a straightforward API for embedding-based similarity.

## Features

- **Easy Embedding**: Encode batches of texts into vector embeddings with a single method.
- **Built-in Caching**: Prevents re-computation for texts previously embedded; saves and loads from disk.
- **Device Management**: Optionally integrates with [device-selector](https://github.com/darizae/device-selector) or falls back to CPU/GPU detection.
- **Cosine Similarity**: Utility method to compute similarity between two embedding vectors.

## Installation

```bash
pip install embedding-utils==0.1.2
