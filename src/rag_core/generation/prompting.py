from typing import Any

ANSWER_JSON_PROMPT = """You are a precise assistant. You MUST respond with valid JSON only.

Answer the QUESTION based on the CONTEXT from the FAQ database.
Use only the facts from the CONTEXT when answering the QUESTION.

Your response must be valid JSON with exactly these fields:
- "answer": string (your answer to the question)
- "citations": array of strings (list of source_id values from the context)
- "confidence": number between 0 and 1 (how confident you are in your answer)

Example response format:
{{
  "answer": "Your answer here",
  "citations": ["source_id_1", "source_id_2"],
  "confidence": 0.8
}}

Question: {q}

Context:
{ctx}

Respond with JSON only:"""


def build_json_prompt(
    q: str, hits: list[tuple[str, dict[str, Any], float]], max_ctx_chars: int = 6000
) -> str:
    """Build JSON prompt from query and retrieved hits.

    Args:
        q: User question/query
        hits: List of (text, metadata, score) tuples from retrieval
        max_ctx_chars: Maximum characters for context section

    Returns:
        Formatted prompt string ready for LLM
    """
    ctx_blocks = []
    total_len = 0

    for text, meta, score in hits:
        src_id = meta.get("source_id", "unknown")
        block = f"[id={src_id} score={score:.3f}] {text}\n"
        block_len = len(block)
        if total_len + block_len > max_ctx_chars:
            break
        ctx_blocks.append(block)
        total_len += block_len

    return ANSWER_JSON_PROMPT.format(q=q, ctx="".join(ctx_blocks))
