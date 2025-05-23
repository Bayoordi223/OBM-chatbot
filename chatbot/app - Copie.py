import streamlit as st
from groq import Groq
from search_faiss import search_similar_chunks

# === CONFIGURATION DE LA PAGE ===
st.set_page_config(
    page_title="Chatbot IA - Orange Business",
    page_icon="🟧",
    layout="centered",
    menu_items={
        'About': "Chatbot d'assistance Orange Business - Version RAG avec FAISS"
    }
)

# === CLÉ API ET MODÈLE ===
def get_api_key():
    return "gsk_" + "RTcNEWFbUusrpNcuu5JfWGdyb3FYmA8otWRtT75cdZB4spqsXeKF"

MODEL_NAME = "llama3-8b-8192"
client = Groq(api_key=get_api_key())

# === STYLES CSS ===
st.markdown("""
    <style>
        .user-message {
            background: #f0f0f0;
            border-radius: 18px 18px 0 18px;
            padding: 12px 16px;
            margin: 8px 0;
            max-width: 85%;
            margin-left: auto;
        }
        .bot-message {
            background: #fff8f2;
            border: 1px solid #ffe0c2;
            border-radius: 18px 18px 18px 0;
            padding: 12px 16px;
            margin: 8px 0;
            max-width: 85%;
        }
        .stButton>button {
            background-color: #ff7900 !important;
            color: white !important;
            border: none !important;
        }
        @media (max-width: 600px) {
            .user-message, .bot-message {
                max-width: 95% !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

# === HEADER ===
col1, col2 = st.columns([0.2, 0.8])
with col1:
    st.image("assets/orange_business.jpg", width=600)
with col2:
    st.markdown("""
        <h1 style='color: #ff7900; margin-bottom: 0;'>Chatbot Orange Business</h1>
    """, unsafe_allow_html=True)

# === SYSTEM PROMPT ===
SYSTEM_PROMPT = """
Tu es un assistant expert multilingue pour Orange Business Services Maroc. 
- Langue : détecte automatiquement la langue de l'utilisateur et répond dans la même langue
- Ton : Professionnel, précis et bienveillant
- Spécialités : Solutions B2B, réseaux, cloud, cybersécurité
Pour les questions hors scope : redirige vers orange-business.com ou support officiel.
"""

# === LANG DETECTION ===
def detect_language(text):
    common_french = {'le', 'la', 'les', 'un', 'une', 'des', 'je', 'tu', 'il'}
    common_english = {'the', 'and', 'you', 'are', 'is', 'to', 'of'}
    f = sum(word.lower() in common_french for word in text.split())
    e = sum(word.lower() in common_english for word in text.split())
    return "english" if e > f else "french"

# === SESSION STATE ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Je suis votre assistant Orange Business. Comment puis-je vous aider aujourd'hui ?"}
    ]
    st.session_state.context_window = 6

# === AFFICHAGE MESSAGES ===
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"<div class='user-message'><strong>Vous</strong><br>{message['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-message'><strong>Assistant Orange</strong><br>{message['content']}</div>", unsafe_allow_html=True)

# === INPUT UTILISATEUR ===
user_input = st.chat_input("Tapez votre message ici...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    lang = detect_language(user_input)
    lang_instruction = f"L'utilisateur a posé une question en {lang}. Réponds dans la même langue."

    # === RECHERCHE RAG AVEC FAISS ===
    context_chunks = search_similar_chunks(user_input, top_k=3)
    retrieved_context = "\n\n".join(context_chunks)

    with st.spinner("🔍 Recherche avec contexte enrichi..."):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": lang_instruction},
                    {"role": "user", "content": f"Voici des informations de contexte :\n{retrieved_context}"},
                    *st.session_state.messages[-st.session_state.context_window:]
                ],
                temperature=0.5,
                max_tokens=700
            )
            bot_reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.rerun()
        except Exception as e:
            st.error("Erreur technique. Merci de réessayer plus tard.")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Désolé, une erreur est survenue. Pour une assistance immédiate, contactez Orange Business Maroc."
            })
            st.rerun()

# === FOOTER ===
st.markdown("""
    <hr style='margin: 20px 0;'>
    <div style='text-align: center; color: #888; font-size: 0.85rem;'>
        ℹ️ Assistant IA. Pour plus d'infos, visitez <a href='https://www.orange-business.com/fr' target='_blank'>orange-business.com</a>
    </div>
    <div style='text-align: center; color: #888; font-size: 0.85rem;'>
        @Copyright Orange Business, Tout droits Réservés</a>
    </div>
""", unsafe_allow_html=True)
