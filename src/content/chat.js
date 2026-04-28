/* ── AskResumeChat — shared chat widget ────────────────────────────────────── *
 * Single source of truth for all chat surfaces:                                *
 *   resume.html  (inline bar + FAB modal)  →  references content/chat.js      *
 *   index.html   (full-page SWA)           →  references chat.js (CI copy)    *
 *                                                                              *
 * API                                                                          *
 *   AskResumeChat.warmUp()   — fire once on page load (container warm-up)     *
 *   AskResumeChat.init(cfg)  — create a chat instance                         *
 *                                                                              *
 * cfg options:                                                                 *
 *   messages        string    element ID of message container                  *
 *   input           string    element ID of textarea                           *
 *   send            string    element ID of send button                        *
 *   typing          string    unique element ID for typing indicator           *
 *   suggestions?    string    element ID of suggestion chips container         *
 *   rateCounter?    string    element ID of rate counter display               *
 *   showAvatars?    boolean   render 👤/🤖 avatars (default: false)            *
 *   withSuggestions?boolean   build suggestion chips (default: false)          *
 *   greet?          boolean   show greeting on init (default: true)            *
 *   greetMessage?   string    override default greeting text                   *
 *   suggestionList? string[]  override default suggestion questions            *
 * ─────────────────────────────────────────────────────────────────────────── */
(function (global) {
  "use strict";

  const API_URL     = "https://resumeai-app.lemontree-3428e352.eastus2.azurecontainerapps.io/api/ask";
  const HEALTH_URL  = "https://resumeai-app.lemontree-3428e352.eastus2.azurecontainerapps.io/api/health";
  const DAILY_LIMIT = 25;
  const STORAGE_KEY = "resumeai_usage";

  const DEFAULT_SUGGESTIONS = [
    "What is your most recent role?",
    "What Cloud services have you used?",
    "Tell me about your Epic experience.",
    "What AI tools do you use?",
    "What certifications do you hold?",
  ];

  const DEFAULT_GREET = "Hi! I'm an AI assistant trained on this resume. Ask me anything about Todd's background, skills, or projects.";

  // ── Rate limit (localStorage, shared across all instances on the page) ──────
  function todayKey() { return new Date().toISOString().slice(0, 10); }

  function getUsage() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return { date: todayKey(), count: 0 };
      const d = JSON.parse(raw);
      return d.date === todayKey() ? d : { date: todayKey(), count: 0 };
    } catch { return { date: todayKey(), count: 0 }; }
  }

  function incrementUsage() {
    const u = getUsage(); u.count++;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(u));
    return u.count;
  }

  function syncUsage(serverRemaining) {
    const used = DAILY_LIMIT - serverRemaining;
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ date: todayKey(), count: used }));
    return used;
  }

  function updateCounter(el, used) {
    if (!el) return;
    const remaining = DAILY_LIMIT - used;
    if (remaining <= 0) {
      el.textContent = `Daily limit reached (${DAILY_LIMIT}/${DAILY_LIMIT}). Come back tomorrow!`;
      el.className = "limit";
    } else if (remaining <= 3) {
      el.textContent = `${used} of ${DAILY_LIMIT} questions used today (${remaining} remaining)`;
      el.className = "warn";
    } else {
      el.textContent = `${used} of ${DAILY_LIMIT} questions used today`;
      el.className = "";
    }
  }

  // ── Warm-up ping ───────────────────────────────────────────────────────────
  function warmUp() {
    fetch(HEALTH_URL, { method: "GET" }).catch(() => {});
  }

  // ── Chat factory ───────────────────────────────────────────────────────────
  function init(cfg) {
    const msgs      = document.getElementById(cfg.messages);
    const sugsEl    = cfg.suggestions ? document.getElementById(cfg.suggestions) : null;
    const counterEl = cfg.rateCounter ? document.getElementById(cfg.rateCounter) : null;
    const inputEl   = document.getElementById(cfg.input);
    const sendBtn   = document.getElementById(cfg.send);
    if (!msgs || !inputEl || !sendBtn) return;

    const showAvatars    = !!cfg.showAvatars;
    const suggestionList = cfg.suggestionList || DEFAULT_SUGGESTIONS;
    const greetMessage   = cfg.greetMessage   || DEFAULT_GREET;

    function addMsg(text, role) {
      const wrap = document.createElement("div");
      wrap.className = `ai-msg ${role}`;
      if (showAvatars) {
        const av = document.createElement("div");
        av.className = "ai-avatar";
        av.textContent = role === "user" ? "👤" : "🤖";
        wrap.appendChild(av);
      }
      const bubble = document.createElement("div");
      bubble.className = "ai-bubble";
      bubble.textContent = text;
      wrap.appendChild(bubble);
      msgs.appendChild(wrap);
      msgs.scrollTop = msgs.scrollHeight;
    }

    function addTyping() {
      const wrap = document.createElement("div");
      wrap.className = "ai-msg bot";
      wrap.id = cfg.typing;
      if (showAvatars) {
        const av = document.createElement("div");
        av.className = "ai-avatar";
        av.textContent = "🤖";
        wrap.appendChild(av);
      }
      const bubble = document.createElement("div");
      bubble.className = "ai-bubble";
      bubble.innerHTML = '<div class="ai-dot-anim"><span></span><span></span><span></span></div>';
      wrap.appendChild(bubble);
      msgs.appendChild(wrap);
      msgs.scrollTop = msgs.scrollHeight;
    }

    function removeTyping() {
      const el = document.getElementById(cfg.typing);
      if (el) el.remove();
    }

    function setLoading(on) {
      sendBtn.disabled = on;
      inputEl.disabled = on;
    }

    function lockInput() {
      inputEl.disabled    = true;
      sendBtn.disabled    = true;
      inputEl.placeholder = "Daily limit reached. Come back tomorrow!";
    }

    function buildSuggestions() {
      if (!sugsEl) return;
      suggestionList.forEach(q => {
        const btn = document.createElement("button");
        btn.className = "ai-sug-btn";
        btn.textContent = q;
        btn.onclick = () => { sugsEl.style.display = "none"; sendQ(q); };
        sugsEl.appendChild(btn);
      });
    }

    async function sendQ(q) {
      if (!q.trim()) return;

      const usage = getUsage();
      if (usage.count >= DAILY_LIMIT) {
        updateCounter(counterEl, usage.count);
        lockInput();
        addMsg("You've reached the daily limit of 25 questions. Come back tomorrow!", "err");
        return;
      }

      addMsg(q, "user");
      inputEl.value = "";
      inputEl.style.height = "auto";
      if (sugsEl) sugsEl.style.display = "none";
      setLoading(true);
      addTyping();

      const controller = new AbortController();
      const timeoutId  = setTimeout(() => controller.abort(), 45000);

      let res;
      try {
        res = await fetch(API_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: q }),
          signal: controller.signal,
        });
      } catch (err) {
        clearTimeout(timeoutId);
        removeTyping();
        addMsg(
          err.name === "AbortError"
            ? "The AI took too long to respond. The service may be warming up — please try again."
            : "Unable to reach the AI service. Please try again later.",
          "err"
        );
        setLoading(false);
        return;
      }
      clearTimeout(timeoutId);
      removeTyping();

      if (res.status === 429) {
        updateCounter(counterEl, DAILY_LIMIT);
        lockInput();
        addMsg("You've reached the daily limit of 25 questions. Come back tomorrow!", "err");
        setLoading(false);
        return;
      }

      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        addMsg(errBody.error || "Something went wrong. Please try again.", "err");
        setLoading(false);
        return;
      }

      const data = await res.json();
      addMsg(data.answer, "bot");

      const used = typeof data.remaining === "number"
        ? syncUsage(data.remaining)
        : incrementUsage();
      updateCounter(counterEl, used);
      if (used >= DAILY_LIMIT) lockInput();
      setLoading(false);
    }

    // ── Setup ────────────────────────────────────────────────────────────────
    if (cfg.greet !== false) addMsg(greetMessage, "bot");
    if (cfg.withSuggestions) buildSuggestions();

    const initialUsed = getUsage().count;
    updateCounter(counterEl, initialUsed);
    if (initialUsed >= DAILY_LIMIT) lockInput();

    sendBtn.addEventListener("click", () => sendQ(inputEl.value));
    inputEl.addEventListener("keydown", e => {
      if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendQ(inputEl.value); }
    });
    inputEl.addEventListener("input", () => {
      inputEl.style.height = "auto";
      inputEl.style.height = Math.min(inputEl.scrollHeight, 80) + "px";
    });
  }

  global.AskResumeChat = { warmUp, init, getUsage, DAILY_LIMIT };

}(window));
