// ============================================================
// GradPath AI — script.js
// Handles all chat logic: mode selection, sending messages,
// showing responses, dark mode, typing indicator, etc.
// ============================================================

// -- Global state --
let currentMode = null;      // "studies" or "career"
let currentSubmode = null;   // "teach", "quiz", "revision", "placement", "career"
let chatHistory = [];        // Full conversation history sent to backend
let isBotTyping = false;     // Prevent sending while AI is responding

// -- DOM references --
const chatWindow = document.getElementById("chatWindow");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

// ============================================================
// PAGE LOAD — Add welcome message and setup dark mode
// ============================================================

window.addEventListener("DOMContentLoaded", () => {
  // Apply saved theme (light/dark) from localStorage
  applyTheme();

  // Show the initial welcome message
  const welcomeMsg = `👋 Hey ${USER.name}! Welcome to GradPath AI.\n\nI'm here to help you with your ${USER.subject} studies and career planning.\n\nSelect a mode above to get started!`;
  addBotMessage(welcomeMsg);
});

// ============================================================
// THEME (DARK / LIGHT MODE)
// ============================================================

function applyTheme() {
  // Dark is default. 'light' class switches to light mode.
  const saved = localStorage.getItem("gradpath-theme");
  if (saved === "light") {
    document.body.classList.add("light");
    document.getElementById("themeIcon").textContent = "🌙";
  } else {
    document.getElementById("themeIcon").textContent = "☀️";
  }
}

function toggleTheme() {
  const isLight = document.body.classList.toggle("light");
  localStorage.setItem("gradpath-theme", isLight ? "light" : "dark");
  document.getElementById("themeIcon").textContent = isLight ? "🌙" : "☀️";
}

// Hook up the toggle button
document.getElementById("themeToggle").addEventListener("click", toggleTheme);

// ============================================================
// MODE SELECTION
// ============================================================

function selectMode(mode) {
  currentMode = mode;
  currentSubmode = null;  // Reset submode when mode changes

  // Clear chat history when switching modes
  chatHistory = [];

  // Update mode button styles
  document.getElementById("studiesBtn").classList.toggle("active", mode === "studies");
  document.getElementById("careerBtn").classList.toggle("active", mode === "career");

  // Keep input disabled until user picks a sub-option
  setInputEnabled(false);

  // Show appropriate sub-option buttons
  if (mode === "studies") {
    showStudiesOptions();
  } else if (mode === "career") {
    showCareerOptions();
  }
}

function showStudiesOptions() {
  // Add a bot message with the sub-mode buttons for Studies Mode
  const container = document.createElement("div");
  container.className = "message bot";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = "📚 What do you want to do in Studies Mode?";

  const btnGroup = document.createElement("div");
  btnGroup.className = "submode-buttons";

  // Three sub-options for Studies Mode
  const options = [
    { label: "🧠 Teach Me a Concept", submode: "teach" },
    { label: "📝 Exam Prep / Quiz Me", submode: "quiz" },
    { label: "⚡ Quick Revision / Notes", submode: "revision" },
  ];

  options.forEach(opt => {
    const btn = document.createElement("button");
    btn.className = "submode-btn";
    btn.textContent = opt.label;
    btn.onclick = () => selectSubmode(opt.submode, opt.label, btnGroup);
    btnGroup.appendChild(btn);
  });

  container.appendChild(bubble);
  container.appendChild(btnGroup);
  chatWindow.appendChild(container);
  scrollToBottom();
}

function showCareerOptions() {
  const container = document.createElement("div");
  container.className = "message bot";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = "💼 What kind of career help do you need?";

  const btnGroup = document.createElement("div");
  btnGroup.className = "submode-buttons";

  // Two sub-options for Career Mode
  const options = [
    { label: "🏢 Placement Guidance", submode: "placement" },
    { label: "🌍 Other Career Options", submode: "career" },
  ];

  options.forEach(opt => {
    const btn = document.createElement("button");
    btn.className = "submode-btn";
    btn.textContent = opt.label;
    btn.onclick = () => selectSubmode(opt.submode, opt.label, btnGroup);
    btnGroup.appendChild(btn);
  });

  container.appendChild(bubble);
  container.appendChild(btnGroup);
  chatWindow.appendChild(container);
  scrollToBottom();
}

// ============================================================
// SUBMODE SELECTION
// Called when user clicks one of the sub-option buttons
// ============================================================

async function selectSubmode(submode, label, btnGroup) {
  currentSubmode = submode;

  // Disable all submode buttons so user can't click again
  btnGroup.querySelectorAll(".submode-btn").forEach(btn => {
    btn.disabled = true;
    btn.style.opacity = btn.textContent === label ? "1" : "0.4";
  });

  // Show user's choice as a chat bubble
  addUserMessage(label);

  // Enable the input now that a submode is selected
  setInputEnabled(true);
  userInput.placeholder = "Type your message...";
  userInput.focus();

  // Get the first bot message for this submode
  const firstMessage = getFirstMessage(submode);
  await showBotTyping(firstMessage);
}

// First message shown after selecting each sub-mode
function getFirstMessage(submode) {
  const msgs = {
    teach: `Great! What concept or topic would you like me to explain in detail?\n\n(e.g. DBMS normalization, Newton's laws, derivatives, supply and demand)`,
    quiz: `Let's do some exam prep! Which subject or topic should I quiz you on?\n\nI'll ask you one question at a time.`,
    revision: `Sure! What topic do you want to revise quickly?\n\nI'll give you short, exam-focused notes with key points and definitions.`,
    placement: `Let's talk placements! To give you the most useful advice, can you tell me:\n\n→ Your CGPA range\n→ Skills or languages you know\n→ Target companies or roles you're aiming for?`,
    career: `Interesting! You want to explore paths beyond traditional placements.\n\nTell me — what are your interests? What do you enjoy doing, and what kind of work do you want to avoid?\n\n(e.g. I like coding but hate 9-5 jobs, or I'm interested in government exams, etc.)`,
  };
  return msgs[submode] || "How can I help you today?";
}

// ============================================================
// SENDING MESSAGES
// ============================================================

async function sendMessage() {
  const text = userInput.value.trim();

  // Don't send empty messages or while bot is typing
  if (!text || isBotTyping) return;

  // Make sure user has selected a mode and submode
  if (!currentSubmode) {
    addSystemMessage("Please select a mode and sub-option first!");
    return;
  }

  // Show user message in chat
  addUserMessage(text);

  // Add to history so AI has context
  chatHistory.push({ role: "user", content: text });

  // Clear and disable input while waiting
  userInput.value = "";
  setInputEnabled(false);
  isBotTyping = true;

  // Show typing animation
  const typingEl = showTypingIndicator();

  try {
    // Call our Flask backend which calls the Groq API
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        submode: currentSubmode,
        history: chatHistory.slice(-10), // Send last 10 messages for context (saves tokens)
      }),
    });

    const data = await response.json();

    // Remove typing indicator
    typingEl.remove();

    if (data.error) {
      addBotMessage("❌ " + data.error);
    } else {
      // Show AI response
      addBotMessage(data.reply);
      // Add to history for future context
      chatHistory.push({ role: "assistant", content: data.reply });
    }

  } catch (err) {
    // Network error or server down
    typingEl.remove();
    addBotMessage("❌ Couldn't connect to the server. Make sure app.py is running.");
    console.error("Fetch error:", err);
  }

  isBotTyping = false;
  setInputEnabled(true);
  userInput.focus();
}

// ============================================================
// UI HELPER FUNCTIONS
// ============================================================

// Add a user message bubble (right side)
function addUserMessage(text) {
  const container = document.createElement("div");
  container.className = "message user";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  const meta = document.createElement("div");
  meta.className = "msg-meta";
  meta.textContent = "You · " + getTime();

  container.appendChild(bubble);
  container.appendChild(meta);
  chatWindow.appendChild(container);
  scrollToBottom();
}

// Add a bot message bubble (left side) with avatar
function addBotMessage(text) {
  const container = document.createElement("div");
  container.className = "message bot";

  const row = document.createElement("div");
  row.className = "bot-row";

  const avatar = document.createElement("div");
  avatar.className = "bot-avatar";
  avatar.textContent = "🎓";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  row.appendChild(avatar);
  row.appendChild(bubble);

  const meta = document.createElement("div");
  meta.className = "msg-meta";
  meta.textContent = "GradPath AI · " + getTime();

  container.appendChild(row);
  container.appendChild(meta);
  chatWindow.appendChild(container);
  scrollToBottom();
}

// Add a centered system-level message (e.g. "Select a mode first")
function addSystemMessage(text) {
  const el = document.createElement("div");
  el.className = "system-message";
  el.textContent = text;
  chatWindow.appendChild(el);
  scrollToBottom();
}

// Show the three bouncing dots while waiting for AI
function showTypingIndicator() {
  const wrapper = document.createElement("div");
  wrapper.className = "message bot";

  const row = document.createElement("div");
  row.className = "bot-row";

  const avatar = document.createElement("div");
  avatar.className = "bot-avatar";
  avatar.textContent = "🎓";

  const indicator = document.createElement("div");
  indicator.className = "typing-indicator";
  indicator.innerHTML = `<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>`;

  row.appendChild(avatar);
  row.appendChild(indicator);
  wrapper.appendChild(row);
  chatWindow.appendChild(wrapper);
  scrollToBottom();
  return wrapper; // Return wrapper so we can remove it later
}

// Used for sub-mode first messages (simulates typing delay)
async function showBotTyping(message) {
  const typingEl = showTypingIndicator();

  // Small delay to feel natural
  await sleep(900);

  typingEl.remove();
  addBotMessage(message);

  // Add this first message to history so AI has context
  chatHistory.push({ role: "assistant", content: message });
}

// Enable or disable the input + send button
function setInputEnabled(enabled) {
  userInput.disabled = !enabled;
  sendBtn.disabled = !enabled;
}

// Scroll chat window to the latest message
function scrollToBottom() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Get current time as HH:MM for message timestamps
function getTime() {
  const now = new Date();
  return now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

// Simple sleep helper for async delays
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ============================================================
// KEYBOARD SUPPORT — Enter to send, Shift+Enter for new line
// ============================================================

userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});
