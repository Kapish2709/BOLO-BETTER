import streamlit as st
import httpx
import base64
import json
from datetime import datetime

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="BoloBetter — Hindi to English Coach",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── STYLING ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap');

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; max-width: 1100px; }

:root {
  --accent: #f4a94e;
  --casual: #6ec6a0;
  --professional: #6aabf0;
  --formal: #b89af0;
  --prospeak: #f4a94e;
}

.stApp { background: #0d0d0f; color: #f0ede8; }
[data-testid="stSidebar"] { background: #141417 !important; border-right: 1px solid rgba(255,255,255,0.07); }

.hero-title {
  font-family: 'Playfair Display', serif;
  font-size: 2.6rem;
  font-weight: 700;
  color: #f0ede8;
  line-height: 1.15;
  margin-bottom: 0.4rem;
}
.hero-title span { color: #f4a94e; }
.hero-sub {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.95rem;
  color: #7a7a8a;
  font-weight: 300;
  margin-bottom: 2rem;
  line-height: 1.7;
}

/* 4-column suggestion grid */
.suggestion-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 0.75rem;
  margin: 1.2rem 0;
}
.suggestion-card {
  background: #1c1c22;
  border-radius: 12px;
  padding: 1.1rem;
  border: 1px solid rgba(255,255,255,0.07);
  transition: all 0.2s;
}
.suggestion-card:hover { border-color: rgba(244,169,78,0.3); transform: translateY(-1px); }

/* Pro Speak card special styling */
.prospeak-card {
  background: linear-gradient(135deg, #1c1c22 0%, #1e1a14 100%);
  border: 1px solid rgba(244,169,78,0.25) !important;
}

.card-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.58rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  font-weight: 500;
  margin-bottom: 0.6rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
.card-text {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.88rem;
  line-height: 1.6;
  color: #f0ede8;
}
.prospeak-text {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.88rem;
  line-height: 1.6;
  color: #f4a94e;
  font-style: italic;
}

.tip-box {
  background: rgba(244,169,78,0.06);
  border: 1px solid rgba(244,169,78,0.2);
  border-radius: 10px;
  padding: 1rem 1.2rem;
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: #f4a94e;
  font-family: 'DM Sans', sans-serif;
  line-height: 1.6;
}

.translated-box {
  background: #1c1c22;
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 10px;
  padding: 1rem 1.4rem;
  margin: 1rem 0;
  font-style: italic;
  font-size: 1rem;
  color: #f0ede8;
  font-family: 'DM Sans', sans-serif;
  line-height: 1.6;
}

.section-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #4a4a5a;
  margin-bottom: 0.4rem;
}

/* Vocabulary cards */
.vocab-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.75rem;
  margin: 1rem 0;
}
.vocab-card {
  background: #141417;
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px;
  padding: 1rem;
}
.vocab-word {
  font-family: 'Playfair Display', serif;
  font-size: 1rem;
  color: #f4a94e;
  margin-bottom: 0.3rem;
  font-weight: 700;
}
.vocab-meaning {
  font-size: 0.75rem;
  color: #7a7a8a;
  margin-bottom: 0.5rem;
  font-family: 'DM Sans', sans-serif;
}
.vocab-syn {
  font-size: 0.72rem;
  color: #6ec6a0;
  margin-bottom: 0.2rem;
  font-family: 'JetBrains Mono', monospace;
}
.vocab-ant {
  font-size: 0.72rem;
  color: #f06a6a;
  font-family: 'JetBrains Mono', monospace;
}

/* Motivational quote */
.quote-box {
  background: #0d0d0f;
  border-left: 3px solid #f4a94e;
  padding: 1rem 1.4rem;
  margin-top: 1.5rem;
  border-radius: 0 10px 10px 0;
}
.quote-text {
  font-family: 'Playfair Display', serif;
  font-size: 0.95rem;
  font-style: italic;
  color: #f0ede8;
  line-height: 1.7;
  margin-bottom: 0.3rem;
}
.quote-author {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  color: #4a4a5a;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

/* History items */
.history-item {
  background: #1c1c22;
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 10px;
  padding: 0.9rem 1rem;
  margin-bottom: 0.6rem;
  transition: border-color 0.2s;
}
.history-item:hover { border-color: rgba(244,169,78,0.25); }
.history-time { font-family: 'JetBrains Mono', monospace; font-size: 0.6rem; color: #4a4a5a; margin-bottom: 0.3rem; }
.history-original { font-size: 0.78rem; color: #7a7a8a; font-style: italic; margin-bottom: 0.25rem; }
.history-best { font-size: 0.82rem; color: #6aabf0; }

.stButton > button {
  background: #1c1c22 !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  color: #f0ede8 !important;
  border-radius: 8px !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.85rem !important;
  transition: all 0.2s !important;
}
.stButton > button:hover { border-color: rgba(244,169,78,0.4) !important; color: #f4a94e !important; }
.stSpinner > div { border-top-color: #f4a94e !important; }
audio { filter: invert(1) hue-rotate(180deg); border-radius: 8px; width: 100%; }
</style>
""", unsafe_allow_html=True)


# ── SESSION STATE ──
if "history" not in st.session_state:
    st.session_state.history = []
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "api_keys_set" not in st.session_state:
    st.session_state.api_keys_set = False

# ── AUTO-LOAD FROM SECRETS ──
try:
    _sarvam_secret = st.secrets.get("SARVAM_API_KEY", "")
    _groq_secret = st.secrets.get("GROQ_API_KEY", "")
    if _sarvam_secret and _groq_secret:
        st.session_state.sarvam_key = _sarvam_secret
        st.session_state.groq_key = _groq_secret
        st.session_state.api_keys_set = True
        st.session_state.keys_from_secrets = True
except Exception:
    st.session_state.keys_from_secrets = False


# ── SIDEBAR ──
with st.sidebar:
    st.markdown("""
    <div style='padding: 0.5rem 0 1.5rem'>
      <div style='font-family: Playfair Display, serif; font-size: 1.5rem; font-weight: 700; color: #f0ede8'>
        Bolo<span style='color:#f4a94e'>Better</span>
      </div>
      <div style='font-family: JetBrains Mono, monospace; font-size: 0.6rem; letter-spacing: 0.15em; color: #4a4a5a; text-transform: uppercase; margin-top: 0.2rem'>
        Hindi → English Coach
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get("keys_from_secrets"):
        st.markdown("#### 🔑 API Keys")
        st.success("Keys loaded from secrets ✓")
        st.caption("Saved securely in Streamlit settings.")
    else:
        st.markdown("#### 🔑 API Keys")
        sarvam_key = st.text_input("Sarvam AI Key", type="password", placeholder="sk_...", help="dashboard.sarvam.ai")
        groq_key = st.text_input("Groq Key (Free)", type="password", placeholder="gsk_...", help="console.groq.com")
        if sarvam_key and groq_key:
            st.session_state.sarvam_key = sarvam_key
            st.session_state.groq_key = groq_key
            st.session_state.api_keys_set = True
            st.success("Keys saved ✓")
        else:
            st.session_state.api_keys_set = False
            st.warning("Enter both keys to start")

    st.divider()

    st.markdown("#### 🎙️ Voice Settings")
    speaker = st.selectbox("TTS Voice", ["ishita", "priya", "neha", "simran", "kavya", "shreya", "ritu", "shubh", "aditya", "rahul"], index=0)
    pace = st.slider("Speaking pace", 0.5, 1.5, 0.9, 0.1)
    st.session_state.speaker = speaker
    st.session_state.pace = pace

    st.divider()

    st.markdown("#### 📖 How to use")
    st.markdown("""
    <div style='font-size: 0.8rem; color: #7a7a8a; line-height: 1.9; font-family: DM Sans, sans-serif'>
    1. Enter API keys above<br>
    2. Record Hindi voice<br>
    3. Get 4 English versions<br>
    4. Learn 3 vocab words<br>
    5. Play any version back!
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("#### 🕐 Session History")
    if st.session_state.history:
        if st.button("🗑️ Clear history", use_container_width=True):
            st.session_state.history = []
            st.session_state.current_result = None
            st.rerun()
        for item in reversed(st.session_state.history[-10:]):
            st.markdown(f"""
            <div class='history-item'>
              <div class='history-time'>{item['timestamp']}</div>
              <div class='history-original'>"{item['translated'][:55]}{'...' if len(item['translated']) > 55 else ''}"</div>
              <div class='history-best'>{item['suggestions'].get('professional', '')[:55]}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:0.8rem; color:#4a4a5a'>No history yet</div>", unsafe_allow_html=True)


# ── GROQ API CALL ──
def call_groq(system_prompt, user_message):
    headers = {
        "Authorization": f"Bearer {st.session_state.groq_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 600,
        "temperature": 0.75
    }
    resp = httpx.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=30)
    if resp.status_code != 200:
        raise Exception(f"Groq error: {resp.text}")
    return resp.json()["choices"][0]["message"]["content"]


# ── TTS FUNCTION ──
def get_tts(text):
    if not text: return None
    try:
        headers = {"api-subscription-key": st.session_state.sarvam_key, "Content-Type": "application/json"}
        payload = {
            "target_language_code": "en-IN",
            "text": text[:500],
            "model": "bulbul:v3",
            "speaker": st.session_state.get("speaker", "ishita"),
            "pace": st.session_state.get("pace", 0.9),
            "speech_sample_rate": 22050
        }
        resp = httpx.post("https://api.sarvam.ai/text-to-speech", headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            return resp.json().get("audios", [None])[0]
    except Exception:
        return None


# ── MAIN CONTENT ──
st.markdown("""
<div class='hero-title'>Speak in Hindi.<br><span>Sound brilliant</span> in English.</div>
<div class='hero-sub'>Record Hindi → get 4 polished English versions including Pro Speak with idioms → learn 3 vocabulary words → hear it all spoken back.</div>
""", unsafe_allow_html=True)

if not st.session_state.api_keys_set:
    st.info("👈 Enter your Sarvam AI and Groq API keys in the sidebar to get started.")
    st.stop()

# ── LAYOUT ──
col1, col2 = st.columns([1.1, 1])

with col1:
    tab1, tab2 = st.tabs(["🎤 Record Voice", "📁 Upload Audio"])

    with tab1:
        st.markdown("<div class='section-label'>Record yourself speaking in Hindi</div>", unsafe_allow_html=True)
        audio_value = st.audio_input("Speak in Hindi", label_visibility="collapsed")

    with tab2:
        st.markdown("<div class='section-label'>Or upload a Hindi audio file</div>", unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a", "webm", "ogg"], label_visibility="collapsed")

    audio_to_process = audio_value if audio_value else uploaded

    if audio_to_process:
        audio_bytes = audio_to_process.read()

        if st.button("✨ Translate & Suggest", use_container_width=True, type="primary"):

            # ── STEP 1: SARVAM STT ──
            with st.spinner("Translating your Hindi..."):
                try:
                    headers_sarvam = {"api-subscription-key": st.session_state.sarvam_key}
                    files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
                    data = {"model": "saaras:v3", "mode": "translate", "with_diarization": "false"}
                    resp = httpx.post("https://api.sarvam.ai/speech-to-text-translate", files=files, data=data, headers=headers_sarvam, timeout=60)
                    if resp.status_code != 200:
                        st.error(f"Sarvam error: {resp.text}")
                        st.stop()
                    translated = resp.json().get("transcript", "").strip()
                    if not translated:
                        st.error("Could not understand. Please speak clearly in Hindi.")
                        st.stop()
                except Exception as e:
                    st.error(f"Translation error: {e}")
                    st.stop()

            # ── STEP 2: GROQ — 4 SUGGESTIONS + VOCAB + QUOTE ──
            with st.spinner("Getting 4 English versions + vocabulary + quote..."):
                try:
                    system_prompt = """You are an expert English communication coach for Hindi speakers.

Given a translated Hindi sentence, provide:

1. Four ways to say it — Casual, Professional, Formal, and Pro Speak
   - Casual: Natural everyday English
   - Professional: Polished workplace English
   - Formal: Very formal/official English
   - Pro Speak: Uses idioms, phrasal verbs, and sophisticated expressions — the kind of English that impresses people. Sound like a native, confident, stylish speaker.

2. A grammar/expression tip (1 sentence)

3. Exactly 3 vocabulary words from your suggestions that a learner might find difficult.
   For each word give: meaning (short), 2 synonyms, 1 antonym

4. One short motivating quote about language, learning, or confidence — with the author name.

Respond in EXACTLY this format (plain text only, no markdown, no asterisks):

What you said: [translated sentence]

Casual: [casual version]
Professional: [professional version]
Formal: [formal version]
Pro Speak: [idioms and phrasal verbs version]

Tip: [one sentence tip]

VOCAB
Word1: [word]
Meaning1: [short meaning]
Synonyms1: [syn1, syn2]
Antonym1: [antonym]

Word2: [word]
Meaning2: [short meaning]
Synonyms2: [syn1, syn2]
Antonym2: [antonym]

Word3: [word]
Meaning3: [short meaning]
Synonyms3: [syn1, syn2]
Antonym3: [antonym]

Quote: [motivating quote text]
Author: [author name]"""

                    raw = call_groq(system_prompt, f'Hindi speech translated to English: "{translated}"\nProvide all 4 versions, 3 vocab words, and a motivating quote.')

                    # Parse response
                    lines = raw.strip().split("\n")
                    parsed = {
                        "what_you_said": translated,
                        "casual": "", "professional": "", "formal": "", "pro_speak": "",
                        "tip": "",
                        "vocab": [],
                        "quote": "", "author": ""
                    }

                    current_word = {}
                    in_vocab = False

                    for line in lines:
                        l = line.strip()
                        if not l:
                            continue
                        low = l.lower()

                        if low.startswith("what you said:"):
                            parsed["what_you_said"] = l.split(":", 1)[1].strip()
                        elif low.startswith("casual:"):
                            parsed["casual"] = l.split(":", 1)[1].strip()
                            in_vocab = False
                        elif low.startswith("professional:"):
                            parsed["professional"] = l.split(":", 1)[1].strip()
                        elif low.startswith("formal:"):
                            parsed["formal"] = l.split(":", 1)[1].strip()
                        elif low.startswith("pro speak:"):
                            parsed["pro_speak"] = l.split(":", 1)[1].strip()
                        elif low.startswith("tip:"):
                            parsed["tip"] = l.split(":", 1)[1].strip()
                        elif low == "vocab":
                            in_vocab = True
                        elif in_vocab and low.startswith("word"):
                            if current_word and "word" in current_word:
                                parsed["vocab"].append(current_word)
                            current_word = {"word": l.split(":", 1)[1].strip()}
                        elif in_vocab and low.startswith("meaning"):
                            current_word["meaning"] = l.split(":", 1)[1].strip()
                        elif in_vocab and low.startswith("synonyms"):
                            current_word["synonyms"] = l.split(":", 1)[1].strip()
                        elif in_vocab and low.startswith("antonym"):
                            current_word["antonym"] = l.split(":", 1)[1].strip()
                        elif low.startswith("quote:"):
                            if current_word and "word" in current_word:
                                parsed["vocab"].append(current_word)
                                current_word = {}
                            in_vocab = False
                            parsed["quote"] = l.split(":", 1)[1].strip()
                        elif low.startswith("author:"):
                            parsed["author"] = l.split(":", 1)[1].strip()

                    if current_word and "word" in current_word:
                        parsed["vocab"].append(current_word)

                except Exception as e:
                    st.error(f"AI error: {e}")
                    st.stop()

            # ── STEP 3: TTS FOR PROFESSIONAL VERSION ──
            with st.spinner("Generating audio..."):
                tts_audio_b64 = get_tts(parsed["professional"])

            # Save
            entry = {
                "id": datetime.now().isoformat(),
                "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "translated": translated,
                "suggestions": parsed,
                "tts_audio": tts_audio_b64
            }
            st.session_state.current_result = entry
            st.session_state.history.append(entry)
            st.rerun()


# ── RESULTS PANEL ──
with col2:
    if st.session_state.current_result:
        r = st.session_state.current_result
        s = r["suggestions"]

        # Translated
        st.markdown("<div class='section-label'>What you said in Hindi (translated)</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='translated-box'>\"{s.get('what_you_said', r['translated'])}\"</div>", unsafe_allow_html=True)

        # 4 Suggestion Cards
        st.markdown("<div class='section-label'>4 Ways to Say It in English</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='suggestion-grid'>
          <div class='suggestion-card'>
            <div class='card-tag' style='color:#6ec6a0'><span class='dot' style='background:#6ec6a0'></span>Casual</div>
            <div class='card-text'>{s.get('casual', '—')}</div>
          </div>
          <div class='suggestion-card'>
            <div class='card-tag' style='color:#6aabf0'><span class='dot' style='background:#6aabf0'></span>Professional</div>
            <div class='card-text'>{s.get('professional', '—')}</div>
          </div>
          <div class='suggestion-card'>
            <div class='card-tag' style='color:#b89af0'><span class='dot' style='background:#b89af0'></span>Formal</div>
            <div class='card-text'>{s.get('formal', '—')}</div>
          </div>
          <div class='suggestion-card prospeak-card'>
            <div class='card-tag' style='color:#f4a94e'><span class='dot' style='background:#f4a94e'></span>✦ Pro Speak</div>
            <div class='prospeak-text'>{s.get('pro_speak', '—')}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Tip
        if s.get("tip"):
            st.markdown(f"<div class='tip-box'>💡 {s['tip']}</div>", unsafe_allow_html=True)

        # Auto-play professional
        if r.get("tts_audio"):
            st.markdown("<div class='section-label' style='margin-top:1rem'>🔊 Professional version (auto-played)</div>", unsafe_allow_html=True)
            st.audio(base64.b64decode(r["tts_audio"]), format="audio/wav")

        # Play all 4 versions
        st.markdown("<div class='section-label' style='margin-top:1rem'>▶ Play any version</div>", unsafe_allow_html=True)
        pc1, pc2, pc3, pc4 = st.columns(4)

        def play_version(text, label):
            audio = get_tts(text)
            if audio:
                st.session_state[f"play_{label}"] = audio

        with pc1:
            if st.button("Casual", use_container_width=True):
                with st.spinner(""):
                    play_version(s.get("casual", ""), "casual")
            if st.session_state.get("play_casual"):
                st.audio(base64.b64decode(st.session_state["play_casual"]), format="audio/wav")

        with pc2:
            if st.button("Pro", use_container_width=True):
                with st.spinner(""):
                    play_version(s.get("professional", ""), "professional")
            if st.session_state.get("play_professional"):
                st.audio(base64.b64decode(st.session_state["play_professional"]), format="audio/wav")

        with pc3:
            if st.button("Formal", use_container_width=True):
                with st.spinner(""):
                    play_version(s.get("formal", ""), "formal")
            if st.session_state.get("play_formal"):
                st.audio(base64.b64decode(st.session_state["play_formal"]), format="audio/wav")

        with pc4:
            if st.button("✦ Pro Speak", use_container_width=True):
                with st.spinner(""):
                    play_version(s.get("pro_speak", ""), "pro_speak")
            if st.session_state.get("play_pro_speak"):
                st.audio(base64.b64decode(st.session_state["play_pro_speak"]), format="audio/wav")

        # ── VOCABULARY SECTION ──
        if s.get("vocab"):
            st.markdown("<div class='section-label' style='margin-top:1.5rem'>📚 Vocabulary Builder — 3 Words to Learn</div>", unsafe_allow_html=True)
            vocab_html = "<div class='vocab-grid'>"
            for v in s["vocab"][:3]:
                vocab_html += f"""
                <div class='vocab-card'>
                  <div class='vocab-word'>{v.get('word', '')}</div>
                  <div class='vocab-meaning'>{v.get('meaning', '')}</div>
                  <div class='vocab-syn'>↑ {v.get('synonyms', '')}</div>
                  <div class='vocab-ant'>↓ {v.get('antonym', '')}</div>
                </div>"""
            vocab_html += "</div>"
            st.markdown(vocab_html, unsafe_allow_html=True)

        # ── MOTIVATING QUOTE ──
        if s.get("quote"):
            st.markdown(f"""
            <div class='quote-box'>
              <div class='quote-text'>"{s['quote']}"</div>
              <div class='quote-author'>— {s.get('author', '')}</div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style='display:flex; flex-direction:column; align-items:center; justify-content:center;
                    height:340px; background:#141417; border: 1px solid rgba(255,255,255,0.07);
                    border-radius:16px; text-align:center; padding:2rem;'>
          <div style='font-size:3rem; margin-bottom:1rem'>🎙️</div>
          <div style='font-family: DM Sans, sans-serif; font-size:0.9rem; color:#4a4a5a; line-height:1.9'>
            Record or upload a Hindi audio clip<br>
            and your results will appear here.<br><br>
            <span style='color:#f4a94e; font-size:0.8rem'>4 English versions · 3 vocab words · 1 quote</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
