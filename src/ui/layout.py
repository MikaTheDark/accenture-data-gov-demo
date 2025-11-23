import streamlit as st
import textwrap
from typing import Literal, Optional

def inject_global_css() -> None:
    """
    Injecte le CSS global.
    Utilisation de textwrap.dedent pour nettoyer les espaces parasites.
    """
    css = textwrap.dedent("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');

        .stApp {
            background: radial-gradient(circle at top left, #1b1b3a 0%, #050816 40%, #000000 100%);
            background-attachment: fixed;
            color: #f5f5f5;
            font-family: 'Poppins', sans-serif;
        }

        [data-testid="stSidebar"] {
            background-color: #0b0c15;
            border-right: 1px solid rgba(255,255,255,0.05);
        }

        .custom-header {
            padding: 2rem 1.5rem;
            border-radius: 12px;
            background: linear-gradient(135deg, rgba(76, 29, 149, 0.4), rgba(30, 58, 138, 0.4));
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            border: 1px solid rgba(255, 255, 255, 0.08);
            text-align: center;
            margin-bottom: 2.5rem;
            backdrop-filter: blur(10px);
        }
        .custom-header h1 {
            margin: 0;
            font-weight: 600;
            font-size: 2rem;
            background: linear-gradient(90deg, #fff, #a5b4fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .custom-header p {
            margin-top: 0.5rem;
            color: #cbd5e1;
            font-size: 0.95rem;
            font-weight: 300;
        }

        .chat-row {
            display: flex;
            margin-bottom: 1.2rem;
            width: 100%;
        }
        .row-user { justify-content: flex-end; }
        .row-assistant { justify-content: flex-start; }

        .chat-bubble {
            padding: 1rem 1.4rem;
            border-radius: 12px;
            max-width: 80%;
            position: relative;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            font-size: 0.95rem;
            line-height: 1.6;
        }
        
        .bubble-user {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            border-bottom-right-radius: 2px;
        }
        
        .bubble-assistant {
            background: #1e1e2e;
            color: #e2e8f0;
            border: 1px solid rgba(255,255,255,0.08);
            border-bottom-left-radius: 2px;
        }

        .agent-badge {
            font-size: 0.65rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            opacity: 0.7;
            margin-bottom: 0.4rem;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .agent-badge::before {
            content: "•";
            color: #a78bfa;
            font-size: 1.2em;
        }

        .sources-block {
            margin-top: 0.8rem;
            padding: 0.8rem;
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
            font-size: 0.8rem;
            border-left: 3px solid #7c3aed;
        }
        .sources-title {
            font-weight: 600;
            color: #a78bfa;
            margin-bottom: 0.3rem;
            display: block;
        }
        
        a { color: #60a5fa !important; text-decoration: none; }
        a:hover { text-decoration: underline; }
        </style>
    """)
    st.markdown(css, unsafe_allow_html=True)

def render_header(title: str, subtitle: str = "") -> None:
    html = textwrap.dedent(f"""
        <div class="custom-header">
            <h1>{title}</h1>
            {f'<p>{subtitle}</p>' if subtitle else ''}
        </div>
    """)
    st.markdown(html, unsafe_allow_html=True)

def render_message(
    role: Literal["user", "assistant"],
    content: str,
    agent_name: Optional[str] = None,
    sources: Optional[str] = None,
) -> None:
    css_role = "row-user" if role == "user" else "row-assistant"
    css_bubble = "bubble-user" if role == "user" else "bubble-assistant"
    display_label = agent_name if agent_name else ("Vous" if role == "user" else "Assistant IA")

    # 1. Préparation du bloc Sources sans AUCUNE indentation
    sources_html = ""
    if sources:
        clean_sources = sources.replace('\n', '<br>')
        # Utilisation de dedent + strip pour garantir 0 espace au début
        sources_html = textwrap.dedent(f"""
            <div class="sources-block">
                <span class="sources-title">📚 Contexte & Sources</span>
                <div style="opacity: 0.9;">{clean_sources}</div>
            </div>
        """).strip()

    # 2. Construction du template principal
    # Important : On colle les balises à gauche pour éviter que Markdown ne panique
    html = f"""
<div class="chat-row {css_role}">
    <div class="chat-bubble {css_bubble}">
        <span class="agent-badge">{display_label}</span>
        <div style="margin-bottom: 0.5rem;">
        {content}</div>
        {sources_html}
    </div>
</div>
"""
    
    # 3. Affichage final
    st.markdown(html, unsafe_allow_html=True)