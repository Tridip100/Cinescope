import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from typing import List, Optional

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CineScope — AI Movie Intelligence",
    page_icon="🎬",
    layout="wide"
)

# ── Pydantic model ───────────────────────────────────────────────────────────
class MovieInfo(BaseModel):
    title: str
    release_year: Optional[int] = None
    genre: Optional[List[str]] = None
    director: Optional[str] = None
    main_cast: Optional[List[str]] = None
    setting_location: Optional[str] = None
    plot: Optional[str] = None
    themes: Optional[List[str]] = None
    ratings: Optional[float] = None
    notable_features: Optional[str] = None
    short_summary: Optional[str] = None

# ── LangChain setup ──────────────────────────────────────────────────────────
model  = ChatMistralAI(model="mistral-small-2506", temperature=0.9)
parser = PydanticOutputParser(pydantic_object=MovieInfo)

prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a professional Movie Information Extraction Assistant.
Extract useful structured information from a movie paragraph.

Rules:
- Do NOT add explanations or commentary
- If information is missing, omit it or use null
- Keep summary short (2-3 lines)
- Do NOT guess unknown facts
- Return ONLY valid JSON matching the schema

{format_instructions}
"""),
    ("human", "Extract information from the following movie description:\n{paragraph}")
])

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: #04040e;
    color: #e8e4dc;
}

.stApp {
    background: #04040e;
    min-height: 100vh;
    position: relative;
}

/* ── LAYER 1: animated radial mesh ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 130% 90% at 5%  0%,   rgba(150,40,255,0.22)  0%, transparent 48%),
        radial-gradient(ellipse 90%  70% at 95% 5%,   rgba(212,175,55,0.16)  0%, transparent 44%),
        radial-gradient(ellipse 70%  80% at 50% 105%,  rgba(20,110,255,0.14)  0%, transparent 52%),
        radial-gradient(ellipse 50%  50% at 80% 55%,  rgba(255,50,110,0.10)  0%, transparent 42%),
        radial-gradient(ellipse 60%  40% at 20% 70%,  rgba(0,200,180,0.07)   0%, transparent 45%),
        #04040e;
    pointer-events: none;
    z-index: 0;
    animation: meshDrift 22s ease-in-out infinite alternate;
}

@keyframes meshDrift {
    0%   { filter: hue-rotate(0deg)   brightness(1.00) saturate(1.0); }
    25%  { filter: hue-rotate(18deg)  brightness(1.06) saturate(1.1); }
    50%  { filter: hue-rotate(-8deg)  brightness(0.97) saturate(0.95); }
    75%  { filter: hue-rotate(25deg)  brightness(1.04) saturate(1.05); }
    100% { filter: hue-rotate(-15deg) brightness(1.02) saturate(1.08); }
}

/* ── LAYER 2: giant purple orb top-left ── */
.stApp::after {
    content: '';
    position: fixed;
    width: 700px; height: 700px;
    border-radius: 50%;
    background: radial-gradient(circle,
        rgba(140,40,255,0.16) 0%,
        rgba(100,20,200,0.08) 40%,
        transparent 70%);
    top: -280px; left: -220px;
    pointer-events: none;
    z-index: 0;
    animation: orb1 24s ease-in-out infinite;
}

@keyframes orb1 {
    0%,100% { transform: translate(0px,   0px)  scale(1.0); }
    30%     { transform: translate(90px,  70px) scale(1.12); }
    60%     { transform: translate(-30px, 110px) scale(0.94); }
}

/* ── LAYER 3: gold orb bottom-right ── */
.orb-gold {
    position: fixed;
    width: 580px; height: 580px;
    border-radius: 50%;
    background: radial-gradient(circle,
        rgba(212,175,55,0.14) 0%,
        rgba(180,140,30,0.07) 45%,
        transparent 70%);
    bottom: -220px; right: -130px;
    pointer-events: none; z-index: 0;
    animation: orb2 28s ease-in-out infinite;
}
@keyframes orb2 {
    0%,100% { transform: translate(0,   0)  scale(1.0); }
    40%     { transform: translate(-80px, -60px) scale(1.18); }
    70%     { transform: translate(55px, -90px)  scale(0.88); }
}

/* ── LAYER 4: cyan orb mid ── */
.orb-cyan {
    position: fixed;
    width: 450px; height: 450px;
    border-radius: 50%;
    background: radial-gradient(circle,
        rgba(0,210,200,0.09) 0%,
        transparent 65%);
    top: 35%; left: 50%;
    pointer-events: none; z-index: 0;
    animation: orb3 35s ease-in-out infinite;
}
@keyframes orb3 {
    0%,100% { transform: translate(0, 0)     scale(1.0); }
    50%     { transform: translate(-70px, 90px) scale(1.25); }
}

/* ── LAYER 5: pink orb top-right ── */
.orb-pink {
    position: fixed;
    width: 350px; height: 350px;
    border-radius: 50%;
    background: radial-gradient(circle,
        rgba(255,50,130,0.10) 0%,
        transparent 68%);
    top: 18%; right: 4%;
    pointer-events: none; z-index: 0;
    animation: orb4 19s ease-in-out infinite reverse;
}
@keyframes orb4 {
    0%,100% { transform: translate(0, 0)   scale(1.0); }
    50%     { transform: translate(-45px, 65px) scale(1.12); }
}

/* ── LAYER 6: twinkling star field ── */
.bg-stars {
    position: fixed; inset: 0;
    pointer-events: none; z-index: 0;
    background-image:
        radial-gradient(1.2px 1.2px at  8% 12%, rgba(255,255,255,0.7)  0%, transparent 100%),
        radial-gradient(1px   1px   at 22% 38%, rgba(212,175,55,0.8)   0%, transparent 100%),
        radial-gradient(0.8px 0.8px at 38%  6%, rgba(255,255,255,0.55) 0%, transparent 100%),
        radial-gradient(1.2px 1.2px at 58% 22%, rgba(160,60,255,0.65)  0%, transparent 100%),
        radial-gradient(1px   1px   at 73% 52%, rgba(255,255,255,0.60) 0%, transparent 100%),
        radial-gradient(1px   1px   at 83% 10%, rgba(212,175,55,0.65)  0%, transparent 100%),
        radial-gradient(0.8px 0.8px at 91% 68%, rgba(255,255,255,0.50) 0%, transparent 100%),
        radial-gradient(1px   1px   at 13% 72%, rgba(0,200,255,0.65)   0%, transparent 100%),
        radial-gradient(1px   1px   at 48% 82%, rgba(255,60,150,0.55)  0%, transparent 100%),
        radial-gradient(0.8px 0.8px at 33% 58%, rgba(255,255,255,0.45) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 68% 88%, rgba(212,175,55,0.55)  0%, transparent 100%),
        radial-gradient(1px   1px   at  4% 48%, rgba(255,255,255,0.45) 0%, transparent 100%),
        radial-gradient(1px   1px   at 55% 45%, rgba(0,200,180,0.50)   0%, transparent 100%),
        radial-gradient(0.8px 0.8px at 77% 30%, rgba(255,255,255,0.40) 0%, transparent 100%),
        radial-gradient(1.2px 1.2px at 29% 90%, rgba(160,60,255,0.50)  0%, transparent 100%);
    animation: twinkle 5s ease-in-out infinite alternate;
}
@keyframes twinkle {
    from { opacity: 0.45; }
    to   { opacity: 1.0; }
}

/* ── LAYER 7: animated grid ── */
.grid-lines {
    position: fixed; inset: 0;
    background-image:
        linear-gradient(rgba(212,175,55,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(212,175,55,0.025) 1px, transparent 1px);
    background-size: 72px 72px;
    pointer-events: none; z-index: 0;
    animation: gridBreath 9s ease-in-out infinite alternate;
}
@keyframes gridBreath {
    from { opacity: 0.35; transform: scale(1.0); }
    to   { opacity: 1.0;  transform: scale(1.005); }
}

/* ── LAYER 8: moving light streak ── */
.light-streak {
    position: fixed;
    top: 0; left: -40%; right: 0;
    height: 1px;
    width: 140%;
    background: linear-gradient(90deg,
        transparent 0%,
        rgba(212,175,55,0.0) 30%,
        rgba(212,175,55,0.45) 50%,
        rgba(160,60,255,0.30) 65%,
        rgba(0,200,200,0.15) 75%,
        transparent 100%);
    pointer-events: none; z-index: 1;
    animation: streakSweep 12s linear infinite;
    opacity: 0;
    transform: rotate(-3deg);
}
@keyframes streakSweep {
    0%   { top: -5%;  opacity: 0; }
    4%   { opacity: 0.8; }
    96%  { opacity: 0.35; }
    100% { top: 108%; opacity: 0; }
}

/* ── LAYER 9: second streak offset ── */
.light-streak-2 {
    position: fixed;
    top: 0; left: -40%; right: 0;
    height: 1px; width: 140%;
    background: linear-gradient(90deg,
        transparent,
        rgba(0,200,200,0.3) 45%,
        rgba(160,60,255,0.2) 60%,
        transparent);
    pointer-events: none; z-index: 1;
    animation: streakSweep 12s 6s linear infinite;
    opacity: 0;
    transform: rotate(-3deg);
}

/* ── LAYER 10: grain ── */
.grain {
    position: fixed; inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none; z-index: 2; opacity: 0.55;
}

/* ── HEADER ── */
.cinescope-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 2rem 0 1.5rem;
    border-bottom: 1px solid rgba(212,175,55,0.15);
    margin-bottom: 2.5rem;
    position: relative; z-index: 10;
}
.brand-name {
    font-family: 'Playfair Display', serif;
    font-weight: 900;
    font-size: 2.6rem;
    letter-spacing: -1px;
    line-height: 1;
    color: #f5f0e8;
}
.brand-name span { color: #d4af37; }
.brand-tagline {
    font-size: 11px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #5a5650;
    margin-top: 4px;
    font-weight: 300;
}
.brand-badge {
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 6px 14px;
    border: 1px solid rgba(212,175,55,0.3);
    color: #d4af37;
    border-radius: 2px;
    font-weight: 500;
}

/* ── INPUT BOX ── */
.input-label {
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #d4af37;
    font-weight: 500;
    margin-bottom: 0.5rem;
    display: block;
    position: relative; z-index: 10;
}

/* ── FILMSTRIP ── */
.filmstrip {
    display: flex; gap: 3px;
    margin-bottom: 2.5rem; opacity: 0.2;
    position: relative; z-index: 10;
}
.filmstrip-hole {
    width: 10px; height: 8px;
    border-radius: 1px;
    background: #d4af37;
}

/* ── Streamlit overrides ── */
div[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(212,175,55,0.2) !important;
    border-radius: 3px !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 300 !important;
    line-height: 1.7 !important;
    caret-color: #d4af37;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(212,175,55,0.5) !important;
    box-shadow: 0 0 0 3px rgba(212,175,55,0.06) !important;
}
div[data-testid="stTextArea"] label { display: none !important; }

.stButton > button {
    background: #d4af37 !important;
    color: #04040e !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 11px !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 2px !important;
    padding: 0.75rem 2.5rem !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #e8c84a !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 28px rgba(212,175,55,0.25) !important;
}

/* metric cards */
div[data-testid="stMetric"] {
    background: rgba(212,175,55,0.04) !important;
    border: 1px solid rgba(212,175,55,0.10) !important;
    border-radius: 4px !important;
    padding: 0.8rem 1rem !important;
}
div[data-testid="stMetricLabel"] {
    color: #d4af37 !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}
div[data-testid="stMetricValue"] {
    color: #f0ece4 !important;
    font-size: 16px !important;
    font-weight: 400 !important;
}

div[data-testid="stInfo"] {
    background: rgba(212,175,55,0.06) !important;
    border: 1px solid rgba(212,175,55,0.18) !important;
    border-left: 3px solid #d4af37 !important;
    color: #c8c0b0 !important;
    border-radius: 0 4px 4px 0 !important;
    font-style: italic !important;
    font-family: 'Playfair Display', serif !important;
}

footer { display: none; }
#MainMenu { display: none; }
header { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("movie", None), ("input_key", 0)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Background layers + Header ────────────────────────────────────────────────
st.markdown("""
<div class="bg-stars"></div>
<div class="grid-lines"></div>
<div class="orb-gold"></div>
<div class="orb-cyan"></div>
<div class="orb-pink"></div>
<div class="light-streak"></div>
<div class="light-streak-2"></div>
<div class="grain"></div>

<div class="cinescope-header">
  <div class="brand-block">
    <div class="brand-name">Cine<span>Scope</span></div>
    <div class="brand-tagline">AI Movie Intelligence Platform</div>
  </div>
  <div class="brand-badge">✦ Powered by Mistral AI</div>
</div>

<div class="filmstrip">
  <div class="filmstrip-hole"></div><div class="filmstrip-hole"></div>
  <div class="filmstrip-hole"></div><div class="filmstrip-hole"></div>
  <div class="filmstrip-hole"></div><div class="filmstrip-hole"></div>
  <div class="filmstrip-hole"></div><div class="filmstrip-hole"></div>
  <div class="filmstrip-hole"></div><div class="filmstrip-hole"></div>
  <div class="filmstrip-hole"></div><div class="filmstrip-hole"></div>
  <div class="filmstrip-hole"></div><div class="filmstrip-hole"></div>
</div>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1.6], gap="large")

with col_left:
    st.markdown('<span class="input-label">Movie Description</span>', unsafe_allow_html=True)
    paragraph = st.text_area(
        "desc",
        placeholder="Paste or type a movie description, synopsis, or any paragraph about a film...\n\nExample: The Dark Knight is a 2008 superhero film directed by Christopher Nolan...",
        height=300,
        key=f"movie_input_{st.session_state.input_key}",
        label_visibility="collapsed"
    )
    analyze_btn = st.button("⬡  Analyze Film", use_container_width=True)

    if analyze_btn and paragraph.strip():
        with st.spinner("Extracting intelligence..."):
            try:
                fmt = parser.get_format_instructions()
                final_prompt = prompt.invoke({
                    "paragraph": paragraph.strip(),
                    "format_instructions": fmt
                })
                response = model.invoke(final_prompt)
                # Parse into Pydantic model
                movie: MovieInfo = parser.parse(response.content)
                st.session_state.movie = movie
                st.session_state.input_key += 1
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")
    elif analyze_btn:
        st.warning("Please enter a movie description first.")

# ── Results ───────────────────────────────────────────────────────────────────
def fmt_list(lst):
    if not lst:
        return "—"
    return ", ".join(lst)

def fmt_val(v):
    if v is None:
        return "—"
    return str(v)

with col_right:
    movie: MovieInfo = st.session_state.movie

    if movie:
        # Title + meta
        genre_str = fmt_list(movie.genre)
        meta_parts = [p for p in [fmt_val(movie.release_year), genre_str] if p != "—"]
        st.markdown(f"### {movie.title}")
        st.caption("  ·  ".join(meta_parts))
        st.divider()

        # Summary
        if movie.short_summary:
            st.info(f'*"{movie.short_summary}"*')

        # Row 1 — metrics
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("🎬 Director", fmt_val(movie.director))
        with c2:
            st.metric("📅 Year", fmt_val(movie.release_year))
        with c3:
            st.metric("⭐ Ratings", fmt_val(movie.ratings) if movie.ratings else "—")

        st.divider()

        # Row 2
        c4, c5, c6 = st.columns(3)
        with c4:
            st.markdown("**🎭 Genre**")
            st.write(fmt_list(movie.genre))
        with c5:
            st.markdown("**📍 Setting**")
            st.write(fmt_val(movie.setting_location))
        with c6:
            st.markdown("**💡 Themes**")
            st.write(fmt_list(movie.themes))

        st.divider()

        # Wide fields
        st.markdown("**👥 Main Cast**")
        st.write(fmt_list(movie.main_cast))

        st.markdown("**📖 Plot**")
        st.write(fmt_val(movie.plot))

        st.markdown("**✨ Notable Features**")
        st.write(fmt_val(movie.notable_features))

        st.divider()

        with st.expander("View structured JSON"):
            st.json(movie.model_dump())

    else:
        st.markdown("""
        <div style='text-align:center; padding:5rem 2rem;'>
          <div style='font-size:3rem; opacity:0.12; margin-bottom:1rem;'>🎬</div>
          <div style='font-style:italic; color:#444; font-size:1rem;'>Your film intelligence will appear here</div>
        </div>
        """, unsafe_allow_html=True)