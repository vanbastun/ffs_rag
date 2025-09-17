import hashlib
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from tqdm import tqdm

# Add src to path to import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from rag_core.generation.openrouter_client import chat_with_openrouter


def generate_document_id(doc: dict[str, Any]) -> str:
    """Generate a unique document ID based on content"""
    combined = f"{doc['section']}-{doc['question']}-{doc['answer'][:10]}"
    hash_object = hashlib.md5(combined.encode())
    hash_hex = hash_object.hexdigest()
    document_id = hash_hex[:8]
    return document_id


def generate_questions(doc: dict[str, Any]) -> list[str]:
    """Generate 5 questions using OpenRouter API"""
    prompt_template = """
You emulate a fantasy player who's thinking to buy subscription.
Formulate 5 questions this student might ask based on a FAQ record. The record
should contain the answer to the questions, and the questions should be complete and not too short.
If possible, use as fewer words as possible from the record.

The record:

section: {section}
question: {question}
answer: {text}

Provide the output in parsable JSON without using code blocks:

["question1", "question2", ..., "question5"]
""".strip()

    prompt = prompt_template.format(
        section=doc["section"], question=doc["question"], text=doc["answer"]
    )

    try:
        response = chat_with_openrouter(prompt=prompt, model="google/gemini-2.5-flash-lite")

        # Parse JSON response from the content field
        content = response["choices"][0]["message"]["content"]
        questions = json.loads(content)
        return questions
    except Exception as e:
        print(f"Error generating questions for doc {doc['id']}: {e}")
        return [doc["question"]]  # Fallback to original question


def main() -> None:
    # Load FAQ data
    faq_path = Path("data/raw/faq_ffs.json")
    if not faq_path.exists():
        print("FAQ data not found. Please run parse_faq.py first.")
        return

    with open(faq_path, encoding="utf-8") as f:
        faq_data = json.load(f)

    print(f"Loaded {len(faq_data)} FAQ entries")

    # Add IDs to all documents
    for doc in faq_data:
        doc["id"] = generate_document_id(doc)

    # Filter out unwanted sections for question generation
    unwanted_sections = ["Common Abbreviations", "Common Terms"]
    documents = [doc for doc in faq_data if doc["section"] not in unwanted_sections]

    print(f"Total documents: {len(faq_data)}")
    print(
        f"Processing {len(documents)} documents for question generation (excluding abbreviations/terms)"
    )

    # Check for duplicate IDs across ALL documents
    hashes = defaultdict(list)
    for doc in faq_data:
        doc_id = doc["id"]
        hashes[doc_id].append(doc)

    duplicates = {doc_id: docs for doc_id, docs in hashes.items() if len(docs) > 1}
    if duplicates:
        print(f"Warning: Found {len(duplicates)} duplicate IDs")
        for doc_id, docs in list(duplicates.items())[:3]:  # Show first 3
            print(f"  ID {doc_id}: {len(docs)} documents")

    # Create prepared directory
    prepared_dir = Path("data/prepared")
    prepared_dir.mkdir(parents=True, exist_ok=True)

    # Generate questions for each document
    results = {}
    for doc in tqdm(documents, desc="Generating questions"):
        doc_id = doc["id"]
        if doc_id in results:
            continue

        questions = generate_questions(doc)
        results[doc_id] = questions

    # Prepare final data structure - include ALL documents with IDs
    prepared_data = []
    for doc in faq_data:
        doc_id = doc["id"]
        prepared_entry = {
            "id": doc_id,
            "section": doc["section"],
            "original_question": doc["question"],
            "answer": doc["answer"],
        }

        # Add generated questions only for documents we processed
        if doc_id in results:
            prepared_entry["generated_questions"] = results[doc_id]
        else:
            prepared_entry["generated_questions"] = []  # Empty for abbreviations/terms

        prepared_data.append(prepared_entry)

    # Save prepared data
    output_path = prepared_dir / "faq_prepared.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(prepared_data, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(prepared_data)} prepared FAQ entries to {output_path}")

    # Show sample
    if prepared_data:
        print("\nSample prepared entry:")
        sample = prepared_data[0]
        print(f"ID: {sample['id']}")
        print(f"Section: {sample['section']}")
        print(f"Original: {sample['original_question']}")
        print(f"Generated questions: {len(sample['generated_questions'])}")
        print(f"First generated: {sample['generated_questions'][0]}")


if __name__ == "__main__":
    main()
