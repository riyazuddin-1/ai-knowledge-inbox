# backend/api/controllers/query_controller.py
from fastapi import HTTPException
from services.ai import AI

from shared.memory import search_vector_store
from workers.chunk_embed.handler import generate_embedding


def answer_question(question: str):
  if not question.strip():
    raise HTTPException(status_code=400, detail="Question cannot be empty.")

  # 1. Embed user question using Gemini
  query_vector = generate_embedding(question)

  # 2. Retrieve top matching chunks from RAM
  matches = search_vector_store(query_vector, top_k=4)

  if not matches:
    return {
        "answer": (
            "Your knowledge inbox doesn't have any indexed content yet to"
            " answer this."
        ),
        "sources": [],
    }

  # 3. Build context block for the LLM
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

Question: {question}
Answer:"""

  # 4. Generate answer via Gemini 3.8 Flash
  response = AI.gemini.models.generate_content(
      model="gemini-3.8-flash",
      contents=prompt,
  )

  return {
      "answer": response.text,
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
