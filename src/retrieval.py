"""
retrieval.py
Gère le chargement de Chroma et fournit les fonctions de récupération de documents.
Compatible LangChain 0.2.x et Chroma moderne.
"""

from __future__ import annotations

from typing import List

from loguru import logger
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from config import (
    CHROMA_DB_DIR,
    CHROMA_COLLECTION_NAME,
    MODEL_EMBEDDINGS,
)


# ================================
# SYSTEM PROMPT POUR LE RAG
# ================================
SYSTEM_PROMPT_RAG = """
Tu es un assistant expert en Data Governance.
Tu dois répondre uniquement à partir du document fourni par le RAG.
Si l'information n'est pas dans le document : dis-le clairement.
Structure ta réponse de manière claire, concise, avec un ton professionnel.
"""


def load_vectorstore() -> Chroma:
    """
    Charge la base vectorielle Chroma existante.
    """
    logger.info("📦 Chargement de la base vectorielle Chroma...")

    embeddings = OpenAIEmbeddings(model=MODEL_EMBEDDINGS)

    vs = Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_DIR,
    )

    logger.success("📚 Base vectorielle chargée avec succès.")
    return vs


def basic_retrieval(query: str, k: int = 4) -> List[Document]:
    """
    Fonction utilitaire simple pour tester la recherche.
    """
    vs = load_vectorstore()
    retriever = vs.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )

    docs = retriever.invoke(query)
    return docs
from langchain_core.documents import Document

def get_relevant_docs(question: str, k: int = 5) -> list[Document]:
    """
    Récupère les documents pertinents depuis Chroma pour une question donnée.
    Utilisé par le generator_agent et summary_agent.
    """
    vs = load_vectorstore()

    retriever = vs.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )

    docs = retriever.invoke(question)
    return docs


def format_sources(docs: list[Document]) -> str:
    """
    Formatte proprement les sources des documents.
    Permet aux agents d'afficher les sources.
    """
    if not docs:
        return "Aucune source."

    lines = []
    seen = set()

    for d in docs:
        src = d.metadata.get("source", "unknown")
        page = d.metadata.get("page", "?")
        key = (src, page)

        if key in seen:
            continue
        seen.add(key)

        lines.append(f"- {src} (page {page})")

    return "\n".join(lines)


if __name__ == "__main__":
    # Test manuel
    logger.info("🔧 Test du retrieval…")
    results = basic_retrieval("What is the purpose of client data safeguards?")
    print(f"{len(results)} documents trouvés.")
    for r in results:
        print("-----")
        print(r.page_content[:200])
        print(r.metadata)
        print("-----")
    logger.info("✅ Test de retrieval terminé.")