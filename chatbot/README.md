
# Orange Business Morocco – Intelligent Chatbot (RAG + LLM)

This project is an intelligent assistant chatbot for Orange Business Morocco, developed in the context of a collaborative initiative between INPT and Orange Business Morocco. The assistant uses Retrieval-Augmented Generation (RAG) and a Large Language Model (LLM) for contextual and precise answers to professional and technical questions.

## Features

- Modern Streamlit user interface with Orange Business branding
- RAG system: semantic search with FAISS to enrich answers with company context
- Integration with Groq API and Llama 3 model
- Multilingual support (French/English) and automatic language detection
- Interactive FAQ for quick access to common questions

## Technologies

- **Python 3**
- **Streamlit**
- **Groq API** (LLM)
- **FAISS** (semantic search)
- **Flask** (for landing page / entrypoint)
- **OpenAI embeddings** (for RAG)
- **HTML / CSS / JS** (custom UI and FAQ)

## Contributors

- **Bayo Oumar**
- **Kamba Divava Junior**
- **Et-Takny El Mehdi**
- **Assoulaimani Aicha**
- **El Bouazzaouy Aicha**
- **Oissti Lamyae**

## Before running the project, you must create your own Groq API key:

- Go to Groq Console and sign up or log in.

- Create a new API key in your Groq dashboard.

- Open the app.py file.

- Replace the text KEY_API_GROQ_A_COLLER_ICI in the get_api_key() function with your Groq API key (the part after gsk_).

## Context

This project was carried out as part of the INPT curriculum, in partnership with Orange Business Morocco, to develop real-world AI solutions and foster collaborative innovation.
