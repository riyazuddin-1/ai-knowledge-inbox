from google import genai
from shared.config.gemini import GEMINI_API_KEY

class AI:
    gemini: genai.Client

    @classmethod
    def init(cls):
        cls.gemini = genai.Client(api_key=GEMINI_API_KEY)

    @classmethod
    def close(cls):
        if cls.gemini:
            cls.gemini.close()
