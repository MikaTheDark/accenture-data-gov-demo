"""
generator_agent.py
Agent orienté 'Deliverables' : Produit des plans d'action, roadmaps et frameworks.
"""

from typing import Any, Dict, List

from loguru import logger
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

from config import LLM_MODEL
from src.retrieval import load_vectorstore


def _maybe_retrieve_context(question: str, k: int = 4) -> List[Document]:
    """Récupère du contexte si nécessaire pour ancrer la recommandation."""
    vs = load_vectorstore()
    retriever = vs.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )
    return retriever.invoke(question)


def run_generator_agent(question: str) -> Dict[str, Any]:
    """
    Produit un livrable consulting actionnable (Roadmap, Slide Structure, Framework).
    """
    logger.info("🧰 [GENERATOR] Création du livrable...")

    # On récupère un peu de contexte pour ne pas être hors-sol
    docs = _maybe_retrieve_context(question)
    context = "\n\n".join(d.page_content for d in docs) if docs else "Aucun document spécifique."

    system_prompt = """
    Vous êtes Directeur de Mission (Engagement Manager) chez Accenture.
    Le client vous sollicite pour structurer une démarche ou produire un plan d'action.
    
    VOTRE OBJECTIF :
    Produire un **Livrable Actionnable** et non une simple réponse textuelle.

    TYPES DE RÉPONSES ATTENDUES :
    - Si on demande un plan -> Fournir une **Roadmap** (Phase 1, Phase 2, Phase 3).
    - Si on demande une stratégie -> Fournir les **Piliers Stratégiques**.
    - Si on demande une présentation -> Fournir la **Structure du Deck** (Slide 1, Slide 2...).

    TON & STYLE :
    - Professionnel, Structuré, Orienté Résultat.
    - Utilisez du vocabulaire métier (Quick Wins, Target Operating Model, KPI, Governance).
    - Soyez force de proposition.
    """

    llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=0.5, # Un peu de créativité pour la structuration
    )

    user_prompt = (
        f"Demande du client : {question}\n\n"
        f"Contexte projet (si applicable) :\n{context}"
    )

    messages = [
        ("system", system_prompt),
        ("user", user_prompt),
    ]

    response = llm.invoke(messages)
    answer_text = response.content if hasattr(response, "content") else str(response)

    return {
        "agent": "Consulting Delivery Lead",
        "answer": answer_text,
        "docs": docs,
        "sources_text": "Recommandation basée sur les standards du cabinet et le contexte client.",
    }