import streamlit as st
from groq import Groq
from search_faiss import search_similar_chunks
import base64
from pathlib import Path

# === CONFIGURATION DE LA PAGE ===
st.set_page_config(
    page_title="Chatbot IA - Orange Business",
    page_icon="🟧",
    layout="centered",
    menu_items={
        'About': "Chatbot d'assistance Orange Business - Version RAG avec FAISS"
    }
)

# === FONCTION POUR ENCODER L'IMAGE ===
@st.cache_data
def get_img_as_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Chemin vers l'image et paramètres
img_path = Path("chatbot/ARRIERE.jpg")
bg_opacity = 0.1 # Ajustez entre 0.1 (transparent) et 1 (opaque)

try:
    img_bg = get_img_as_base64(img_path)
    background_style = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpg;base64,{img_bg}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }}
    
    /* Overlay pour l'opacité */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(255, 255, 255, {1 - bg_opacity});
        z-index: -1;
    }}
    
    /* Conteneur principal */
    .stApp {{
        background-color: transparent !important;
    }}
    """
except Exception as e:
    st.error(f"Erreur de chargement de l'image: {e}")
    background_style = """
    <style>
    .stApp {
        background: linear-gradient(135deg, #ff7e00, #ff5200);
    }
    </style>
    """

# === STYLE COMPLET ===
st.markdown(f"""
{background_style}
<style>
    /* BULLES DE DISCUSSION */
    .chat-container {{
        max-width: 1000px;
        margin: 0 auto;
        margin-bottom: 22px;
    }}
    .chat-row {{
        display: flex;
        margin: 22px 0;
    }}
    .bubble-user {{
        margin-left: auto;
        background: linear-gradient(120deg, rgba(255, 121, 0, 0.9), rgba(255, 179, 102, 0.9));
        color: white;
        padding: 22px 32px;
        border-radius: 22px 22px 6px 22px;
        max-width: 88%;
        min-width: 220px;
        font-size: 1.19rem;
        box-shadow: 0 3px 12px rgba(255,121,0,0.10);
        animation: slideUp .42s cubic-bezier(.42,0,.58,1) both;
        word-break: break-word;
        backdrop-filter: blur(2px);
    }}
    .bubble-bot {{
        margin-right: auto;
        background: linear-gradient(120deg, rgba(255, 248, 242, 0.9), rgba(255, 217, 179, 0.9));
        color: #222;
        padding: 22px 32px;
        border-radius: 22px 22px 22px 6px;
        max-width: 88%;
        min-width: 220px;
        font-size: 1.19rem;
        border: 1.5px solid rgba(255, 227, 194, 0.7);
        box-shadow: 0 3px 12px rgba(255,121,0,0.05);
        animation: slideUp .42s cubic-bezier(.42,0,.58,1) both;
        word-break: break-word;
        backdrop-filter: blur(2px);
    }}
    .label-bot, .label-user {{
        font-size: 1.06em;
    }}
    .label-bot {{
        font-weight: 600;
        color: #ff7900;
        margin-bottom: 2px;
        margin-left: 4px;
    }}
    .label-user {{
        font-weight: 600;
        color: #777;
        margin-bottom: 2px;
        text-align: right;
        margin-right: 8px;
    }}
    @keyframes slideUp {{
        from {{ opacity:0; transform:translateY(18px);}}
        to {{ opacity:1; transform:translateY(0);}}
    }}
    @media (max-width: 900px) {{
        .bubble-bot, .bubble-user {{ max-width: 99%; padding: 18px 8px; font-size: 1.04rem;}}
        .chat-container {{ padding: 1px;}}
    }}
    /* === FAQ FLOTANTE === */
    #faq-button {{
        position: fixed;
        bottom: 24px;
        right: 24px;
        background-color: #ff7900;
        color: white;
        border: none;
        border-radius: 50px;
        padding: 13px 28px;
        font-size: 17px;
        cursor: pointer;
        z-index: 9999;
        box-shadow: 0 4px 18px rgba(255,121,0,0.18);
        font-weight: bold;
        transition: all 0.3s;
    }}
    #faq-button:hover {{
        background-color: #e96b00;
        transform: translateY(-2px) scale(1.04);
    }}
    #faq-modal {{
        display: none;
        position: fixed;
        bottom: 90px;
        right: 24px;
        width: 320px;
        background: white;
        border: 1px solid #ffe0c2;
        border-radius: 15px;
        padding: 17px;
        z-index: 10000;
        box-shadow: 0 8px 26px rgba(255,121,0,0.10);
        animation: fadeFaq .26s cubic-bezier(.4,0,.2,1);
    }}
    @keyframes fadeFaq {{
        from {{ opacity: 0; transform:translateY(40px);}}
        to {{ opacity: 1; transform:translateY(0);}}
    }}
    .faq-header {{
        display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;
    }}
    .faq-title {{
        color: #ff7900; font-weight: bold; font-size: 1.1rem;
    }}
    #close-faq {{
        background: none; border: none; color: #888; font-size: 22px; cursor: pointer;
    }}
    .faq-question {{
        background: #fff8f2;
        border: 1px solid #ffe0c2;
        border-radius: 8px;
        padding: 11px 15px;
        margin-bottom: 9px;
        font-size: 15px;
        cursor: pointer;
        transition: all 0.18s;
        font-weight: 500;
        color: #ff7900;
    }}
    .faq-question:hover {{
        background-color: #ff7900;
        color: white;
        transform: translateX(-3px) scale(1.01);
    }}
    .faq-icon {{ margin-right: 7px; font-size: 16px; }}
    @media (max-width: 600px) {{
        #faq-modal {{ width: 98vw; right: 1vw; bottom: 80px;}}
        #faq-button {{ right: 1vw;}}
    }}
</style>
""", unsafe_allow_html=True)

# === CLÉ API ET MODÈLE ===
def get_api_key():
    return "gsk_" + "KEY_API_GROQ_A_COLLER_ICI"

MODEL_NAME = "llama3-8b-8192"
client = Groq(api_key=get_api_key())

# === HEADER ===
header_col1, header_col2 = st.columns([0.22, 0.78])
with header_col1:
    st.image("chatbot/assets/orange_business.jpg", width=90)
with header_col2:
    st.markdown("""
        <div style='display: flex; flex-direction: column; align-items: center;'>
            <h1 style='
                color: #ff7900;
                font-family: "Montserrat", Arial, sans-serif;
                font-size: 2.7rem;
                font-weight: 900;
                letter-spacing: 2px;
                text-shadow: 1px 2px 16px #2227, 0px 1px 0px #fff3;
                margin-bottom: 0;
                margin-top: 12px;
                line-height: 1.1;
                text-transform: uppercase;
                white-space: nowrap;
                text-align: center;
            '>
                CHATBOT ORANGE BUSINESS
            </h1>
            <p style='color: #fff; margin-top: 0.5rem; font-size: 1.10rem; text-shadow:1px 1px 6px #111; text-align: center;'>Assistant intelligent pour vos questions professionnelles</p>
        </div>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;900&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)


st.divider()

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

# === AFFICHAGE MESSAGES (BULLES) ===
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f"""
            <div class="chat-row">
                <div class="bubble-user">
                    <div class="label-user">Vous</div>
                    {message['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(
            f"""
            <div class="chat-row">
                <div class="bubble-bot">
                    <div class="label-bot">Assistant Orange</div>
                    {message['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# === INPUT UTILISATEUR ===
user_input = st.chat_input("Posez votre question ici...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    lang = detect_language(user_input)
    lang_instruction = f"L'utilisateur a posé une question en {lang}. Réponds dans la même langue."
    context_chunks = search_similar_chunks(user_input, top_k=3)
    retrieved_context = "\n\n".join(context_chunks)

    with st.spinner("OrangeBot rédige une réponse..."):
        try:
            client = Groq(api_key=get_api_key())
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
        except Exception:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Désolé, une erreur est survenue. Pour une assistance immédiate, contactez Orange Business Maroc."
            })
            st.rerun()

# === FOOTER ===
st.markdown("""
    <div style='margin-top: 40px;'>
        <hr style='margin: 20px 0; border: none; border-top: 1px solid #eee;'>
        <div style='text-align: center; color: #fff; font-size: 0.95em; line-height: 1.5; text-shadow: 1px 1px 8px #2228;'>
            <div style='margin-bottom: 8px;'>
                ℹ️ Assistant IA Orange Business Services
            </div>
            <div style='margin-bottom: 8px;'>
                 Pour plus d'informations, visitez <a href='https://www.orange-business.com/fr' target='_blank' style='color: #ff7900; text-decoration: none;'>orange-business.com</a>
            </div>
            <div>
                © 2025 Orange Business. Tous droits réservés.
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)


# === FAQ FONCTIONNELLE ===
st.markdown("""
<style>
    /* Styles CSS existants conservés */
    #faq-button {
        position: fixed;
        bottom: 24px;
        right: 24px;
        background-color: #ff7900;
        color: white;
        border: none;
        border-radius: 50px;
        padding: 13px 28px;
        font-size: 17px;
        cursor: pointer;
        z-index: 9999;
        box-shadow: 0 4px 18px rgba(255,121,0,0.18);
        font-weight: bold;
        transition: all 0.3s;
    }
    #faq-button:hover {
        background-color: #e96b00;
        transform: translateY(-2px) scale(1.04);
    }
    #faq-modal {
        display: none;
        position: fixed;
        bottom: 90px;
        right: 24px;
        width: 320px;
        background: white;
        border: 1px solid #ffe0c2;
        border-radius: 15px;
        padding: 17px;
        z-index: 10000;
        box-shadow: 0 8px 26px rgba(255,121,0,0.10);
        animation: fadeFaq .26s cubic-bezier(.4,0,.2,1);
    }
</style>

<div id="faq-modal">
    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
        <div style='color: #ff7900; font-weight: bold; font-size: 1.1rem;'>📋 FAQ Orange Business</div>
        <button id="close-faq" style='background: none; border: none; color: #888; font-size: 22px; cursor: pointer;'>×</button>
    </div>
    <div class="faq-question" onclick="setQuestion('Quelles solutions cloud propose Orange pour les entreprises ?')">
        <span>☁️</span> Solutions Cloud
    </div>
    <div class="faq-question" onclick="setQuestion('Comment sécuriser mon réseau avec Orange ?')">
        <span>🔐</span> Sécurité réseau
    </div>
    <div class="faq-question" onclick="setQuestion('Comment contacter le support technique Orange ?')">
        <span>🛠️</span> Support technique
    </div>
</div>

<button id="faq-button">📋 FAQ Orange</button>

<script>
// Fonction pour afficher/masquer le modal
document.getElementById('faq-button').onclick = function() {
    document.getElementById('faq-modal').style.display = 'block';
};
document.getElementById('close-faq').onclick = function() {
    document.getElementById('faq-modal').style.display = 'none';
};

// Fonction pour insérer la question dans le chat
function setQuestion(question) {
    const input = window.parent.document.querySelector('.stChatInput textarea');
    if (input) {
        input.value = question;
        const event = new Event('input', { bubbles: true });
        input.dispatchEvent(event);
        // Déclenchement manuel de la soumission
        const form = window.parent.document.querySelector('.stChatInput form');
        if (form) {
            form.dispatchEvent(new Event('submit', { cancelable: true }));
        }
    }
    document.getElementById('faq-modal').style.display = 'none';
}

// Fermer le modal si clic en dehors
window.addEventListener('click', function(event) {
    const modal = document.getElementById('faq-modal');
    const btn = document.getElementById('faq-button');
    if (event.target !== btn && !btn.contains(event.target)) {
        if (event.target !== modal && !modal.contains(event.target)) {
            modal.style.display = 'none';
        }
    }
});
</script>
""", unsafe_allow_html=True)