"""
ingest.py
Pipeline d’ingestion PRO : PDF -> Nettoyage -> Chunks -> VectorDB.
Gère le reset de la base et la tolérance aux pannes.
"""

import sys
import os
# Ajoute le dossier racine (parent) au chemin de recherche de Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import shutil
from typing import List
from tqdm import tqdm  # Pour la barre de progression

from loguru import logger
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from config import (
    DOCUMENTS_DIR,
    CHROMA_DB_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL,
    OPENAI_API_KEY,
    CHROMA_COLLECTION_NAME,
)

def reset_vector_db() -> None:
    """
    Supprime la base de données existante pour repartir de zéro.
    C'est crucial pour éviter les doublons lors des ré-ingestions.
    """
    if os.path.exists(CHROMA_DB_DIR):
        try:
            shutil.rmtree(CHROMA_DB_DIR)
            logger.warning(f"🧹 Ancienne base de données supprimée : {CHROMA_DB_DIR}")
        except Exception as e:
            logger.error(f"❌ Impossible de supprimer l'ancienne DB : {e}")

def load_pdfs() -> List:
    """Charge tous les PDFs avec gestion d'erreurs et barre de progression."""
    if not os.path.exists(DOCUMENTS_DIR):
        raise ValueError(f"❌ Dossier documents introuvable : {DOCUMENTS_DIR}")

    files = [f for f in os.listdir(DOCUMENTS_DIR) if f.lower().endswith(".pdf")]
    
    if not files:
        raise ValueError("❌ Aucun document PDF trouvé.")

    docs: List = []
    
    logger.info(f"📂 Découverte de {len(files)} fichiers PDF...")

    # Utilisation de TQDM pour une barre de progression pro
    for filename in tqdm(files, desc="Chargement des PDF"):
        file_path = os.path.join(DOCUMENTS_DIR, filename)
        
        try:
            loader = PyPDFLoader(file_path)
            file_docs = loader.load()
            
            # Nettoyage des métadonnées pour l'UI
            clean_name = os.path.splitext(filename)[0].replace("_", " ").title()
            
            for d in file_docs:
                d.metadata["source"] = clean_name  # Nom joli pour l'UI
                d.metadata["filename"] = filename  # Nom technique
                
            docs.extend(file_docs)
            
        except Exception as e:
            logger.error(f"⚠️ Erreur lors du chargement de {filename} : {e}")
            continue

    logger.success(f"📥 {len(docs)} pages chargées au total.")
    return docs


def chunk_documents(docs: List) -> List:
    """
    Découpe intelligente : on essaie de ne pas couper les phrases en deux.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True,
        # Séparateurs prioritaires : Paragraphe > Ligne > Phrase > Mots
        separators=["\n\n", "\n", ".", " ", ""] 
    )
    chunks = splitter.split_documents(docs)
    logger.success(f"🧩 Découpage terminé : {len(chunks)} fragments générés.")
    return chunks


def embed_and_store(chunks: List) -> None:
    """Génère les embeddings et stocke dans Chroma."""
    logger.info("⚙️ Initialisation du modèle d'Embeddings OpenAI...")

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=OPENAI_API_KEY,
    )

    logger.info(f"💾 Indexation dans ChromaDB ({CHROMA_DB_DIR})...")
    
    # Batch processing automatique par Chroma
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=CHROMA_COLLECTION_NAME,
        persist_directory=CHROMA_DB_DIR,
    )
    
    logger.success("🏁 Indexation terminée avec succès !")


def run_ingestion() -> None:
    """Pipeline complet d’ingestion (Reset -> Load -> Chunk -> Store)."""
    logger.info("🚀 Démarrage du pipeline d'ingestion Data Governance...")
    
    # 1. Nettoyage (Clean Slate)
    reset_vector_db()
    
    # 2. Chargement
    docs = load_pdfs()
    if not docs:
        logger.warning("Aucun document valide n'a été chargé. Arrêt.")
        return

    # 3. Découpage
    chunks = chunk_documents(docs)
    
    # 4. Stockage
    embed_and_store(chunks)

    logger.success("🎉 Base de connaissance mise à jour !")


if __name__ == "__main__":
    run_ingestion()
