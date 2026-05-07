import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from groq import Groq
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

app = Flask(__name__)

# Better secret key
app.secret_key = "your_super_secret_random_key"

# Load API key from .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Check API key
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing in .env file")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

MODEL = "llama-3.1-8b-instant"


# -------------------------------------------------------
# SYSTEM PROMPTS
# -------------------------------------------------------

def get_system_prompt(submode, name, subject, year):

    if submode == "teach":
        return f"""
You are GradPath AI, a deeply knowledgeable academic tutor.

Student:
Name: {name}
Subject: {subject}
Year: {year}

Teach clearly with examples and simple explanations.
"""

    elif submode == "quiz":
        return f"""
You are GradPath AI acting as a quiz assistant.

Student:
Name: {name}
Subject: {subject}
Year: {year}

Ask only ONE question at a time.
"""

    elif submode == "revision":
        return f"""
You are GradPath AI helping students revise quickly.

Student:
Name: {name}
Subject: {subject}
Year: {year}

Give short revision notes.
"""

    elif submode == "placement":
        return f"""
You are GradPath AI giving placement guidance.

Student:
Name: {name}
Subject: {subject}
Year: {year}

Give realistic placement advice.
"""

    elif submode == "career":
        return f"""
You are GradPath AI giving career guidance.

Student:
Name: {name}
Subject: {subject}
Year: {year}

Suggest practical career options.
"""

    return "You are a helpful assistant."


# -------------------------------------------------------
# ROUTES
# -------------------------------------------------------

@app.route("/")
def index():

    if "name" in session:
        return redirect(url_for("chat"))

    return render_template("index.html")


@app.route("/onboard", methods=["POST"])
def onboard():

    name = request.form.get("name", "").strip()
    subject = request.form.get("subject", "").strip()
    year = request.form.get("year", "").strip()

    if not name or not subject or not year:
        return redirect(url_for("index"))

    session["name"] = name
    session["subject"] = subject
    session["year"] = year

    return redirect(url_for("chat"))


@app.route("/chat")
def chat():

    if "name" not in session:
        return redirect(url_for("index"))

    user_data = {
        "name": session["name"],
        "subject": session["subject"],
        "year": session["year"]
    }

    return render_template("chat.html", user=user_data)


@app.route("/api/chat", methods=["POST"])
def api_chat():

    if "name" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()

    user_message = data.get("message", "")
    submode = data.get("submode", "")
    history = data.get("history", [])

    name = session["name"]
    subject = session["subject"]
    year = session["year"]

    system_prompt = get_system_prompt(submode, name, subject, year)

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    for msg in history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    messages.append({
        "role": "user",
        "content": user_message
    })

    try:

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            top_p=0.9,
            max_tokens=1024
        )

        bot_reply = response.choices[0].message.content

        return jsonify({
            "reply": bot_reply
        })

    except Exception as e:

        print("Groq Error:", e)

        return jsonify({
            "error": "Failed to generate response"
        }), 500


@app.route("/reset")
def reset():

    session.clear()

    return redirect(url_for("index"))


# -------------------------------------------------------
# MAIN
# -------------------------------------------------------

if __name__ == "__main__":

    print("GradPath AI is running...")
    print("Open http://127.0.0.1:5001")

    app.run(debug=True, port=5001)