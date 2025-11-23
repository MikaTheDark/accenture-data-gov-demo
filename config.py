"""
config.py
Configuration centralisée : Gestion hybride (Local .env / Cloud Streamlit Secrets).
Supporte GPT-5.1 comme demandé.
Correction : Ajout des alias de compatibilité pour éviter les ImportError.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from loguru import logger

# Chargement du .env en local (ne fait rien si le fichier n'existe pas sur le Cloud)
load_dotenv()

def get_secret(key_name: str, default: str = None) -> str | None:
    """
    Récupère une clé de configuration de manière robuste :
    1. Vérifie les variables d'environnement (OS)
    2. Vérifie les secrets Streamlit (st.secrets)
    3. Renvoie la valeur par défaut sinon
    """
    # 1. Priorité aux variables d'environnement (Local & Docker)
    value = os.getenv(key_name)
    if value:
        return value
    
    # 2. Fallback sur Streamlit Secrets (Déploiement Cloud)
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except FileNotFoundError:
        pass # Pas de fichier secrets.toml, c'est normal en local
    except Exception:
        pass 

    return default

# ============================
#   PROJECT INFO
# ============================
PROJECT_NAME = "Data Governance Intelligence"

# ============================
#   API KEYS
# ============================
OPENAI_API_KEY = get_secret("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    # On ne lève une erreur que si on est sûr de ne pas l'avoir trouvée
    logger.warning("⚠️ OPENAI_API_KEY non trouvée. L'application risque de ne pas fonctionner.")

# ============================
#   LLM CONFIG (Sélecteur de modèles)
# ============================
# Utilisation du modèle cutting-edge GPT-5.1 comme demandé par défaut
LLM_MODEL = get_secret("CHAT_MODEL", "gpt-5.1")
EMBEDDING_MODEL = get_secret("EMBEDDING_MODEL", "text-embedding-3-large")

# 🔥 CORRECTION CRUCIALE : ALIAS DE COMPATIBILITÉ
# Ton fichier src/retrieval.py cherche 'MODEL_EMBEDDINGS', on lui donne ce qu'il veut.
MODEL_EMBEDDINGS = EMBEDDING_MODEL 

# ==============================
#   CHROMA DB PATHS
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCUMENTS_DIR = os.path.join(DATA_DIR, "documents")
CHROMA_DB_DIR = os.path.join(BASE_DIR, "chroma_db")
CHROMA_COLLECTION_NAME = "data_governance_rag"

# ==============================
#   RAG PARAMETERS
# ==============================
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Paramètres de recherche
TOP_K_RESULTS = 6
SIMILARITY_THRESHOLD = 0.7

# ==============================
#   LOGGING
# ==============================
logger.add(
    "logs.log",
    rotation="500 KB",
    retention="2 days",
    level="INFO",
    encoding="utf-8"
)

logger.info(f"Config chargée. Modèle actif : {LLM_MODEL}")