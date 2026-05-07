# GradPath AI 🎓

Your AI Study & Career Companion — built for college students.

GradPath AI is a locally-hosted chatbot that helps you:
- **Learn concepts** with a patient AI tutor
- **Prepare for exams** with one-question-at-a-time quizzes
- **Revise quickly** with short, exam-focused notes
- **Get placement advice** tailored to your profile
- **Explore career paths** beyond traditional placements

---

## Setup Instructions

### Step 1 — Clone / Download the project

Put the `gradpath-ai` folder somewhere on your computer.

### Step 2 — Create your `.env` file

In the project folder, create a file named `.env` (copy from `.env.example`):

```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free API key from: https://console.groq.com

### Step 3 — Install Python dependencies

Make sure you have Python 3.9+ installed. Then run:

```bash
pip install -r requirements.txt
```

### Step 4 — Run the app

```bash
python app.py
```

### Step 5 — Open in browser

Visit: http://localhost:5000

---

## How to Use

1. Fill in your name, subject, and year on the first screen
2. You'll land on the chat page with a welcome message
3. Click **Studies Mode** or **Career Mode**
4. Pick a sub-option and start chatting!

### Studies Mode Options:
- **Teach Me a Concept** — explain any topic in depth
- **Exam Prep / Quiz Me** — one question at a time, evaluated live
- **Quick Revision / Notes** — short bullet-style revision notes

### Career Mode Options:
- **Placement Guidance** — realistic placement advice based on your profile
- **Other Career Options** — UPSC, GATE, MBA, freelancing, and more

---

## Tech Stack

- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Backend:** Python Flask
- **AI:** Groq API (llama-3.1-8b-instant)
- **Session:** Flask in-memory session (no database)

---

## File Structure

```
gradpath-ai/
├── app.py                # Flask backend
├── requirements.txt      # Python packages
├── .env.example          # Template for API key
├── README.md             # This file
├── templates/
│   ├── index.html        # Onboarding page
│   └── chat.html         # Chat interface
└── static/
    ├── style.css         # All styles (light + dark mode)
    └── script.js         # Frontend chat logic
```

---

## Model Configuration

- **temperature = 0.7**: Produces balanced responses. It allows for natural-sounding language without becoming too random or losing focus.
- **top_p = 0.9**: Provides controlled variation, ensuring the AI draws from a diverse vocabulary while remaining strictly relevant to the topic.
- **Why it matters**: This configuration is highly suitable for a study and career chatbot, as it strikes the right balance between being an engaging mentor and a precise, reliable academic assistant.

---

## Domain Knowledge

- This chatbot is uniquely designed for students within the education and career domain.
- Prompts are specifically structured for:
  - Concept learning (step-by-step explanations)
  - Exam preparation (interactive quizzing)
  - Revision (concise, exam-focused notes)
  - Placement guidance (realistic, profile-based advice)
- All AI responses are tightly controlled using tailored system prompts to ensure they meet the specific needs of these academic use cases.

---

## Notes

- No data is stored anywhere — everything resets when you close the server
- Press Ctrl+C in terminal to stop the server
- Dark mode toggle is in the top-right corner of the chat page
- You can switch modes anytime during a conversation
