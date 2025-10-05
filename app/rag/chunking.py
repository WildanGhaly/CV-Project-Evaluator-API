"""
Text chunking utilities for RAG system.
"""
import re
from typing import List


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks for better retrieval.
    
    Args:
        text: Input text to chunk
        chunk_size: Target chunk size in characters
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    if not text or len(text) <= chunk_size:
        return [text] if text else []
    
    # Clean up text
    text = re.sub(r'\s+', ' ', text).strip()
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # If not at the end, try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings within the last 100 chars of chunk
            search_start = max(start + chunk_size - 100, start)
            sentence_end = max(
                text.rfind('. ', search_start, end),
                text.rfind('! ', search_start, end),
                text.rfind('? ', search_start, end),
                text.rfind('\n', search_start, end)
            )
            if sentence_end > start:
                end = sentence_end + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap
        if start < 0:
            start = 0
    
    return chunks


def chunk_by_paragraphs(text: str, max_chunk_size: int = 1000) -> List[str]:
    """
    Chunk text by paragraphs, combining small paragraphs.
    
    Args:
        text: Input text to chunk
        max_chunk_size: Maximum chunk size in characters
    
    Returns:
        List of text chunks
    """
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    current_chunk = []
    current_size = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        para_size = len(para)
        
        # If single paragraph is too large, split it
        if para_size > max_chunk_size:
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            # Split large paragraph
            sub_chunks = chunk_text(para, chunk_size=max_chunk_size, overlap=50)
            chunks.extend(sub_chunks)
        else:
            # Add to current chunk if it fits
            if current_size + para_size + 2 <= max_chunk_size:  # +2 for newlines
                current_chunk.append(para)
                current_size += para_size + 2
            else:
                # Start new chunk
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_size = para_size
    
    # Add remaining chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks
