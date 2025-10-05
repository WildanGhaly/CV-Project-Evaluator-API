"""
Document ingestion script for RAG system.
Processes system documents and stores them in Qdrant vector database.
"""
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.utils.pdf import extract_text
from app.rag.chunking import chunk_by_paragraphs
from app.rag.retrieve import get_embedding, get_qdrant_client
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_DOCS_PATH = Path("data/system_docs")


def ingest_document(file_path: Path, collection_name: str, client: QdrantClient) -> int:
    """
    Ingest a single document into vector database.
    
    Args:
        file_path: Path to document file
        collection_name: Target collection name
        client: Qdrant client instance
    
    Returns:
        Number of chunks ingested
    """
    logger.info(f"Ingesting {file_path.name} into {collection_name}")
    
    # Extract text
    if file_path.suffix.lower() == '.pdf':
        text = extract_text(str(file_path))
    else:
        text = file_path.read_text(encoding='utf-8')
    
    if not text.strip():
        logger.warning(f"Empty document: {file_path.name}")
        return 0
    
    # Chunk text
    chunks = chunk_by_paragraphs(text, max_chunk_size=800)
    logger.info(f"Created {len(chunks)} chunks from {file_path.name}")
    
    # Create embeddings and points
    points = []
    for i, chunk in enumerate(chunks):
        try:
            embedding = get_embedding(chunk)
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "text": chunk,
                    "source": file_path.name,
                    "chunk_index": i
                }
            )
            points.append(point)
        except Exception as e:
            logger.error(f"Error creating embedding for chunk {i}: {e}")
            continue
    
    # Upsert to collection
    if points:
        client.upsert(collection_name=collection_name, points=points)
        logger.info(f"Ingested {len(points)} chunks from {file_path.name}")
    
    return len(points)


def create_collection(client: QdrantClient, collection_name: str, vector_size: int = 1536):
    """Create a collection if it doesn't exist."""
    try:
        collections = client.get_collections()
        if any(c.name == collection_name for c in collections.collections):
            logger.info(f"Collection {collection_name} already exists, recreating...")
            client.delete_collection(collection_name)
        
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
        logger.info(f"Created collection: {collection_name}")
    except Exception as e:
        logger.error(f"Error creating collection {collection_name}: {e}")
        raise


def run():
    """Main ingestion function."""
    logger.info("Starting document ingestion...")
    
    try:
        client = get_qdrant_client()
        
        # Ingest job descriptions
        logger.info("\n=== Ingesting Job Descriptions ===")
        create_collection(client, "job_descriptions")
        jd_dir = SYSTEM_DOCS_PATH / "job_descriptions"
        total_chunks = 0
        if jd_dir.exists():
            for file_path in jd_dir.glob("*"):
                if file_path.is_file() and file_path.suffix in ['.txt', '.pdf']:
                    total_chunks += ingest_document(file_path, "job_descriptions", client)
        logger.info(f"Job descriptions: {total_chunks} chunks total")
        
        # Ingest case study brief
        logger.info("\n=== Ingesting Case Study Brief ===")
        create_collection(client, "case_study")
        case_brief_files = list(SYSTEM_DOCS_PATH.glob("case_study_brief.*"))
        total_chunks = 0
        for file_path in case_brief_files:
            if file_path.suffix in ['.txt', '.pdf']:
                total_chunks += ingest_document(file_path, "case_study", client)
        logger.info(f"Case study: {total_chunks} chunks total")
        
        # Ingest scoring rubrics
        logger.info("\n=== Ingesting Scoring Rubrics ===")
        create_collection(client, "scoring_rubrics")
        rubric_files = list(SYSTEM_DOCS_PATH.glob("*_rubric.*"))
        total_chunks = 0
        for file_path in rubric_files:
            if file_path.suffix in ['.txt', '.pdf']:
                total_chunks += ingest_document(file_path, "scoring_rubrics", client)
        logger.info(f"Scoring rubrics: {total_chunks} chunks total")
        
        logger.info("\n=== Ingestion Complete ===")
        logger.info("All documents have been processed and stored in vector database")
        
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        raise


if __name__ == "__main__":
    run()