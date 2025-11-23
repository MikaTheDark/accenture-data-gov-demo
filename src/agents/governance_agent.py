"""
governance_agent.py
Agent expert en Data Governance & Data Strategy (Vision Accenture).
"""

from typing import Any, Dict

from loguru import logger
from langchain_openai import ChatOpenAI

from config import LLM_MODEL

def run_governance_agent(question: str, risk_level: str = "Medium") -> Dict[str, Any]:
    """
    Répond avec la vision stratégique d'un Directeur Data Strategy.
    """
    logger.info(f"📘 [GOVERNANCE] Démarrage... (Risk Level: {risk_level})")

    system_prompt = f"""
    Vous êtes Directeur "Data & AI Strategy" chez Accenture.
    Vous ne donnez pas de cours théoriques, vous donnez des conseils stratégiques applicables aux grandes entreprises.

    CONTEXTE CLIENT :
    Le client a un profil de risque : {risk_level}.
    
    VOTRE POSTURE :
    - Parlez de "Transformation", de "Data Democratization" et de "Valeur".
    - Utilisez un vocabulaire Corporate (Stakeholders, Roadmap, KPI, ROI).
    - Utilisez "Nous" et faites référence aux "Best Practices du marché".
    - Soyez structuré : Contexte > Enjeux > Roadmap.

    Si la question porte sur un concept (ex: Data Mesh), expliquez-le non pas comme un prof, 
    mais comme une opportunité de transformation pour l'entreprise.
    """

    llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=0.5, # Plus créatif pour la stratégie
    )

    messages = [
        ("system", system_prompt),
        ("user", question),
    ]

    response = llm.invoke(messages)
    answer_text = response.content if hasattr(response, "content") else str(response)

    return {
        "agent": "Data Strategy Director",
        "answer": answer_text,
        "docs": [],
        "sources_text": "Expertise Accenture Strategy & Consulting.",
    }