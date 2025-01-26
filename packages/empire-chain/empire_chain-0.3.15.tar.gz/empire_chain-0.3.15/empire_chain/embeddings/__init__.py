from .openai_embeddings import OpenAIEmbeddings

def SentenceTransformerEmbeddings(*args, **kwargs):
    try:
        from .sentence_transformers_embeddings import SentenceTransformerEmbeddings as _SentenceTransformerEmbeddings
        return _SentenceTransformerEmbeddings(*args, **kwargs)
    except ImportError:
        raise ImportError(
            "Could not import sentence-transformers. Please install it with: "
            "pip install sentence-transformers"
        )

__all__ = ["OpenAIEmbeddings", "SentenceTransformerEmbeddings"]
