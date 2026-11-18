import math

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from app.core.config import JINA_API_KEY, NVIDIA_API_KEY


class AIServiceError(RuntimeError):
    """Raised when an external AI provider fails or returns an unusable response."""


class AIClient:
    def __init__(self):
        self.jina = OpenAI(
            base_url="https://api.jina.ai/v1",
            api_key=JINA_API_KEY,
        )
        self.nvidia = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=NVIDIA_API_KEY,
        )
        self.jina_embedding_model = "jina-embeddings-v3"
        self.nvidia_chat_model = "nvidia/nemotron-3.5-lightning-30b-a3b"

    def embed_text(self, text: str) -> list[float]:
        """Generates vector embeddings using Jina AI."""
        try:
            cleaned_text = text.replace("\n", " ").strip()
            response = self.jina.embeddings.create(
                model=self.jina_embedding_model,
                input=[cleaned_text],
            )
            if not response.data or not response.data[0].embedding:
                raise AIServiceError("Embedding provider returned no embedding.")

            embedding = [float(value) for value in response.data[0].embedding]
            if not embedding or not all(math.isfinite(value) for value in embedding):
                raise AIServiceError("Embedding provider returned an invalid embedding.")
            return embedding
        except AIServiceError:
            raise
        except Exception as exc:
            raise AIServiceError("Embedding provider request failed.") from exc

    def generate_response(
        self,
        messages: list[ChatCompletionMessageParam],
        model: str | None = None,
    ) -> str:
        """Generates LLM completions using NVIDIA NIM."""
        try:
            response = self.nvidia.chat.completions.create(
                model=model or self.nvidia_chat_model,
                messages=messages,
                temperature=0.2,
                max_tokens=1024,
            )

            if not response.choices:
                raise AIServiceError("Language model returned no choices.")

            choice = response.choices[0]
            message = choice.message
            if message is None:
                raise AIServiceError("Language model returned no message.")
            if getattr(message, "refusal", None):
                raise AIServiceError("Language model refused the request.")

            content = message.content
            if not isinstance(content, str) or not content.strip():
                raise AIServiceError("Language model returned empty content.")

            return content.strip()
        except AIServiceError:
            raise
        except Exception as exc:
            raise AIServiceError("Language model request failed.") from exc

    def close(self):
        errors = []
        for client in (self.jina, self.nvidia):
            try:
                client.close()
            except Exception as exc:
                errors.append(exc)
        if errors:
            raise RuntimeError("Could not close AI provider clients.") from errors[0]

AI = AIClient()
