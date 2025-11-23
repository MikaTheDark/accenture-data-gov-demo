"""
rag_agent.py
Agent généraliste qui interroge la base de connaissances avec une posture de Consultant.
"""

from typing import Any, Dict, List

from loguru import logger
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

from config import LLM_MODEL
from src.retrieval import load_vectorstore

def _retrieve_docs(question: str, k: int = 5) -> List[Document]:
    vs = load_vectorstore()
    retriever = vs.as_retriever(search_kwargs={"k": k})
    return retriever.invoke(question)

def run_rag_agent(question: str) -> Dict[str, Any]:
    """
    Répond aux questions sur les documents avec un ton professionnel.
    """
    logger.info("🔍 [RAG AGENT] Recherche d'informations...")

    # 1. Retrieval
    docs = _retrieve_docs(question)
    context = "\n\n".join(d.page_content for d in docs)

    if not context:
        return {
            "agent": "Knowledge Base",
            "answer": "Après analyse de vos documents internes, nous n'avons trouvé aucune information spécifique à ce sujet. Souhaitez-vous élargir la recherche aux standards du marché ?",
            "docs": [],
            "sources_text": ""
        }

    # 2. Prompt "Consultant Knowledge"
    system_prompt = """
    Vous êtes un Consultant Senior chez Accenture, expert en analyse documentaire.
    Votre mission est de synthétiser les informations présentes dans la base de connaissance du client.

    CONSIGNES :
    1. Répondez UNIQUEMENT en vous basant sur le CONTEXTE fourni ci-dessous.
    2. Si l'information n'est pas dans le contexte, dites-le clairement ("Nos documents actuels ne couvrent pas ce point...").
    3. Adoptez un ton professionnel, synthétique et précis.
    4. Citez vos sources quand c'est possible (ex: "Selon la section Sécurité...").
    """

    llm = ChatOpenAI(model=LLM_MODEL, temperature=0)

    messages = [
        ("system", system_prompt),
        ("user", f"Question du client : {question}\n\nCONTEXTE EXTRAIT :\n{context}"),
    ]

    # 3. Generation
    response = llm.invoke(messages)
    answer = response.content if hasattr(response, "content") else str(response)

    return {
        "agent": "Knowledge Base Analyst",
        "answer": answer,
        "docs": docs,
        "sources_text": "Extraits de la base documentaire client (Accenture Data Cloud POV).",
    }