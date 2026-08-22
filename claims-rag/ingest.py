"""Ingest claims-handling guidelines into the local vector store.

Embeddings via OpenAI; API key comes from the environment (OPENAI_API_KEY).
"""

from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

DOCS_DIR = Path(__file__).parent / "docs"
CHROMA_DIR = str(Path(__file__).parent / "chroma_db")


def main() -> None:
    docs = DirectoryLoader(str(DOCS_DIR), glob="**/*.md").load()
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=100
    ).split_documents(docs)
    Chroma.from_documents(
        chunks,
        OpenAIEmbeddings(model="text-embedding-3-small"),
        persist_directory=CHROMA_DIR,
    )
    print(f"Ingested {len(chunks)} chunks from {len(docs)} documents.")


if __name__ == "__main__":
    main()
