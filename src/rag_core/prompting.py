from typing import Any

ANSWER_JSON_PROMPT = """You are a precise assistant.
Answer as JSON with fields: answer, citations (list of source_id), confidence (0..1).
Use only the context. If missing, answer: "I don't know".

Question: {q}

Context:
{ctx}
"""


def build_json_prompt(
    q: str, hits: list[tuple[str, dict[str, Any], float]], max_ctx_chars: int = 6000
) -> str:
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
