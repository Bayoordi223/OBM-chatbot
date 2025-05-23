from flask import Flask, send_from_directory, redirect
import subprocess
import os
import sys
import traceback

app = Flask(__name__, static_folder='landing_page')

# Track if we've already started Streamlit
streamlit_started = False

@app.route('/')
def home():
    return send_from_directory('landing_page', 'index.html')

@app.route('/style.css')
def style():
    return send_from_directory('landing_page', 'style.css')

@app.route('/launch')
def launch_chatbot():
    global streamlit_started
    try:
        if not streamlit_started:
            # Launch Streamlit without browser
            env = os.environ.copy()
            env["BROWSER"] = "none"

            # Works across platforms
            subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "chatbot/app.py", "--server.headless", "true", "--browser.serverAddress", "localhost", "--browser.serverPort", "8501"],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT
            )
            streamlit_started = True

        return redirect("http://localhost:8501", code=302)

    except Exception:
        return f"<h1>Erreur</h1><pre>{traceback.format_exc()}</pre>", 500

if __name__ == "__main__":
    app.run(port=5000)
