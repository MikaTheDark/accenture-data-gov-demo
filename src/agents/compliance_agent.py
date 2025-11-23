"""
compliance_agent.py
Analyse le document sous l’angle safeguards / sécurité / conformité / risques.
Version dynamique connectée à la Sidebar.
"""

from typing import Any, Dict, List

from loguru import logger
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

from config import LLM_MODEL
from src.retrieval import load_vectorstore


def _retrieve_compliance_context(question: str, k: int = 6) -> List[Document]:
    """Récupère les segments pertinents dans la vector DB."""
    vs = load_vectorstore()
    retriever = vs.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )
    return retriever.invoke(question)


def run_compliance_agent(
    question: str, 
    framework: str = "Général", 
    risk_level: str = "Medium"
) -> Dict[str, Any]:
    """
    Fournit une analyse compliance dynamique.
    Args:
        question: La question de l'utilisateur.
        framework: Le référentiel choisi (ex: EU AI Act, GDPR).
        risk_level: Le niveau d'appétence au risque (Low, Medium, High).
    """
    logger.info(f"🔐 [COMPLIANCE] Mode: {framework} | Risque: {risk_level}")

    # 1. Récupération du contexte (RAG)
    docs = _retrieve_compliance_context(question)
    context = "\n\n".join(d.page_content for d in docs)

    # 2. Construction du Prompt Dynamique (Prompt Engineering avancée)
    # On force l'IA à adopter la posture choisie dans la sidebar.
    system_prompt = f"""
    Tu es un auditeur Senior en conformité et sécurité des données (Risk & Compliance).
    
    PARAMÈTRES DE LA MISSION :
    - RÉFÉRENTIEL D'AUDIT : {framework}
    - NIVEAU DE VIGILANCE : {risk_level} (Impact sur la sévérité de tes recommandations).
    
    TA MISSION :
    1. Analyse la question de l'utilisateur en te basant UNIQUEMENT sur le contexte fourni ci-dessous.
    2. Identifie les écarts ou les contrôles nécessaires selon le référentiel {framework}.
    3. Si le risque est 'High', sois extrêmement strict et alarmiste. Si 'Low', sois pragmatique.
    
    STRUCTURE TA RÉPONSE :
    - 🛡️ **Analyse de Conformité ({framework})** : Synthèse directe.
    - ⚠️ **Risques Identifiés** : Liste des points d'attention (basés sur le texte).
    - ✅ **Recommandations** : Actions concrètes à mener.
    """

    llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=0.1, # Température basse pour la rigueur
    )

    messages = [
        ("system", system_prompt),
        (
            "user",
            f"QUESTION : {question}\n\nCONTEXTE DOCUMENTAIRE (Accenture/Source) :\n{context}",
        ),
    ]

    # 3. Exécution
    logger.info("🧠 [COMPLIANCE] Appel du LLM...")
    response = llm.invoke(messages)
    answer_text = response.content if hasattr(response, "content") else str(response)

    return {
        "agent": "Compliance Agent",
        "answer": answer_text,
        "docs": docs,
        "sources_text": f"Analyse croisée : Document interne vs Référentiel {framework}.",
    }