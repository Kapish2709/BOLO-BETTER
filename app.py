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

/* Hide Streamlit default elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; max-width: 1100px; }

:root {
  --accent: #f4a94e;
  --casual: #6ec6a0;
  --professional: #6aabf0;
  --formal: #b89af0;
}

/* App background */
.stApp { background: #0d0d0f; color: #f0ede8; }
[data-testid="stSidebar"] { background: #141417 !important; border-right: 1px solid rgba(255,255,255,0.07); }

/* Hero title */
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

/* Suggestion cards */
.suggestion-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1rem;
  margin: 1.2rem 0;
}
.suggestion-card {
  background: #1c1c22;
  border-radius: 12px;
  padding: 1.2rem;
  border: 1px solid rgba(255,255,255,0.07);
  transition: border-color 0.2s;
}
.suggestion-card:hover { border-color: rgba(244,169,78,0.3); }
.card-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  font-weight: 500;
  margin-bottom: 0.6rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  display: inline-block;
}
.card-text {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.92rem;
  line-height: 1.6;
  color: #f0ede8;
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

/* History items */
.history-item {
  background: #1c1c22;
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 10px;
  padding: 0.9rem 1rem;
  margin-bottom: 0.6rem;
  cursor: pointer;
  transition: border-color 0.2s;
}
.history-item:hover { border-color: rgba(244,169,78,0.25); }
.history-time {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  color: #4a4a5a;
  margin-bottom: 0.3rem;
}
.history-original {
  font-size: 0.78rem;
  color: #7a7a8a;
  font-style: italic;
  margin-bottom: 0.25rem;
}
.history-best {
  font-size: 0.82rem;
  color: #6aabf0;
}

/* Streamlit button overrides */
.stButton > button {
  background: #1c1c22 !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  color: #f0ede8 !important;
  border-radius: 8px !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.85rem !important;
  transition: all 0.2s !important;
}
.stButton > button:hover {
  border-color: rgba(244,169,78,0.4) !important;
  color: #f4a94e !important;
}

/* Spinner */
.stSpinner > div { border-top-color: #f4a94e !important; }

/* Audio player */
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

# ── AUTO-LOAD KEYS FROM STREAMLIT SECRETS ──
# If secrets are saved in Streamlit Cloud, load them automatically
# so users never have to type them manually
try:
    _sarvam_secret = st.secrets.get("SARVAM_API_KEY", "")
    _openai_secret = st.secrets.get("OPENAI_API_KEY", "")
    if _sarvam_secret and _openai_secret:
        st.session_state.sarvam_key = _sarvam_secret
        st.session_state.openai_key = _openai_secret
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

    # Only show key input boxes if secrets are NOT already loaded
    if st.session_state.get("keys_from_secrets"):
        st.markdown("#### 🔑 API Keys")
        st.success("Keys loaded from secrets ✓")
        st.caption("Your API keys are saved securely in Streamlit settings.")
    else:
        st.markdown("#### 🔑 API Keys")
        sarvam_key = st.text_input("Sarvam AI Key", type="password", placeholder="sk_...", help="Get from dashboard.sarvam.ai")
        openai_key = st.text_input("OpenAI Key", type="password", placeholder="sk-proj-...", help="Get from platform.openai.com/api-keys")

        if sarvam_key and openai_key:
            st.session_state.sarvam_key = sarvam_key
            st.session_state.openai_key = openai_key
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
    <div style='font-size: 0.8rem; color: #7a7a8a; line-height: 1.8; font-family: DM Sans, sans-serif'>
    1. Enter your API keys above<br>
    2. Record your voice below<br>
    3. Get 3 English suggestions<br>
    4. Play them back & learn!
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # History
    st.markdown("#### 🕐 Session History")
    if st.session_state.history:
        if st.button("🗑️ Clear history", use_container_width=True):
            st.session_state.history = []
            st.session_state.current_result = None
            st.rerun()

        for i, item in enumerate(reversed(st.session_state.history[-10:])):
            st.markdown(f"""
            <div class='history-item'>
              <div class='history-time'>{item['timestamp']}</div>
              <div class='history-original'>"{item['translated'][:60]}{'...' if len(item['translated']) > 60 else ''}"</div>
              <div class='history-best'>{item['suggestions'].get('professional', '')[:60]}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:0.8rem; color:#4a4a5a'>No history yet</div>", unsafe_allow_html=True)


# ── MAIN CONTENT ──
st.markdown("""
<div class='hero-title'>Speak in Hindi.<br><span>Sound brilliant</span> in English.</div>
<div class='hero-sub'>Record yourself speaking in Hindi → get your message translated + 3 polished English versions → hear them spoken back.</div>
""", unsafe_allow_html=True)

if not st.session_state.api_keys_set:
    st.info("👈 Enter your Sarvam AI and OpenAI API keys in the sidebar to get started.")
    st.stop()


# ── RECORDER COMPONENT ──
# Custom HTML component that handles mic recording in browser
recorder_html = """
<style>
  .rec-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.2rem;
    padding: 2rem;
    background: #141417;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    margin-bottom: 1rem;
  }
  .rec-btn {
    width: 100px; height: 100px;
    border-radius: 50%;
    background: #1c1c22;
    border: 2px solid rgba(244,169,78,0.3);
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: all 0.3s;
    font-size: 2.2rem;
    outline: none;
  }
  .rec-btn:hover { border-color: #f4a94e; transform: scale(1.05); }
  .rec-btn.recording {
    background: rgba(244,169,78,0.15);
    border-color: #f4a94e;
    animation: pulse 1.5s ease-out infinite;
  }
  @keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(244,169,78,0.4); }
    70% { box-shadow: 0 0 0 20px rgba(244,169,78,0); }
    100% { box-shadow: 0 0 0 0 rgba(244,169,78,0); }
  }
  .rec-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #7a7a8a;
    letter-spacing: 0.05em;
  }
  .rec-label.active { color: #f4a94e; }
  .waveform {
    display: flex; align-items: center; gap: 3px;
    height: 28px; opacity: 0; transition: opacity 0.3s;
  }
  .waveform.active { opacity: 1; }
  .wbar {
    width: 3px; background: #f4a94e; border-radius: 2px;
    animation: wv 0.8s ease-in-out infinite; min-height: 4px;
  }
  .wbar:nth-child(1){animation-delay:0s}
  .wbar:nth-child(2){animation-delay:0.1s}
  .wbar:nth-child(3){animation-delay:0.2s}
  .wbar:nth-child(4){animation-delay:0.3s}
  .wbar:nth-child(5){animation-delay:0.2s}
  .wbar:nth-child(6){animation-delay:0.1s}
  @keyframes wv { 0%,100%{height:4px} 50%{height:24px} }
  #audioOut { display:none; }
</style>

<div class='rec-wrap'>
  <button class='rec-btn' id='recBtn' onclick='toggleRec()'>🎤</button>
  <div class='waveform' id='waveform'>
    <div class='wbar'></div><div class='wbar'></div>
    <div class='wbar'></div><div class='wbar'></div>
    <div class='wbar'></div><div class='wbar'></div>
  </div>
  <div class='rec-label' id='recLabel'>Click mic to start recording</div>
</div>
<input type='text' id='audioOut' />

<script>
let mediaRec = null, chunks = [], isRec = false;

async function toggleRec() {
  isRec ? stopRec() : await startRec();
}

async function startRec() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    chunks = [];
    mediaRec = new MediaRecorder(stream);
    mediaRec.ondataavailable = e => chunks.push(e.data);
    mediaRec.onstop = processAudio;
    mediaRec.start();
    isRec = true;
    document.getElementById('recBtn').classList.add('recording');
    document.getElementById('recBtn').textContent = '⏹';
    document.getElementById('waveform').classList.add('active');
    document.getElementById('recLabel').textContent = 'Recording... Click to stop';
    document.getElementById('recLabel').classList.add('active');
  } catch(e) {
    document.getElementById('recLabel').textContent = 'Mic error: ' + e.message;
  }
}

function stopRec() {
  if (mediaRec) {
    mediaRec.stop();
    mediaRec.stream.getTracks().forEach(t => t.stop());
    isRec = false;
    document.getElementById('recBtn').classList.remove('recording');
    document.getElementById('recBtn').textContent = '🎤';
    document.getElementById('waveform').classList.remove('active');
    document.getElementById('recLabel').textContent = 'Processing...';
  }
}

async function processAudio() {
  const blob = new Blob(chunks, { type: 'audio/webm' });
  const wav = await toWav(blob);
  const b64 = await toBase64(wav);
  // Send to Streamlit via query param trick
  const data = b64.split(',')[1];
  window.parent.postMessage({ type: 'streamlit:setComponentValue', value: data }, '*');
  document.getElementById('recLabel').textContent = 'Click mic to record again';
}

function toBase64(blob) {
  return new Promise(r => {
    const reader = new FileReader();
    reader.onloadend = () => r(reader.result);
    reader.readAsDataURL(blob);
  });
}

async function toWav(blob) {
  const ctx = new AudioContext();
  const buf = await blob.arrayBuffer();
  const decoded = await ctx.decodeAudioData(buf);
  const sr = 16000, len = decoded.duration * sr;
  const off = new OfflineAudioContext(1, len, sr);
  const src = off.createBufferSource();
  src.buffer = decoded;
  src.connect(off.destination);
  src.start();
  const rendered = await off.startRendering();
  return bufToWav(rendered);
}

function bufToWav(buf) {
  const data = buf.getChannelData(0);
  const pcm = new Int16Array(data.length);
  for (let i = 0; i < data.length; i++) pcm[i] = Math.max(-32768, Math.min(32767, data[i] * 32768));
  const wb = new ArrayBuffer(44 + pcm.length * 2);
  const v = new DataView(wb);
  const s = (str, o) => [...str].forEach((c,i) => v.setUint8(o+i, c.charCodeAt(0)));
  s('RIFF',0); v.setUint32(4,36+pcm.length*2,true);
  s('WAVE',8); s('fmt ',12);
  v.setUint32(16,16,true); v.setUint16(20,1,true); v.setUint16(22,1,true);
  v.setUint32(24,16000,true); v.setUint32(28,32000,true);
  v.setUint16(32,2,true); v.setUint16(34,16,true);
  s('data',36); v.setUint32(40,pcm.length*2,true);
  new Int16Array(wb,44).set(pcm);
  return new Blob([wb], {type:'audio/wav'});
}
</script>
"""

# ── AUDIO UPLOAD FALLBACK ──
col1, col2 = st.columns([1.2, 1])

with col1:
    tab1, tab2 = st.tabs(["🎤 Record Voice", "📁 Upload Audio"])

    with tab1:
        st.markdown("<div class='section-label'>Record yourself speaking in Hindi</div>", unsafe_allow_html=True)
        # Since Streamlit components need a package for full bidirectional comm,
        # we use st.audio_input which is native in Streamlit >= 1.31
        audio_value = st.audio_input("Speak in Hindi", label_visibility="collapsed")

    with tab2:
        st.markdown("<div class='section-label'>Or upload a Hindi audio file</div>", unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a", "webm", "ogg"], label_visibility="collapsed")
        audio_value_upload = uploaded

    # Process whichever audio we have
    audio_to_process = audio_value if audio_value else (audio_value_upload if 'audio_value_upload' in dir() else None)

    if audio_to_process:
        audio_bytes = audio_to_process.read()
        audio_b64 = base64.b64encode(audio_bytes).decode()

        if st.button("✨ Translate & Suggest", use_container_width=True, type="primary"):
            with st.spinner("Translating your Hindi..."):
                try:
                    # Step 1: Sarvam STT translate
                    headers_sarvam = {"api-subscription-key": st.session_state.sarvam_key}
                    files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
                    data = {"model": "saaras:v3", "mode": "translate", "with_diarization": "false"}

                    resp = httpx.post(
                        "https://api.sarvam.ai/speech-to-text-translate",
                        files=files, data=data, headers=headers_sarvam, timeout=60
                    )

                    if resp.status_code != 200:
                        st.error(f"Sarvam error: {resp.text}")
                        st.stop()

                    translated = resp.json().get("transcript", "").strip()
                    if not translated:
                        st.error("Could not understand audio. Please speak clearly in Hindi.")
                        st.stop()

                except Exception as e:
                    st.error(f"Translation error: {e}")
                    st.stop()

            with st.spinner("Getting English suggestions from AI..."):
                try:
                    # Step 2: OpenAI suggestions
                    headers_oai = {"Authorization": f"Bearer {st.session_state.openai_key}", "Content-Type": "application/json"}
                    system_prompt = """You are a friendly English communication coach helping Hindi speakers.

The user spoke in Hindi. Their speech was translated to English. Give them better ways to say the same thing.

Respond in EXACTLY this format (plain text, no markdown):
What you said: [the translated text]

Casual: [casual natural version]
Professional: [professional version]
Formal: [formal version]

Tip: [one short sentence tip about why these sound better]"""

                    payload = {
                        "model": "gpt-4o",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f'Hindi speech translated to: "{translated}"\nProvide better English versions.'}
                        ],
                        "max_tokens": 350,
                        "temperature": 0.7
                    }

                    resp2 = httpx.post("https://api.openai.com/v1/chat/completions", headers=headers_oai, json=payload, timeout=30)

                    if resp2.status_code != 200:
                        st.error(f"OpenAI error: {resp2.text}")
                        st.stop()

                    suggestion_text = resp2.json()["choices"][0]["message"]["content"]
                    lines = suggestion_text.strip().split("\n")
                    parsed = {"what_you_said": translated, "casual": "", "professional": "", "formal": "", "tip": ""}
                    for line in lines:
                        l = line.strip()
                        if l.lower().startswith("what you said:"): parsed["what_you_said"] = l.split(":",1)[1].strip()
                        elif l.lower().startswith("casual:"): parsed["casual"] = l.split(":",1)[1].strip()
                        elif l.lower().startswith("professional:"): parsed["professional"] = l.split(":",1)[1].strip()
                        elif l.lower().startswith("formal:"): parsed["formal"] = l.split(":",1)[1].strip()
                        elif l.lower().startswith("tip:"): parsed["tip"] = l.split(":",1)[1].strip()

                except Exception as e:
                    st.error(f"AI error: {e}")
                    st.stop()

            with st.spinner("Generating audio..."):
                try:
                    # Step 3: TTS for professional version
                    tts_audio_b64 = None
                    if parsed["professional"]:
                        headers_tts = {"api-subscription-key": st.session_state.sarvam_key, "Content-Type": "application/json"}
                        tts_payload = {
                            "target_language_code": "en-IN",
                            "text": parsed["professional"][:500],
                            "model": "bulbul:v3",
                            "speaker": st.session_state.get("speaker", "ishita"),
                            "pace": st.session_state.get("pace", 0.9),
                            "speech_sample_rate": 22050
                        }
                        tts_resp = httpx.post("https://api.sarvam.ai/text-to-speech", headers=headers_tts, json=tts_payload, timeout=30)
                        if tts_resp.status_code == 200:
                            tts_audio_b64 = tts_resp.json().get("audios", [None])[0]
                except Exception:
                    tts_audio_b64 = None

            # Save result
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

with col2:
    # ── RESULTS PANEL ──
    if st.session_state.current_result:
        r = st.session_state.current_result
        s = r["suggestions"]

        st.markdown("<div class='section-label'>What you said in Hindi (translated)</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='translated-box'>\"{s.get('what_you_said', r['translated'])}\"</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-label'>3 Better Ways to Say It</div>", unsafe_allow_html=True)
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
        </div>
        """, unsafe_allow_html=True)

        if s.get("tip"):
            st.markdown(f"<div class='tip-box'>💡 {s['tip']}</div>", unsafe_allow_html=True)

        # TTS audio player
        if r.get("tts_audio"):
            st.markdown("<div class='section-label' style='margin-top:1rem'>🔊 Hear the professional version</div>", unsafe_allow_html=True)
            audio_bytes_out = base64.b64decode(r["tts_audio"])
            st.audio(audio_bytes_out, format="audio/wav")

        # Play other versions
        st.markdown("<div class='section-label' style='margin-top:1rem'>Play a different version</div>", unsafe_allow_html=True)
        pcol1, pcol2, pcol3 = st.columns(3)

        def play_version(text, label):
            if not text: return
            try:
                headers_tts = {"api-subscription-key": st.session_state.sarvam_key, "Content-Type": "application/json"}
                tts_payload = {
                    "target_language_code": "en-IN",
                    "text": text[:500],
                    "model": "bulbul:v3",
                    "speaker": st.session_state.get("speaker", "ishita"),
                    "pace": st.session_state.get("pace", 0.9),
                    "speech_sample_rate": 22050
                }
                resp = httpx.post("https://api.sarvam.ai/text-to-speech", headers=headers_tts, json=tts_payload, timeout=30)
                if resp.status_code == 200:
                    audio_b64 = resp.json().get("audios", [None])[0]
                    if audio_b64:
                        st.session_state[f"play_{label}"] = audio_b64
            except Exception as e:
                st.error(f"TTS error: {e}")

        with pcol1:
            if st.button("▶ Casual", use_container_width=True):
                with st.spinner(""):
                    play_version(s.get("casual", ""), "casual")
            if st.session_state.get("play_casual"):
                st.audio(base64.b64decode(st.session_state["play_casual"]), format="audio/wav")

        with pcol2:
            if st.button("▶ Professional", use_container_width=True):
                with st.spinner(""):
                    play_version(s.get("professional", ""), "professional")
            if st.session_state.get("play_professional"):
                st.audio(base64.b64decode(st.session_state["play_professional"]), format="audio/wav")

        with pcol3:
            if st.button("▶ Formal", use_container_width=True):
                with st.spinner(""):
                    play_version(s.get("formal", ""), "formal")
            if st.session_state.get("play_formal"):
                st.audio(base64.b64decode(st.session_state["play_formal"]), format="audio/wav")

    else:
        st.markdown("""
        <div style='display:flex; flex-direction:column; align-items:center; justify-content:center;
                    height:300px; background:#141417; border: 1px solid rgba(255,255,255,0.07);
                    border-radius:16px; text-align:center; padding:2rem;'>
          <div style='font-size:3rem; margin-bottom:1rem'>🎙️</div>
          <div style='font-family: DM Sans, sans-serif; font-size:0.9rem; color:#4a4a5a; line-height:1.8'>
            Record or upload a Hindi audio clip<br>and your results will appear here.
          </div>
        </div>
        """, unsafe_allow_html=True)
