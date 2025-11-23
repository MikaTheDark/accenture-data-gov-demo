"""
summary_agent.py
Agent spécialisé dans la production de notes de synthèse exécutives (Executive Summaries).
"""

from typing import Any, Dict, List

from loguru import logger
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

from config import LLM_MODEL
from src.retrieval import load_vectorstore


def _pick_docs_for_summary(question: str, max_docs: int = 7) -> List[Document]:
    """Sélectionne les passages clés pour la synthèse."""
    vs = load_vectorstore()
    retriever = vs.as_retriever(
        search_type="similarity",
        search_kwargs={"k": max_docs},
    )
    return retriever.invoke(question)


def run_summary_agent(question: str) -> Dict[str, Any]:
    """
    Produit une synthèse niveau 'Comité Exécutif' (CODIR).
    """
    logger.info("📝 [SUMMARY] Rédaction de la note de synthèse...")

    docs = _pick_docs_for_summary(question)
    context = "\n\n".join(d.page_content for d in docs)

    # Prompt "Consultant Senior"
    system_prompt = """
    Vous êtes Manager chez Accenture Strategy.
    Votre mission est de rédiger une **Note de Synthèse Executive** (Executive Summary) destinée au Comité de Direction (CODIR) du client.

    CONSIGNES DE RÉDACTION :
    1. **Style Direct & Impactant** : Allez à l'essentiel. Pas de phrases de remplissage.
    2. **Structure "Top-Down"** : Commencez par le message clé (Key Takeaway), puis détaillez.
    3. **Format** : Utilisez des titres, du gras pour les concepts clés, et des bullet points.
    4. **Source** : Basez-vous UNIQUEMENT sur les éléments factuels du contexte fourni.

    STRUCTURE ATTENDUE :
    - 💡 **L'Essentiel en 3 lignes** (TL;DR)
    - 🔑 **Points Clés de l'Analyse** (Structuré par thèmes)
    - ⚠️ **Points de Vigilance / Risques** (Si mentionnés dans le texte)
    """

    llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=0.2, # Faible température pour la fidélité
    )

    user_prompt = (
        f"Sujet de la demande : {question}\n\n"
        f"CONTEXTE DOCUMENTAIRE BRUT :\n{context}"
    )

    messages = [
        ("system", system_prompt),
        ("user", user_prompt),
    ]

    response = llm.invoke(messages)
    answer_text = response.content if hasattr(response, "content") else str(response)

    return {
        "agent": "Executive Summary Lead",
        "answer": answer_text,
        "docs": docs,
        "sources_text": "Synthèse consolidée des documents stratégiques.",
    }