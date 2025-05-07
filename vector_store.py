# vector_store.py
import os
from pathlib import Path

from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

from config import CHROMA_DIR
from data_utils import load_documents


def get_vectordb(embed_model: str) -> Chroma:
    """
    Build (or load) a persistent Chroma vector store
    using the specified Ollama embed model.

    • CHROMA_DIR remains a pathlib.Path in config.py.
    • We cast it to str only when we pass it to Chroma,
      because chromadb expects a plain string.
    """
    embeddings = OllamaEmbeddings(model=embed_model)

    # ── Ensure the persistence directory exists ──────────────────────────────
    persist_dir = str(CHROMA_DIR)           # ← cast Path → str for Chroma
    Path(persist_dir).mkdir(parents=True, exist_ok=True)

    # ── Create collection on first run ───────────────────────────────────────
    if not os.listdir(persist_dir):         # empty → nothing indexed yet
        vectordb = Chroma.from_documents(
            load_documents(),
            embeddings,
            persist_directory=persist_dir,
        )
        vectordb.persist()

    # ── Return a handle to the (possibly newly-created) store ────────────────
    return Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
    )
