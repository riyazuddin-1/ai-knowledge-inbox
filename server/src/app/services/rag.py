from app.services.ai import AI
from app.core.similarity import search_similarity
from app.services.embedding import generate_embedding

def answer_question(question: str):
    cleaned_question = question.strip()
    if not cleaned_question:
        raise ValueError("Question cannot be empty.")

    # 1. Embed query vector
    query_vector = generate_embedding(cleaned_question)

    # 2. Search RAM similarity index
    matches = search_similarity(query_vector, top_k=4)

    if not matches:
        return {
            "answer": "Your knowledge inbox doesn't have any indexed content yet to answer this.",
            "sources": [],
        }

    context_blocks = []
    for i, m in enumerate(matches, 1):
        title = m.get("source_title") or f"Document #{m['content_id']}"
        context_blocks.append(f"[Source {i} - {title}]:\n{m['text']}")

    context_str = "\n\n".join(context_blocks)

    prompt = f"""You are a helpful AI Knowledge Assistant. Answer the user's question strictly using the provided context snippets below. 
If the answer is not contained within the context, state clearly that you do not have enough information in the saved notes to answer.
Cite your sources using [Source X] notation.

Context:
{context_str}

Question: {cleaned_question}
Answer:"""

    answer = AI.generate_response(prompt)

    return {
        "answer": answer,
        "sources": [
            {
                "content_id": m["content_id"],
                "title": m.get("source_title"),
                "source_url": m.get("source_url"),
                "snippet": m["text"],
                "relevance_score": round(m["score"], 3),
            }
            for m in matches
        ],
    }
