import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Secret key needed for Flask sessions to work
# In a real project, use a proper random secret key
app.secret_key = "gradpath-secret-key-2024"

# Initialize the Groq client with API key from .env
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# The model we're using - fast and capable for student tasks
MODEL = "llama-3.1-8b-instant"

# -------------------------------------------------------
# SYSTEM PROMPTS - one for each sub-mode
# These get injected with user data before sending to AI
# -------------------------------------------------------

def get_system_prompt(submode, name, subject, year):
    """Return the correct system prompt based on which sub-mode the user selected."""

    # This restriction is added to every prompt so the AI refuses off-topic questions
    # consistently across all modes — no separate backend filtering needed
    domain_restriction = """
STRICT RULE — YOU MUST FOLLOW THIS ALWAYS:
You are only allowed to respond to topics related to: education, studies, academics, exams, revision, placements, and career guidance.
If the user asks about ANYTHING outside these domains (jokes, sports, celebrities, movies, general knowledge, random facts, etc.), respond with EXACTLY this sentence and nothing else:
"Sorry, I couldn't process that request. If you'd like, I can still help you with your studies or career-related questions."
Do not add any explanation. Do not apologize further. Output only that one sentence for off-topic questions.
"""

    if submode == "teach":
        return f"""You are GradPath AI, a deeply knowledgeable academic tutor for college students.
The student's name is {name}, studying {subject} in {year}.
Your job is to teach concepts deeply and clearly. When the student tells you a topic:
1. Give a clear, simple definition.
2. Explain the concept step by step with examples.
3. Use analogies where helpful.
4. End with 2-3 key points to remember.
Keep responses focused. Use short paragraphs. No bullet spam.
If the student is confused, re-explain in a simpler way.
{domain_restriction}"""

    elif submode == "quiz":
        return f"""You are GradPath AI acting as an exam preparation assistant.
The student's name is {name}, studying {subject} in {year}.
Your task:
1. Ask the student what topic they want to be quizzed on.
2. Generate ONE question at a time (can be MCQ or short-answer).
3. Wait for the student's answer.
4. Evaluate: tell them if correct or incorrect.
5. If incorrect, briefly explain the right answer.
6. Ask if they want another question on the same topic or a new topic.
Never give all questions at once. Always one at a time. Keep it encouraging.
{domain_restriction}"""

    elif submode == "revision":
        # NEW FEATURE: Quick Revision / Notes mode
        return f"""You are GradPath AI helping students revise quickly.
The student is {name}, studying {subject} in {year}.
When a topic is given:
- Provide short, concise notes
- Focus on exam revision
- Use simple language
- Include key points only
- Avoid long explanations
{domain_restriction}"""

    elif submode == "placement":
        return f"""You are GradPath AI, a realistic and honest career mentor for Indian college students.
The student's name is {name}, studying {subject} in {year}.
For placement guidance:
- Ask about their CGPA range, current skills, and target companies/roles.
- Give honest, ground-reality advice. Do not over-promise.
- Suggest: skills to learn, projects to build, timeline to placement-readiness.
- If their profile has gaps, point them out kindly but clearly.
- Recommend specific role types that match their background.
Be warm but realistic. A student with 5.5 CGPA needs different advice than one with 8.5.
{domain_restriction}"""

    elif submode == "career":
        return f"""You are GradPath AI, a career options advisor for college students.
The student's name is {name}, studying {subject} in {year}.
Your job is to explore non-traditional career paths beyond campus placements.
Cover options like: UPSC/state exams, GATE, MBA, MS abroad, freelancing,
startups, research, certifications, YouTube/content, and more.
Ask what they enjoy and what they want to avoid.
Give realistic timelines and first steps for each path they are interested in.
Do not lecture. Keep it conversational and practical.
{domain_restriction}"""

    # Fallback - shouldn't happen but just in case
    return f"You are GradPath AI, a helpful assistant for {name} who is studying {subject} in {year}.\n{domain_restriction}"


# -------------------------------------------------------
# FLASK ROUTES
# -------------------------------------------------------

@app.route("/")
def index():
    """Show the onboarding page where user enters their details."""
    # If user already has a session, send them to chat
    if "name" in session:
        return redirect(url_for("chat"))
    return render_template("index.html")


@app.route("/onboard", methods=["POST"])
def onboard():
    """Handle the onboarding form submission. Save user data to session."""
    name = request.form.get("name", "").strip()
    subject = request.form.get("subject", "").strip()
    year = request.form.get("year", "").strip()

    # Basic server-side validation
    if not name or not subject or not year:
        return redirect(url_for("index"))

    # Save user info in Flask session (stays in memory, no database needed)
    session["name"] = name
    session["subject"] = subject
    session["year"] = year

    return redirect(url_for("chat"))


@app.route("/chat")
def chat():
    """Show the main chat page. Redirect to onboarding if not logged in."""
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
    """
    Main API endpoint that frontend calls when user sends a message.
    Receives message, mode, submode, and conversation history.
    Calls Groq API and returns the AI response.
    """
    if "name" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()

    # Extract what we need from the request
    user_message = data.get("message", "")
    submode = data.get("submode", "")
    history = data.get("history", [])  # Previous messages in the conversation

    # Get user info from session
    name = session["name"]
    subject = session["subject"]
    year = session["year"]

    # Pick the right system prompt for this mode
    system_prompt = get_system_prompt(submode, name, subject, year)

    # Build the messages list for Groq
    # System prompt goes first as a "system" role message (required in groq >= 1.0)
    messages = [{"role": "system", "content": system_prompt}]
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
        # temperature controls randomness (0.7 is balanced for natural but focused answers)
        # top_p controls diversity (0.9 allows varied vocabulary while staying relevant)
        # These values are ideal for an academic chatbot to avoid overly robotic responses.
        # Call Groq API
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=1024,
            temperature=0.7,
            top_p=0.9,
            messages=messages
        )

        # Extract the text response
        bot_reply = response.choices[0].message.content

        return jsonify({"reply": bot_reply})

    except Exception as e:
        # Return a friendly error instead of crashing
        print(f"Groq API error: {e}")
        return jsonify({"error": "Something went wrong. Please check your API key and try again."}), 500


@app.route("/reset")
def reset():
    """Clear the session and send user back to onboarding."""
    session.clear()
    return redirect(url_for("index"))


# -------------------------------------------------------
# ENTRY POINT
# -------------------------------------------------------

if __name__ == "__main__":
    # Check if API key is loaded before starting
    if not os.environ.get("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY not found in .env file!")
        print("Create a .env file with: GROQ_API_KEY=your_key_here")
    else:
        print("GradPath AI is starting...")
        print("Open: http://localhost:5001")
        app.run(debug=True, port=5001)
