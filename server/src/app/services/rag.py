from openai.types.chat import ChatCompletionMessageParam

from app.services.ai import AI
from app.core.memory import search_similarity
from app.services.embedding import generate_embedding
from app.core.tokenization import count_tokens


MAX_INPUT_TOKENS = 7168
SYSTEM_MESSAGE = """You are a helpful AI Knowledge Assistant. Answer the user's latest question using the provided saved-note context and conversation history. If the context does not contain the answer, say that you do not have enough information in the saved notes. Cite sources using [Source X] notation."""


def _build_messages(
    question: str,
    history: list[dict[str, str]],
    matches: list[dict],
) -> tuple[list[ChatCompletionMessageParam], list[dict]]:
    selected_matches = list(matches)
    selected_history = list(history)

    while True:
        context_blocks = []
        for index, match in enumerate(selected_matches, 1):
            title = (match.get("source_title") or f"Document #{match['content_id']}")[:200]
            context_blocks.append(f"[Source {index} - {title}]:\n{match['text']}")

        context = "\n\n".join(context_blocks)
        user_content = (
            f"Context:\n{context}\n\n"
            f"Question: {question}"
        )
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": SYSTEM_MESSAGE},
        ]
        for message in selected_history:
            if message["role"] == "user":
                messages.append({"role": "user", "content": message["content"]})
            else:
                messages.append(
                    {"role": "assistant", "content": message["content"]}
                )
        messages.append({"role": "user", "content": user_content})
        message_contents = [
            SYSTEM_MESSAGE,
            *(message["content"] for message in selected_history),
            user_content,
        ]
        token_count = sum(count_tokens(content) + 4 for content in message_contents) + 2
        if token_count <= MAX_INPUT_TOKENS:
            return messages, selected_matches
        if selected_history:
            if len(selected_history) > 1:
                del selected_history[:2]
            else:
                selected_history.pop(0)
        elif len(selected_matches) > 1:
            selected_matches.pop()
        else:
            raise ValueError("Question and retrieved context exceed the model input limit.")


def answer_question(question: str, history: list[dict[str, str]] | None = None):
    cleaned_question = question.strip()
    if not cleaned_question:
        raise ValueError("Question cannot be empty.")
    if count_tokens(cleaned_question) > MAX_INPUT_TOKENS:
        raise ValueError("Question exceeds the model input limit.")

    query_vector = generate_embedding(cleaned_question)
    matches = search_similarity(query_vector, top_k=4)

    if not matches:
        return {
            "answer": "Your knowledge inbox doesn't have any indexed content yet to answer this.",
            "sources": [],
        }

    messages, selected_matches = _build_messages(
        question=cleaned_question,
        history=history or [],
        matches=matches,
    )
    answer = AI.generate_response(messages)

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
            for m in selected_matches
        ],
    }
