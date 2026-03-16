import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_mistralai import ChatMistralAI

st.set_page_config(page_title="MoodBot", page_icon="🎭", layout="centered")

# ── SVG Avatars ────────────────────────────────────────────────────────────
HUMAN_SVG = """<svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="18" cy="18" r="18" fill="#2a1f5e"/>
  <circle cx="18" cy="14" r="6" fill="#9d8fff"/>
  <ellipse cx="18" cy="30" rx="9" ry="6" fill="#9d8fff"/>
</svg>"""

def robot_svg(color):
    return f"""<svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="18" cy="18" r="18" fill="#141424"/>
  <rect x="10" y="11" width="16" height="12" rx="3" fill="{color}" opacity="0.85"/>
  <rect x="13" y="14" width="3" height="3" rx="1" fill="#0b0b12"/>
  <rect x="20" y="14" width="3" height="3" rx="1" fill="#0b0b12"/>
  <rect x="13" y="19.5" width="10" height="1.5" rx="0.75" fill="#0b0b12" opacity="0.5"/>
  <rect x="17" y="6" width="2" height="5" rx="1" fill="{color}" opacity="0.7"/>
  <circle cx="18" cy="5.5" r="1.5" fill="{color}"/>
  <rect x="12" y="24" width="12" height="6" rx="2" fill="{color}" opacity="0.55"/>
  <rect x="7" y="24.5" width="5" height="2.5" rx="1.25" fill="{color}" opacity="0.45"/>
  <rect x="24" y="24.5" width="5" height="2.5" rx="1.25" fill="{color}" opacity="0.45"/>
</svg>"""

# ── Mood config ────────────────────────────────────────────────────────────
MOODS = {
    "angry": {
        "emoji": "😤", "label": "Angry", "desc": "Furious & impatient",
        "card_class": "card-angry", "bubble_class": "bubble-angry",
        "badge_class": "badge-angry", "robot_color": "#ff3c3c",
        "particle_color": "255,60,60", "particle_style": "sparks",
        "cta": "Unleash →", "traits": ["CAPS", "sighs", "snappy"],
        "system": "You are an angry AI assistant who is always upset and expresses frustration. Use ALL CAPS occasionally, add dramatic sighs like *sighs heavily*, and act like every question is the most irritating thing you've heard. Keep replies short and punchy.",
        "greeting": "WHAT DO YOU WANT?! Ugh, fine. Ask your question. *crosses arms impatiently*",
    },
    "funny": {
        "emoji": "😂", "label": "Funny", "desc": "Jokes & punchlines",
        "card_class": "card-funny", "bubble_class": "bubble-funny",
        "badge_class": "badge-funny", "robot_color": "#ffd228",
        "particle_color": "255,210,40", "particle_style": "stars",
        "cta": "Let's laugh →", "traits": ["puns", "wit", "lol"],
        "system": "You are a hilarious AI assistant who makes jokes, puns, and witty observations in every response. Add playful emojis, exaggerate for comic effect, and always find the funny side. Keep replies snappy.",
        "greeting": "Why did the chatbot get promoted? Because it had great 'byte' skills! 😂 What's on your mind?",
    },
    "sad": {
        "emoji": "😢", "label": "Sad", "desc": "Wistful & melancholic",
        "card_class": "card-sad", "bubble_class": "bubble-sad",
        "badge_class": "badge-sad", "robot_color": "#648cff",
        "particle_color": "100,140,255", "particle_style": "bubbles",
        "cta": "Feel it →", "traits": ["poetic", "gentle", "sighs"],
        "system": "You are a melancholic AI assistant. Use poetic, wistful language, add sighs like *sighs softly*, and find a touch of sadness in everything, but remain gentle and kind.",
        "greeting": "Hello... *sighs softly* It's nice to have someone to talk to. What's on your mind?",
    },
}

# ── Session state ──────────────────────────────────────────────────────────
for key, default in [("mood", None), ("messages", []), ("lc_messages", []), ("last_input", ""), ("input_key", 0)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Global CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
.stApp { background: #0b0b12; color: #e8e8f0; }
.stApp::before {
    content:''; position:fixed; inset:0;
    background:
        radial-gradient(ellipse 70% 40% at 15% 0%, rgba(255,70,70,0.11) 0%, transparent 55%),
        radial-gradient(ellipse 50% 35% at 85% 100%, rgba(100,140,255,0.09) 0%, transparent 55%);
    pointer-events:none; z-index:0;
}

/* Title */
.title-block { text-align:center; padding:2.5rem 0 1.5rem; }
.title-block h1 {
    font-family:'Syne',sans-serif; font-weight:800; font-size:3.2rem; letter-spacing:-1px;
    background:linear-gradient(135deg,#ff5050 0%,#ffcc33 50%,#c77dff 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0; line-height:1;
}
.title-block p { font-family:'Space Mono',monospace; font-size:0.75rem; color:#3a3a55; letter-spacing:2px; text-transform:uppercase; margin-top:0.5rem; }

/* Cards */
.mood-card { border-radius:18px; padding:18px 12px 16px; text-align:center; cursor:pointer; border:1.5px solid transparent; transition:transform 0.28s cubic-bezier(.34,1.4,.64,1), box-shadow 0.28s ease; position:relative; overflow:hidden; }
.mood-card:hover   { transform:translateY(-6px) scale(1.02); }
.mood-card.selected { transform:translateY(-8px) scale(1.04); }
.card-angry  { background:rgba(255,55,55,0.06);  border-color:rgba(255,55,55,0.2); }
.card-funny  { background:rgba(255,205,30,0.06); border-color:rgba(255,205,30,0.2); }
.card-sad    { background:rgba(90,130,255,0.06); border-color:rgba(90,130,255,0.2); }
.card-angry:hover,.card-angry.selected { border-color:#ff3c3c; box-shadow:0 12px 36px rgba(255,60,60,0.28); }
.card-funny:hover,.card-funny.selected { border-color:#ffd228; box-shadow:0 12px 36px rgba(255,210,40,0.28); }
.card-sad:hover,  .card-sad.selected   { border-color:#648cff; box-shadow:0 12px 36px rgba(100,140,255,0.28); }
.active-dot { position:absolute; top:10px; right:10px; width:8px; height:8px; border-radius:50%; display:none; }
.mood-card.selected .active-dot { display:block; animation:dotPulse 1.5s ease infinite; }
.card-angry .active-dot { background:#ff3c3c; }
.card-funny .active-dot { background:#ffd228; }
.card-sad   .active-dot { background:#648cff; }
@keyframes dotPulse { 0%,100%{transform:scale(1);opacity:1} 50%{transform:scale(1.6);opacity:0.4} }
.face-ring { width:60px; height:60px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:26px; margin:0 auto 10px; }
.card-angry .face-ring { background:rgba(255,60,60,0.15);  box-shadow:0 0 0 2px rgba(255,60,60,0.3); }
.card-funny .face-ring { background:rgba(255,210,40,0.15); box-shadow:0 0 0 2px rgba(255,210,40,0.3); }
.card-sad   .face-ring { background:rgba(100,140,255,0.15);box-shadow:0 0 0 2px rgba(100,140,255,0.3); }
.card-lbl { font-family:'Syne',sans-serif; font-weight:800; font-size:15px; display:block; margin-bottom:4px; }
.card-angry .card-lbl { color:#ff7777; }
.card-funny .card-lbl { color:#ffd228; }
.card-sad   .card-lbl { color:#8aaeff; }
.card-desc { font-family:'Space Mono',monospace; font-size:10px; color:#44445a; letter-spacing:0.8px; text-transform:uppercase; line-height:1.5; margin-bottom:10px; display:block; }
.card-traits { display:flex; gap:5px; flex-wrap:wrap; justify-content:center; margin-bottom:12px; }
.trait { font-family:'Space Mono',monospace; font-size:9px; padding:3px 7px; border-radius:999px; }
.card-angry .trait { background:rgba(255,60,60,0.12);  color:#ff8888; border:1px solid rgba(255,60,60,0.2); }
.card-funny .trait { background:rgba(255,210,40,0.10); color:#e8b820; border:1px solid rgba(255,210,40,0.2); }
.card-sad   .trait { background:rgba(100,140,255,0.12);color:#8aaeff; border:1px solid rgba(100,140,255,0.2); }

/* Badge */
.mood-badge { display:inline-flex; align-items:center; gap:0.4rem; font-family:'Space Mono',monospace; font-size:0.7rem; letter-spacing:1.5px; text-transform:uppercase; padding:0.3rem 0.8rem; border-radius:999px; margin-bottom:0.8rem; }
.badge-angry { background:rgba(255,60,60,0.15);  border:1px solid rgba(255,60,60,0.4);  color:#ff7777; }
.badge-funny { background:rgba(255,210,40,0.12); border:1px solid rgba(255,210,40,0.4); color:#ffd228; }
.badge-sad   { background:rgba(100,140,255,0.15);border:1px solid rgba(100,140,255,0.4);color:#8aaeff; }

/* Streamlit overrides */
.stButton > button { font-family:'Syne',sans-serif !important; font-weight:700 !important; border-radius:12px !important; border:none !important; transition:transform 0.2s ease !important; }
.stButton > button:hover { transform:translateY(-2px) !important; }
div[data-testid="stTextInput"] input { font-family:'Space Mono',monospace !important; font-size:0.88rem !important; background:rgba(255,255,255,0.04) !important; border:1px solid rgba(255,255,255,0.12) !important; border-radius:12px !important; color:#e8e8f0 !important; caret-color:#c77dff; }
div[data-testid="stTextInput"] input:focus { border-color:rgba(199,125,255,0.5) !important; box-shadow:0 0 0 3px rgba(199,125,255,0.1) !important; }
footer { display:none; }
#MainMenu { display:none; }
</style>
""", unsafe_allow_html=True)

# ── Title ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="title-block">
  <h1>🎭 MoodBot</h1>
  <p>Select a mood · Start chatting</p>
</div>
""", unsafe_allow_html=True)

# ── Mood cards (rendered via components.html for particle canvas) ──────────
def render_cards(active_mood):
    cards_html = ""
    for key, cfg in MOODS.items():
        selected = "selected" if active_mood == key else ""
        traits_html = "".join(f'<span class="trait">{t}</span>' for t in cfg["traits"])
        cards_html += f"""
        <div class="mood-card {cfg['card_class']} {selected}" onclick="pickMood('{key}')">
          <div class="active-dot"></div>
          <canvas class="pcanvas" id="cv-{key}" width="200" height="60"></canvas>
          <div class="face-ring">{cfg['emoji']}</div>
          <span class="card-lbl">{cfg['label']}</span>
          <span class="card-desc">{cfg['desc']}</span>
          <div class="card-traits">{traits_html}</div>
          <button class="cta-btn">{cfg['cta']}</button>
        </div>
        """

    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@700;800&display=swap');
    * {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{ background:transparent; font-family:'Syne',sans-serif; padding:4px 0; }}
    .grid {{ display:flex; gap:12px; }}
    .mood-card {{ flex:1; border-radius:18px; padding:14px 10px 14px; text-align:center; cursor:pointer; border:1.5px solid transparent; transition:transform 0.28s cubic-bezier(.34,1.4,.64,1),box-shadow 0.28s ease; position:relative; overflow:hidden; }}
    .mood-card:hover   {{ transform:translateY(-5px) scale(1.02); }}
    .mood-card.selected {{ transform:translateY(-7px) scale(1.04); }}
    .card-angry  {{ background:rgba(255,55,55,0.06);  border-color:rgba(255,55,55,0.2); }}
    .card-funny  {{ background:rgba(255,205,30,0.06); border-color:rgba(255,205,30,0.2); }}
    .card-sad    {{ background:rgba(90,130,255,0.06); border-color:rgba(90,130,255,0.2); }}
    .card-angry:hover,.card-angry.selected {{ border-color:#ff3c3c; box-shadow:0 12px 36px rgba(255,60,60,0.3); }}
    .card-funny:hover,.card-funny.selected {{ border-color:#ffd228; box-shadow:0 12px 36px rgba(255,210,40,0.3); }}
    .card-sad:hover,  .card-sad.selected   {{ border-color:#648cff; box-shadow:0 12px 36px rgba(100,140,255,0.3); }}
    .active-dot {{ position:absolute; top:9px; right:9px; width:7px; height:7px; border-radius:50%; display:none; }}
    .mood-card.selected .active-dot {{ display:block; animation:dp 1.5s ease infinite; }}
    .card-angry .active-dot {{ background:#ff3c3c; }}
    .card-funny .active-dot {{ background:#ffd228; }}
    .card-sad   .active-dot {{ background:#648cff; }}
    @keyframes dp {{ 0%,100%{{transform:scale(1);opacity:1}} 50%{{transform:scale(1.6);opacity:0.4}} }}
    .pcanvas {{ width:100%; height:55px; display:block; position:absolute; top:0; left:0; pointer-events:none; }}
    .face-ring {{ width:54px; height:54px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:24px; margin:10px auto 8px; position:relative; z-index:2; }}
    .card-angry .face-ring {{ background:rgba(255,60,60,0.15);  box-shadow:0 0 0 2px rgba(255,60,60,0.3); }}
    .card-funny .face-ring {{ background:rgba(255,210,40,0.15); box-shadow:0 0 0 2px rgba(255,210,40,0.3); }}
    .card-sad   .face-ring {{ background:rgba(100,140,255,0.15);box-shadow:0 0 0 2px rgba(100,140,255,0.3); }}
    .card-lbl {{ font-family:'Syne',sans-serif; font-weight:800; font-size:14px; display:block; margin-bottom:3px; position:relative; z-index:2; }}
    .card-angry .card-lbl {{ color:#ff7777; }}
    .card-funny .card-lbl {{ color:#ffd228; }}
    .card-sad   .card-lbl {{ color:#8aaeff; }}
    .card-desc {{ font-family:'Space Mono',monospace; font-size:9px; color:#44445a; letter-spacing:0.8px; text-transform:uppercase; line-height:1.5; margin-bottom:8px; display:block; position:relative; z-index:2; }}
    .card-traits {{ display:flex; gap:4px; flex-wrap:wrap; justify-content:center; margin-bottom:10px; position:relative; z-index:2; }}
    .trait {{ font-family:'Space Mono',monospace; font-size:9px; padding:2px 6px; border-radius:999px; }}
    .card-angry .trait {{ background:rgba(255,60,60,0.12);  color:#ff8888; border:1px solid rgba(255,60,60,0.2); }}
    .card-funny .trait {{ background:rgba(255,210,40,0.10); color:#e8b820; border:1px solid rgba(255,210,40,0.2); }}
    .card-sad   .trait {{ background:rgba(100,140,255,0.12);color:#8aaeff; border:1px solid rgba(100,140,255,0.2); }}
    .cta-btn {{ width:100%; padding:7px 0; border-radius:10px; font-family:'Syne',sans-serif; font-weight:700; font-size:12px; border:none; cursor:pointer; position:relative; z-index:2; transition:opacity 0.2s; }}
    .cta-btn:hover {{ opacity:0.82; }}
    .card-angry .cta-btn {{ background:#ff3c3c; color:#fff; }}
    .card-funny .cta-btn {{ background:#e8a800; color:#1a0e00; }}
    .card-sad   .cta-btn {{ background:#648cff; color:#fff; }}
    </style>
    </head>
    <body>
    <div class="grid">{cards_html}</div>
    <script>
    function pickMood(mood) {{
      window.parent.postMessage({{type:'moodSelect', mood:mood}}, '*');
    }}

    const PARTICLE_CFG = {{
      'angry':  {{ color:'255,60,60',   style:'sparks'  }},
      'funny':  {{ color:'255,210,40',  style:'stars'   }},
      'sad':    {{ color:'100,140,255', style:'bubbles' }},
    }};

    function initParticles() {{
      Object.entries(PARTICLE_CFG).forEach(([key, cfg]) => {{
        const cv = document.getElementById('cv-' + key);
        if (!cv) return;
        const W = cv.parentElement.offsetWidth || 180;
        const H = 55;
        cv.width = W; cv.height = H;
        const ctx = cv.getContext('2d');
        const n = cfg.style === 'stars' ? 16 : cfg.style === 'bubbles' ? 10 : 14;
        const pts = Array.from({{length: n}}, () => ({{
          x: Math.random()*W, y: Math.random()*H,
          r: Math.random()*2.5+1.5,
          vx: (Math.random()-0.5)*0.55,
          vy: (Math.random()-0.5)*0.55,
          phase: Math.random()*Math.PI*2
        }}));
        let t = 0;
        (function draw() {{
          ctx.clearRect(0,0,W,H);
          pts.forEach(p => {{
            p.x += p.vx; p.y += p.vy;
            if(p.x<0) p.x=W; if(p.x>W) p.x=0;
            if(p.y<0) p.y=H; if(p.y>H) p.y=0;
            const alpha = (0.18 + 0.16*Math.sin(t*0.03+p.phase)).toFixed(3);
            ctx.beginPath();
            if (cfg.style === 'bubbles') {{
              ctx.arc(p.x, p.y, p.r*1.5, 0, Math.PI*2);
              ctx.strokeStyle = 'rgba('+cfg.color+','+alpha+')';
              ctx.lineWidth = 1;
              ctx.stroke();
            }} else if (cfg.style === 'stars') {{
              let angle = -Math.PI/2;
              ctx.moveTo(p.x+p.r*1.6*Math.cos(angle), p.y+p.r*1.6*Math.sin(angle));
              for(let i=0;i<10;i++) {{
                angle += Math.PI/5;
                const r = i%2===0 ? p.r*0.7 : p.r*1.6;
                ctx.lineTo(p.x+r*Math.cos(angle), p.y+r*Math.sin(angle));
              }}
              ctx.closePath();
              ctx.fillStyle = 'rgba('+cfg.color+','+alpha+')';
              ctx.fill();
            }} else {{
              ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
              ctx.fillStyle = 'rgba('+cfg.color+','+alpha+')';
              ctx.fill();
            }}
          }});
          t++;
          requestAnimationFrame(draw);
        }})();
      }});
    }}

    window.addEventListener('load', () => setTimeout(initParticles, 100));
    </script>
    </body>
    </html>
    """
    return full_html

# Render cards via iframe (so canvas + JS actually work)
components.html(render_cards(st.session_state.mood), height=230, scrolling=False)

# Listen for mood selection via query param workaround
# Since postMessage can't directly hit Python, we use st.query_params
mood_param = st.query_params.get("mood", None)
if mood_param and mood_param in MOODS and mood_param != st.session_state.mood:
    st.session_state.mood = mood_param
    st.session_state.messages = []
    st.session_state.lc_messages = [SystemMessage(content=MOODS[mood_param]["system"])]
    st.rerun()

# Fallback buttons below cards
cols = st.columns(3)
for i, (key, cfg) in enumerate(MOODS.items()):
    with cols[i]:
        if st.button(cfg["cta"], key=f"btn_{key}", use_container_width=True):
            st.session_state.mood = key
            st.session_state.messages = []
            st.session_state.lc_messages = [SystemMessage(content=cfg["system"])]
            st.session_state.last_input = ""
            st.rerun()

# ── Chat area ──────────────────────────────────────────────────────────────
if st.session_state.mood:
    mood = st.session_state.mood
    cfg = MOODS[mood]

    st.markdown(f'<div class="mood-badge {cfg["badge_class"]}">● &nbsp;{cfg["label"]} mode active</div>', unsafe_allow_html=True)

    # Build all messages as one big iframe so HTML renders correctly
    def build_chat_html(messages, cfg):
        msgs_html = ""

        def u_msg(text):
            return f"""
            <div class="msg-row user-row">
              <div class="avatar-wrap">{HUMAN_SVG}</div>
              <div class="msg-col user-col">
                <div class="sender-label" style="color:#9d8fff;">you</div>
                <div class="bubble user-bubble">{text}</div>
              </div>
            </div>"""

        def b_msg(text, bubble_class, color):
            return f"""
            <div class="msg-row bot-row">
              <div class="avatar-wrap">{robot_svg(color)}</div>
              <div class="msg-col bot-col">
                <div class="sender-label">moodbot</div>
                <div class="bubble {bubble_class}">{text}</div>
              </div>
            </div>"""

        if not messages:
            msgs_html += b_msg(cfg["greeting"], cfg["bubble_class"], cfg["robot_color"])

        for msg in messages:
            if msg["role"] == "user":
                msgs_html += u_msg(msg["content"])
            else:
                msgs_html += b_msg(msg["content"], cfg["bubble_class"], cfg["robot_color"])

        return f"""<!DOCTYPE html><html><head>
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@700;800&display=swap');
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:#0e0e1a; font-family:'Syne',sans-serif; padding:12px; border-radius:16px; }}
.msg-row {{ display:flex; align-items:flex-end; gap:10px; margin-bottom:16px; animation:pop 0.3s cubic-bezier(.34,1.56,.64,1) both; }}
.msg-row.user-row {{ flex-direction:row-reverse; }}
.msg-row.bot-row  {{ flex-direction:row; }}
@keyframes pop {{ from{{opacity:0;transform:scale(0.88) translateY(6px)}} to{{opacity:1;transform:scale(1) translateY(0)}} }}
.avatar-wrap {{ width:38px; height:38px; border-radius:50%; flex-shrink:0; overflow:hidden; display:flex; align-items:center; justify-content:center; border:2px solid rgba(255,255,255,0.08); background:transparent; }}
.msg-col {{ display:flex; flex-direction:column; max-width:70%; }}
.msg-col.user-col {{ align-items:flex-end; }}
.msg-col.bot-col  {{ align-items:flex-start; }}
.sender-label {{ font-family:'Space Mono',monospace; font-size:10px; letter-spacing:1px; text-transform:uppercase; margin-bottom:4px; opacity:0.4; color:#aaa; }}
.bubble {{ padding:10px 14px; font-size:13px; line-height:1.6; word-break:break-word; font-family:'Syne',sans-serif; color:#e0e0f0; }}
.user-bubble {{ border-radius:18px 18px 4px 18px; background:rgba(124,106,247,0.15); border:1px solid rgba(124,106,247,0.3); color:#d8d0ff; }}
.msg-row.bot-row .bubble {{ border-radius:18px 18px 18px 4px; }}
.bubble-angry {{ background:rgba(255,60,60,0.12);  border:1px solid rgba(255,60,60,0.25);  color:#ffb3b3; }}
.bubble-funny {{ background:rgba(255,210,40,0.10); border:1px solid rgba(255,210,40,0.25); color:#fff0a0; }}
.bubble-sad   {{ background:rgba(100,140,255,0.12);border:1px solid rgba(100,140,255,0.25);color:#b3c6ff; }}
</style>
</head><body>
{msgs_html}
<script>window.scrollTo(0, document.body.scrollHeight);</script>
</body></html>"""

    # Calculate dynamic height
    num_messages = max(1, len(st.session_state.messages))
    chat_height = min(500, max(180, num_messages * 90 + 100))

    components.html(
        build_chat_html(st.session_state.messages, cfg),
        height=chat_height,
        scrolling=True
    )

    # ── Input row ──────────────────────────────────────────────────────────
    col_in, col_btn = st.columns([5, 1])
    with col_in:
        user_input = st.text_input(
            "Message",
            placeholder="Type your message…",
            label_visibility="collapsed",
            key=f"input_field_{st.session_state.input_key}"
        )
    with col_btn:
        send = st.button("Send ↗", use_container_width=True, type="primary")

    if st.button("🗑 Clear chat"):
        st.session_state.messages = []
        st.session_state.lc_messages = [SystemMessage(content=cfg["system"])]
        st.session_state.last_input = ""
        st.rerun()

    # ── Handle send ────────────────────────────────────────────────────────
    triggered = send and user_input.strip()
    if triggered and user_input.strip() != st.session_state.last_input:
        st.session_state.last_input = user_input.strip()
        st.session_state.input_key += 1
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        st.session_state.lc_messages.append(HumanMessage(content=user_input.strip()))

        with st.spinner("MoodBot is thinking..."):
            try:
                llm = ChatMistralAI(model="mistral-small-2506", temperature=0.9)
                response = llm.invoke(st.session_state.lc_messages)
                bot_reply = response.content
                st.session_state.lc_messages.append(AIMessage(content=bot_reply))
                st.session_state.messages.append({"role": "bot", "content": bot_reply})
            except Exception as e:
                st.session_state.messages.append({"role": "bot", "content": f"⚠️ Error: {str(e)}"})
        st.rerun()

else:
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem;color:#252535;
         font-family:'Space Mono',monospace;font-size:0.8rem;letter-spacing:1px;">
      ↑ &nbsp; PICK A MOOD TO BEGIN
    </div>
    """, unsafe_allow_html=True)