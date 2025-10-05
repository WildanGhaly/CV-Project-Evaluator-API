"""
RAG retrieval using Qdrant vector database.
"""
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from openai import OpenAI
from app.config import settings
from typing import List
import logging

logger = logging.getLogger(__name__)

# Singleton client instances
_qdrant_client: QdrantClient | None = None
_openai_client: OpenAI | None = None


def get_qdrant_client() -> QdrantClient:
    """Get or create Qdrant client singleton."""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(":memory:")  # Use in-memory for simplicity
        logger.info("Initialized Qdrant client (in-memory)")
    return _qdrant_client


def get_openai_client() -> OpenAI:
    """Get or create OpenAI client singleton."""
    global _openai_client
    if _openai_client is None:
        if not settings.openai_api_key:
            raise Exception("OpenAI API key not configured")
        _openai_client = OpenAI(api_key=settings.openai_api_key)
        logger.info("Initialized OpenAI client for embeddings")
    return _openai_client


def get_embedding(text: str) -> List[float]:
    """
    Get embedding vector for text using OpenAI.
    
    Args:
        text: Text to embed
    
    Returns:
        Embedding vector (1536 dimensions for text-embedding-3-small)
    """
    try:
        client = get_openai_client()
        response = client.embeddings.create(
            input=text[:8000],  # Limit text length
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error getting embedding: {e}")
        raise


def retrieve_context(query: str, collection: str, top_k: int = 3) -> str:
    """
    Retrieve relevant text chunks from vector database.
    
    Args:
        query: Search query
        collection: Collection name to search
        top_k: Number of results to retrieve
    
    Returns:
        Concatenated text from top-k results
    """
    try:
        client = get_qdrant_client()
        
        # Get query embedding
        query_vector = get_embedding(query)
        
        # Search in collection
        results = client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k
        )
        
        # Concatenate results
        contexts = []
        for result in results:
            if hasattr(result, 'payload') and 'text' in result.payload:
                contexts.append(result.payload['text'])
        
        combined = '\n\n'.join(contexts)
        logger.info(f"Retrieved {len(results)} chunks from {collection}, total {len(combined)} chars")
        return combined
        
    except UnexpectedResponse as e:
        logger.warning(f"Collection {collection} not found or empty: {e}")
        # Return empty string if collection doesn't exist yet
        return ""
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        raise


def check_collection_exists(collection: str) -> bool:
    """Check if a collection exists in Qdrant."""
    try:
        client = get_qdrant_client()
        collections = client.get_collections()
        return any(c.name == collection for c in collections.collections)
    except Exception:
        return False