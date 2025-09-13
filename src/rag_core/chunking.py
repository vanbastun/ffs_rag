import re

# Compile patterns once for speed
_MD_SYMBOLS = re.compile(r"[#>*`_~\[\]\(\)!-]")
_WS = re.compile(r"\s+")


def simple_md_clean(text: str) -> str:
    """Remove basic markdown symbols and normalize whitespace.
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text with normalized whitespace
    """
    # Remove markdown symbols
    text = _MD_SYMBOLS.sub(" ", text)
    # Collapse all whitespace types into single spaces
    return _WS.sub(" ", text).strip()


def fixed_chunk(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks by words.
    
    Args:
        text: Input text to chunk
        size: Chunk length in tokens (words)
        overlap: Overlap between chunks in tokens
        
    Returns:
        List of text chunks
        
    Raises:
        ValueError: If size <= 0, overlap < 0, or overlap >= size
    """
    if size <= 0:
        raise ValueError("size must be positive")
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")

    tokens = text.split()
    step = size - overlap
    return [" ".join(tokens[i : i + size]) for i in range(0, len(tokens), step)]
