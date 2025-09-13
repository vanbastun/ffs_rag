import hashlib
from datetime import datetime, timezone
from pathlib import Path

from src.rag_core.config import Settings
from src.rag_core.embeddings import FastEmbedEmbeddings
from src.rag_core.faq_parser import FAQParser
from src.rag_core.vectorstore_qdrant import QdrantVectorStore


def file_hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    s = Settings()
    vs = QdrantVectorStore(s.qdrant_url)
    emb = FastEmbedEmbeddings(s.embedding_model)
    parser = FAQParser()
    
    # Process FAQ file
    faq_path = Path("data/raw/faq_ffs.txt")
    if faq_path.exists():
        print(f"Processing FAQ file: {faq_path}")
        
        # Parse FAQ items
        faq_items = parser.parse_faq_file(str(faq_path))
        print(f"Found {len(faq_items)} FAQ items")
        
        # Convert to chunks
        chunks_data = parser.faq_items_to_chunks(faq_items)
        
        # Create document metadata
        meta_doc = {
            "source_id": "faq_ffs",
            "title": "Fantasy Football Scout FAQ",
            "uri": str(faq_path),
            "lang": "en",
            "version": 1,
            "hash": file_hash(faq_path),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        
        # Upsert document
        doc_id = vs.upsert_document(meta_doc)
        
        # Prepare texts and metadata for vector storage
        texts = [chunk["text"] for chunk in chunks_data]
        metas = [chunk["metadata"] for chunk in chunks_data]
        
        # Generate embeddings
        print("Generating embeddings...")
        vecs = emb.encode(texts)
        
        # Insert chunks into vector store
        print("Inserting chunks into vector store...")
        vs.insert_chunks(doc_id, texts, metas, vecs)
        
        print(f"Successfully processed {len(faq_items)} FAQ items")
    else:
        print(f"FAQ file not found: {faq_path}")
    
    print("Ingest completed")


if __name__ == "__main__":
    main()
