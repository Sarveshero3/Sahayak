# data_utils.py
import pandas as pd
from langchain.schema import Document
from config import CSV_PATH

def load_documents() -> list[Document]:
    """
    Read the coping-mechanism CSV (auto-creating it if missing) and return
    a list of LangChain Document objects.
    """
    
    df = pd.read_csv(CSV_PATH)

    docs: list[Document] = []
    for _, row in df.iterrows():
        content = (
            f"Exercise: {row['exercise']}\n"
            f"Category: {row['category']}\n"
            f"Duration: {row['duration']}\n"
            f"Problems: {row['problems']}\n"
            f"Instructions: {row['instructions']}"
        )
        docs.append(Document(page_content=content, metadata=row.to_dict()))

    return docs
