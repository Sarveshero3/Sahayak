# config.py
"""
Centralised constants for the Mental Well-Being Companion.
No sample CSV fallback: the file must already be present.
"""

import os
from pathlib import Path

# ---------- Paths ----------
BASE_DIR  = Path(__file__).resolve().parent
CSV_PATH  = BASE_DIR / "coping mechanism.csv"   # 👉 must exist
CHROMA_DIR = BASE_DIR / "chroma_db"

# ---------- Default model names (editable in the Streamlit sidebar) ----------
DEFAULT_CHAT_MODEL  = "mistral:latest"      # any chat-capable Ollama model
DEFAULT_EMBED_MODEL = "nomic-embed-text"    # any embed-capable Ollama model

# Convenience helper (optional): sanity-check at app start-up
def validate_paths():
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"CSV file not found at {CSV_PATH}. "
            "Please ensure 'coping mechanism.csv' is in the same folder."
        )
    CHROMA_DIR.mkdir(exist_ok=True)
