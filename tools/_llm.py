"""Shared Gemini client used by the tool functions in this package."""
import os
from functools import lru_cache

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set.")
    return genai.Client(api_key=api_key)
