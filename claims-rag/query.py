"""Query the claims knowledge base (retrieval-augmented generation)."""

import sys
from pathlib import Path

from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

CHROMA_DIR = str(Path(__file__).parent / "chroma_db")

PROMPT = (
    "You are an assistant for Acme Insurance claims handlers. Answer the "
    "question using only the provided guideline excerpts. Cite the source "
    "document for every claim you make.\n\nExcerpts:\n{context}\n\n"
    "Question: {question}"
)


def main() -> None:
    question = " ".join(sys.argv[1:]) or "What is the deadline for water damage claims?"
    store = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
    )
    context = "\n---\n".join(
        doc.page_content for doc in store.similarity_search(question, k=4)
    )
    llm = ChatOpenAI(model="gpt-4o-mini")
    answer = llm.invoke(PROMPT.format(context=context, question=question))
    print(answer.content)


if __name__ == "__main__":
    main()
