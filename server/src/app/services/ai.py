from openai import OpenAI
from app.core.config import JINA_API_KEY, NVIDIA_API_KEY

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
        cleaned_text = text.replace("\n", " ").strip()
        response = self.jina.embeddings.create(
            model=self.jina_embedding_model,
            input=[cleaned_text],
        )
        if not response.data or not response.data[0].embedding:
            raise ValueError("Embedding values are missing from Jina response.")
        return list(response.data[0].embedding)

    def generate_response(self, prompt: str, model: str | None = None) -> str:
        """Generates LLM completions using NVIDIA NIM with robust error checking."""
        try:
            response = self.nvidia.chat.completions.create(
                model=model or self.nvidia_chat_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1024,
            )

            if not response.choices:
                raise ValueError("NVIDIA NIM returned no choices in response.")

            choice = response.choices[0]
            message = choice.message
            
            # Check for model refusal
            if hasattr(message, "refusal") and message.refusal:
                raise ValueError(f"NVIDIA NIM model refused the request: {message.refusal}")
                
            content = message.content
            if not content or not content.strip():
                finish_reason = getattr(choice, "finish_reason", "unknown")
                raise ValueError(
                    f"NVIDIA NIM returned empty content (finish_reason: {finish_reason}). "
                    "This usually indicates a content safety filter block or length limit."
                )
                
            return content.strip()
            
        except Exception as e:
            if "openai" in str(type(e)).lower() or "APIStatusError" in type(e).__name__:
                raise ValueError(f"NVIDIA NIM API Error: {str(e)}")
            raise e

    def close(self):
        self.jina.close()
        self.nvidia.close()

AI = AIClient()
