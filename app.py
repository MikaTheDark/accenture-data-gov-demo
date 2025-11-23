"""
app.py
Point d'entrée de l'application Data Governance Intelligence.
Version Finale : Consulting Edition
"""

from __future__ import annotations

import time
from typing import Any, Dict, Literal

import streamlit as st
from loguru import logger

# Import des configurations et modules locaux
from config import PROJECT_NAME
from src.ui import inject_global_css, render_header, render_message
from src.agents import (
    run_rag_agent,
    run_summary_agent,
    run_compliance_agent,
    run_governance_agent,
    run_generator_agent,
)

# --- DÉFINITION DES TYPES ---
AgentName = Literal[
    "auto",
    "rag",
    "summary",
    "compliance",
    "governance",
    "generator",
]

# --- GESTION DE L'ÉTAT (SESSION STATE) ---
def _init_session_state() -> None:
    """Initialise les variables de session si elles n'existent pas."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                # Texte brut nettoyé pour éviter les bugs d'affichage HTML
                "content": "Bonjour ! Je suis votre assistant spécialisé en Gouvernance de Données. "
                           "Je peux analyser le document Accenture, vérifier la conformité (AI Act/RGPD) "
                           "ou générer des plans d'action stratégiques. Comment puis-je vous aider ?",
                "agent": "System"
            }
        ]
    if "last_agent" not in st.session_state:
        st.session_state.last_agent = None

# --- LOGIQUE DE ROUTAGE (CERVEAU) ---
def detect_agent(user_input: str, manual_choice: str) -> AgentName:
    """
    Détermine quel agent activer en fonction du choix utilisateur ou des mots-clés.
    """
    if manual_choice != "auto":
        return manual_choice

    text = user_input.lower()
    
    # Heuristiques simples pour le mode Auto
    if any(k in text for k in ["résume", "synthèse", "summary", "tl;dr"]):
        return "summary"
    if any(k in text for k in ["conformité", "compliance", "risque", "rgpd", "ai act", "security", "règlement"]):
        return "compliance"
    if any(k in text for k in ["gouvernance", "data owner", "steward", "qualité", "lineage", "mesh", "architecture"]):
        return "governance"
    if any(k in text for k in ["plan", "action", "slide", "présentation", "email", "stratégie", "migration"]):
        return "generator"
    
    return "rag"  # Par défaut : Recherche documentaire classique

def run_agent_engine(user_input: str, agent: AgentName, framework: str, risk: str) -> Dict[str, Any]:
    """
    Orchestrateur : Exécute l'agent choisi en injectant le contexte métier (Framework, Risque).
    """
    logger.info(f"🚀 Execution Agent: {agent} | Context: {framework}, {risk}")
    
    if agent == "rag":
        return run_rag_agent(user_input)
    elif agent == "summary":
        return run_summary_agent(user_input)
    elif agent == "compliance":
        return run_compliance_agent(user_input, framework=framework, risk_level=risk)
    elif agent == "governance":
        return run_governance_agent(user_input, risk_level=risk)
    elif agent == "generator":
        return run_generator_agent(user_input)
    
    return run_rag_agent(user_input)

# --- FONCTION PRINCIPALE (UI) ---
def main() -> None:
    # 1. Configuration de la page
    st.set_page_config(
        page_title=f"{PROJECT_NAME} | Consulting",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 2. Injection du style et initialisation
    inject_global_css()
    _init_session_state()

    # --- SIDEBAR (PARAMÈTRES) ---
    with st.sidebar:
        st.markdown("### 🎛️ Panneau de Contrôle")
        
        st.markdown("**Mode Opératoire**")
        agent_choice_label = st.selectbox(
            "Sélectionnez un agent spécialisé :",
            [
                "⚡ Auto-Detection (Smart)",
                "📄 RAG (Document Knowledge)",
                "📝 Synthétiseur (Executive Summary)",
                "⚖️ Compliance Officer (Risk)",
                "🏛️ Governance Architect (Strategy)",
                "💼 Consulting Generator (Deliverables)"
            ],
            index=0
        )
        
        # Mapping du label vers le nom technique
        mapping = {
            "⚡ Auto-Detection (Smart)": "auto",
            "📄 RAG (Document Knowledge)": "rag",
            "📝 Synthétiseur (Executive Summary)": "summary",
            "⚖️ Compliance Officer (Risk)": "compliance",
            "🏛️ Governance Architect (Strategy)": "governance",
            "💼 Consulting Generator (Deliverables)": "generator"
        }
        manual_agent = mapping[agent_choice_label]

        st.divider()
        
        st.markdown("**Paramètres de Simulation**")
        # Ces variables seront passées aux agents
        selected_framework = st.selectbox("Référentiel de Conformité", ["EU AI Act", "GDPR", "NIST AI RMF", "ISO 42001"], index=0)
        selected_risk = st.selectbox("Niveau de risque", ["Low (Agile)", "Medium (Standard)", "High (Critical)"], index=1)
        
        st.divider()
        
        # Bouton Reset
        if st.button("🗑️ Nouvelle Session", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.divider()

        # 🔥 Placeholder pour le téléchargement (rempli à la fin du script)
        download_placeholder = st.empty()

        st.markdown(
            """
            <div style='margin-top: 2rem; font-size: 0.75rem; color: #64748b; text-align: center;'>
                Enterprise Data Governance Tool v1.0<br>
                Powered by LangChain & OpenAI
            </div>
            """, 
            unsafe_allow_html=True
        )

    # --- ZONE PRINCIPALE ---
    render_header(
        title="Data Governance Intelligence",
        subtitle="Assistant IA Multi-Agents pour la conformité et la stratégie de données"
    )

    # Affichage de l'historique de chat
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            render_message(
                role=msg["role"],
                content=msg["content"],
                agent_name=msg.get("agent"),
                sources=msg.get("sources")
            )

    # --- SCÉNARIOS CONSULTING (BOUTONS RAPIDES) ---
    st.write("") # Spacer pour aérer
    cols = st.columns(3)
    prompt_trigger = None
    
    # Scénario 1 : Migration Cloud
    if cols[0].button("☁️ Migration Cloud Complex", use_container_width=True):
        prompt_trigger = (
            "Je dois piloter une migration Cloud à grande échelle pour une institution financière "
            "avec des données sensibles (PII). Propose une stratégie de migration (ex: approche 7Rs) "
            "en détaillant les étapes de sécurisation des données et la gestion du risque hybride."
        )

    # Scénario 2 : Conformité Internationale
    if cols[1].button("🌍 Transfert Data EU/US", use_container_width=True):
        prompt_trigger = (
            "Quelles sont les exigences techniques et juridiques pour transférer des données clients "
            "de l'Europe vers les États-Unis ? Liste les contrôles de sécurité obligatoires (chiffrement, BYOK) "
            "et les implications pour la souveraineté des données."
        )

    # Scénario 3 : Architecture Data Mesh
    if cols[2].button("🕸️ Gouvernance Data Mesh", use_container_width=True):
        prompt_trigger = (
            "Nous passons d'un Data Lake monolithique à une architecture Data Mesh distribuée. "
            "Comment doit évoluer notre modèle de gouvernance ? Définis les nouvelles responsabilités "
            "des Domaines vs l'équipe Plateforme centrale."
        )

    # Barre de saisie utilisateur
    user_input = st.chat_input("Ex: Quels sont les pré-requis sécurité pour une architecture Serverless ?")
    
    # Logique de déclenchement (Soit bouton, soit texte)
    final_input = prompt_trigger if prompt_trigger else user_input

    if final_input:
        # 1. Afficher le message utilisateur tout de suite
        st.session_state.messages.append({"role": "user", "content": final_input})
        render_message(role="user", content=final_input)

        # 2. Détection et Exécution de l'IA
        target_agent = detect_agent(final_input, manual_agent)
        
        # Feedback visuel avec st.status
        with st.status(f"🤖 L'agent **{target_agent.upper()}** analyse votre demande...", expanded=True) as status:
            try:
                # Petite latence simulée pour l'effet UX
                time.sleep(0.3)
                
                if target_agent == "compliance":
                    st.write(f"⚖️ Vérification selon le référentiel : **{selected_framework}**...")
                elif target_agent == "governance":
                    st.write(f"🏛️ Application du niveau de risque : **{selected_risk}**...")
                else:
                    st.write("🔍 Analyse sémantique de la requête...")
                
                # APPEL RÉEL À L'AGENT (Wiring final)
                result = run_agent_engine(
                    user_input=final_input, 
                    agent=target_agent, 
                    framework=selected_framework, 
                    risk=selected_risk
                )
                
                answer = result.get("answer", "Désolé, je n'ai pas pu générer de réponse.")
                agent_used = result.get("agent", target_agent).capitalize()
                sources = result.get("sources_text", None)

                st.write("✅ Génération terminée.")
                status.update(label="Réponse générée avec succès", state="complete", expanded=False)

                # 3. Sauvegarde dans l'historique
                msg_data = {
                    "role": "assistant",
                    "content": answer,
                    "agent": f"{agent_used}",
                    "sources": sources
                }
                st.session_state.messages.append(msg_data)
                
                # 4. Affichage de la réponse IA
                render_message(role="assistant", content=answer, agent_name=f"{agent_used}", sources=sources)

            except Exception as e:
                logger.exception("Erreur critique")
                status.update(label="Erreur système", state="error")
                st.error(f"Une erreur est survenue : {str(e)}")

    # --- GÉNÉRATION DU RAPPORT (Update dynamique) ---
    # On reconstruit le log complet ici pour inclure le tout dernier message échangé
    full_log = ""
    for msg in st.session_state.messages:
        role_label = "CLIENT" if msg["role"] == "user" else f"EXPERT ACCENTURE ({msg.get('agent', 'System')})"
        full_log += f"\n\n{'='*30}\n{role_label}\n{'='*30}\n{msg['content']}\n"
    
    # On remplit le placeholder vide créé au début dans la sidebar
    with download_placeholder:
        st.download_button(
            label="📥 Télécharger le Rapport Complet",
            data=full_log,
            file_name="rapport_audit_accenture.txt",
            mime="text/plain",
            use_container_width=True
        )

if __name__ == "__main__":
    main()