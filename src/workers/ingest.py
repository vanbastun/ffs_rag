import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from src.rag_core.config import Settings
from src.rag_core.embeddings import FastEmbedEmbeddings
from src.rag_core.bm25_qdrant import BM25QdrantClient
from src.rag_core.vectorstore_qdrant import QdrantVectorStore


def file_hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    s = Settings()
    vs = QdrantVectorStore(s.qdrant_url)
    bm25_client = BM25QdrantClient(s.qdrant_url)
    emb = FastEmbedEmbeddings(s.embedding_model)
    
    # Process FAQ prepared data
    faq_path = Path("data/prepared/faq_prepared.json")
    if faq_path.exists():
        print(f"Processing FAQ prepared data: {faq_path}")
        
        # Load FAQ data
        with open(faq_path, 'r', encoding='utf-8') as f:
            faq_data = json.load(f)
        
        print(f"Found {len(faq_data)} FAQ items")
        
        # Prepare documents for both dense and sparse vectors
        dense_documents = []
        bm25_documents = []
        
        for item in faq_data:
            # Create text for dense vectors (question + answer)
            text_content = f"Q: {item['original_question']}\nA: {item['answer']}"
            
            # Create metadata
            metadata = {
                "source_id": item["id"],
                "section": item["section"],
                "original_question": item["original_question"],
                "answer": item["answer"],
                "generated_questions": item["generated_questions"],
                "lang": "en",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            
            # For dense vectors
            dense_documents.append({
                "text": text_content,
                "metadata": metadata,
                "id": item["id"]
            })
            
            # For BM25 - use all questions (original + generated)
            all_questions = [item["original_question"]] + item["generated_questions"]
            for q in all_questions:
                bm25_documents.append({
                    "text": f"{q} {item['answer']}",  # Include answer for better matching
                    "id": f"{item['id']}_{q[:20]}",  # Unique ID for each question
                    "original_id": item["id"],
                    "question": q,
                    "answer": item["answer"],
                    "section": item["section"],
                    "lang": "en"
                })
        
        # Create document metadata for dense vectors
        meta_doc = {
            "source_id": "faq_prepared",
            "title": "Fantasy Football Scout FAQ (Prepared)",
            "uri": str(faq_path),
            "lang": "en",
            "version": 1,
            "hash": file_hash(faq_path),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        
        # Upsert document for dense vectors
        doc_id = vs.upsert_document(meta_doc)
        
        # Prepare texts and metadata for dense vector storage
        texts = [doc["text"] for doc in dense_documents]
        metas = [doc["metadata"] for doc in dense_documents]
        
        # Generate embeddings for dense vectors
        print("Generating embeddings for dense vectors...")
        vecs = emb.encode(texts)
        
        # Insert chunks into dense vector store
        print("Inserting chunks into dense vector store...")
        vs.insert_chunks(doc_id, texts, metas, vecs)
        
        # Insert documents into BM25 collection
        print("Inserting documents into BM25 collection...")
        bm25_client.upsert_documents(bm25_documents)
        
        print(f"Successfully processed {len(faq_data)} FAQ items")
        print(f"Created {len(dense_documents)} dense vectors")
        print(f"Created {len(bm25_documents)} BM25 documents")
    else:
        print(f"FAQ prepared file not found: {faq_path}")
    
    print("Ingest completed")


if __name__ == "__main__":
    main()
