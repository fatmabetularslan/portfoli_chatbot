import streamlit as st
import base64
import json
from common_css import LIGHT_CSS, DARK_CSS
from pathlib import Path
import streamlit.components.v1 as components
from rag_system import load_cv_index
from tools.tool_definitions import ToolDefinitions
import modern_chatbot

st.set_page_config(page_title="Fatma Betül Arslan", page_icon="🤖", layout="centered")

PDF_PATH = "assets/Fatma-Betül-ARSLAN-cv.pdf"
PROFILE_IMG_PATH = Path("assets/vesika.jpg")


@st.cache_resource(show_spinner=False)
def _init_chat_resources():
    rag = load_cv_index("betül-cv.json")
    tool_def = ToolDefinitions()
    try:
        tool_def.initialize_job_analyzer(None, rag.cv_json, rag)
    except Exception as exc:
        st.warning(f"Job analyzer başlatılamadı: {exc}")
    return rag, tool_def


# --- State ---
if "lang" not in st.session_state:
    st.session_state["lang"] = "tr"
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False
if "page" not in st.session_state:
    st.session_state["page"] = "home"

current_lang = st.session_state["lang"]

# Eğer ?embedded_chat=1 ile gelindiyse sadece chatbot'u render et
qp_for_embed = st.query_params
if qp_for_embed.get("embedded_chat") == "1":
    # Üstteki Streamlit toolbar/header'ı ve ekstra boşlukları gizle
    st.markdown(
        """
        <style>
        header[data-testid="stHeader"],
        [data-testid="stToolbar"],
        .stAppDeployButton {
            display: none !important;
        }
        .stMainBlockContainer, .main .block-container {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
        body {
            padding-top: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    rag, tool_def = _init_chat_resources()
    modern_chatbot.run(tool_def=tool_def, rag=rag, cv_json=rag.cv_json)
    st.stop()

# --- Global CSS: tema + header gizleme ---
st.markdown("""
    <style>
/* Streamlit header'ını gizle */
header[data-testid="stHeader"],
.stApp > header,
header {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}

.main .block-container {
    padding-top: 0 !important;
    max-width: 1200px;
}

body {
    /* Sayfanın en üstü ile profil görseli arasındaki boşluğu azalt */
    padding-top: 40px !important;
}

.main {
    padding-top: 0 !important;
}

.stApp > div:first-child {
    padding-top: 0 !important;
}
    </style>
    """, unsafe_allow_html=True)

# Tema CSS
st.markdown(
    f"<style>{DARK_CSS if st.session_state.dark_mode else LIGHT_CSS}</style>",
    unsafe_allow_html=True
)

# --- Navigation Bar (chat linki yok) ---
st.markdown("""
<style>
.nav-menu {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    width: 100% !important;
    background: rgba(255, 255, 255, 0.98) !important;
    backdrop-filter: blur(10px) !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08) !important;
    z-index: 9999 !important;
    padding: 16px 0 !important;
    border-bottom: 1px solid #e2e8f0 !important;
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
}

.nav-menu-content {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    padding: 0 40px;
    flex-wrap: wrap;
}

.nav-menu-links {
    display: flex;
    align-items: center;
    gap: 24px;
    flex-wrap: wrap;
}

.nav-menu-toggles {
    display: flex;
    align-items: center;
    gap: 12px;
}

.nav-link {
    color: #1e293b;
    text-decoration: none;
    font-weight: 500;
    font-size: 0.98em;
    transition: color 0.2s, background 0.2s;
    padding: 8px 14px;
    border-radius: 6px;
    cursor: pointer;
    white-space: nowrap;
}

.nav-link:hover {
    color: #667eea;
    background: rgba(102, 126, 234, 0.1);
}

.nav-toggle-btn {
    width: 40px;
    height: 40px;
    font-size: 1.2em;
    border-radius: 20px;
    border: 1px solid #e2e8f0;
    background: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    color: #475569;
    margin: 0;
    padding: 0;
}
.nav-toggle-btn:hover {
    background: #f1f5f9;
    border-color: #cbd5e1;
    transform: scale(1.05);
}
.nav-toggle-btn.selected {
    background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
    border-color: #2563eb;
    color: #ffffff;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
}

.stApp[data-theme="dark"] .nav-menu {
    background: rgba(30, 41, 59, 0.95) !important;
    border-bottom-color: #475569 !important;
}
.stApp[data-theme="dark"] .nav-link {
    color: #cbd5e1 !important;
}
.stApp[data-theme="dark"] .nav-link:hover {
    color: #a5b4fc !important;
    background: rgba(102, 126, 234, 0.2) !important;
}
.stApp[data-theme="dark"] .nav-toggle-btn {
    background: #1e293b;
    border-color: #475569;
    color: #cbd5e1;
}
.stApp[data-theme="dark"] .nav-toggle-btn:hover {
    background: #334155;
    border-color: #64748b;
}
.stApp[data-theme="dark"] .nav-toggle-btn.selected {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    border-color: #3b82f6;
    color: #ffffff;
}

/* scroll davranışı */
body {
    padding-top: 40px !important;
    scroll-behavior: smooth;
}
.main { padding-top: 40px !important; }
.stApp > div:first-child { padding-top: 0 !important; }
.portfolio-section { scroll-margin-top: 60px; }

@media (max-width: 768px) {
    .nav-menu-content {
        gap: 15px;
        padding: 0 10px;
    }
    .nav-link {
        font-size: 0.85em;
        padding: 4px 8px;
    }
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                const offset = 70;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - offset;
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
});
</script>
""", unsafe_allow_html=True)
nav_texts = {
    "tr": {
        "home": "Ana Sayfa",
        "about": "Hakkımda",
        "experience": "Deneyim",
        "projects": "Projeler",
        "skills": "Yetenekler",
        "awards": "Ödüller",
        "articles": "Yazılar",
        "references": "Referanslar",
        "contact": "İletişim",
    },
    "en": {
        "home": "Home",
        "about": "About",
        "experience": "Experience",
        "projects": "Projects",
        "skills": "Skills",
        "awards": "Awards",
        "articles": "Articles",
        "references": "References",
        "contact": "Contact",
    }
}[current_lang]

lang = st.session_state["lang"]
dark = st.session_state["dark_mode"]
en_selected = "selected" if lang == "en" else ""
tr_selected = "selected" if lang == "tr" else ""
light_selected = "selected" if not dark else ""
dark_selected = "selected" if dark else ""

st.markdown(f"""
<div class="nav-menu">
  <div class="nav-menu-content">
    <div class="nav-menu-links">
      <a href="#" class="nav-link" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}}); return false;">{nav_texts['home']}</a>
      <a href="#about" class="nav-link">{nav_texts['about']}</a>
      <a href="#experience" class="nav-link">{nav_texts['experience']}</a>
      <a href="#projects" class="nav-link">{nav_texts['projects']}</a>
      <a href="#skills" class="nav-link">{nav_texts['skills']}</a>
      <a href="#awards" class="nav-link">{nav_texts['awards']}</a>
      <a href="#articles" class="nav-link">{nav_texts['articles']}</a>
      <a href="#references" class="nav-link">{nav_texts['references']}</a>
      <a href="#contact" class="nav-link">{nav_texts['contact']}</a>
    </div>
    <div class="nav-menu-toggles">
      <form method="GET" style="display:flex;gap:6px;align-items:center;margin:0;">
        <button class="nav-toggle-btn {en_selected}" name="setlang" value="en" type="submit" title="English">EN</button>
        <button class="nav-toggle-btn {tr_selected}" name="setlang" value="tr" type="submit" title="Türkçe">🇹🇷</button>
        <button class="nav-toggle-btn {light_selected}" name="settheme" value="light" type="submit" title="Light Mode">☀️</button>
        <button class="nav-toggle-btn {dark_selected}" name="settheme" value="dark" type="submit" title="Dark Mode">🌙</button>
      </form>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# query params -> state
qp = st.query_params
rerun_needed = False
if qp.get("setlang"):
    st.session_state["lang"] = qp["setlang"]
    rerun_needed = True
if qp.get("settheme"):
    st.session_state["dark_mode"] = qp["settheme"] == "dark"
    rerun_needed = True
if rerun_needed:
    qp.clear()
    st.rerun()

# --- Arka plan şekilleri ---
st.markdown("""
<style>
.background-shapes {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: -1;
    overflow: hidden;
}
.blob-1 {
    position: absolute;
    top: -10%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: linear-gradient(135deg, #3b5bdb 0%, #5b21b6 100%);
    border-radius: 50%;
    filter: blur(60px);
    opacity: 0.15;
    animation: float 6s ease-in-out infinite;
}
.blob-2 {
    position: absolute;
    bottom: -15%;
    left: -15%;
    width: 350px;
    height: 350px;
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    border-radius: 50%;
    filter: blur(50px);
    opacity: 0.12;
    animation: float 8s ease-in-out infinite reverse;
}
.wave-shape {
    position: absolute;
    top: 20%;
    right: 5%;
    width: 200px;
    height: 200px;
    background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
    border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
    filter: blur(40px);
    opacity: 0.1;
    animation: morph 10s ease-in-out infinite;
}
.bottom-wave {
    position: absolute;
    bottom: -5%;
    left: 0;
    width: 100%;
    height: 300px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    opacity: 0.08;
    clip-path: polygon(0 100%, 100% 100%, 100% 60%, 80% 40%, 60% 60%, 40% 40%, 20% 60%, 0 40%);
    animation: wave-float 12s ease-in-out infinite;
}
.bottom-blob {
    position: absolute;
    bottom: -10%;
    right: -5%;
    width: 500px;
    height: 500px;
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #4facfe 100%);
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.06;
    animation: blob-float 15s ease-in-out infinite;
}
@keyframes wave-float {
    0%, 100% { transform: translateY(0px) scale(1); }
    50% { transform: translateY(-15px) scale(1.02); }
}
@keyframes blob-float {
    0%, 100% { transform: translateY(0px) rotate(0deg) scale(1); }
    33% { transform: translateY(-10px) rotate(120deg) scale(1.05); }
    66% { transform: translateY(-5px) rotate(240deg) scale(0.95); }
}
@keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-20px) rotate(180deg); }
}
@keyframes morph {
    0%, 100% { border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%; }
    25% { border-radius: 58% 42% 75% 25% / 76% 46% 54% 24%; }
    50% { border-radius: 50% 50% 33% 67% / 55% 27% 73% 45%; }
    75% { border-radius: 33% 67% 58% 42% / 63% 68% 32% 37%; }
}
.main-content { position: relative; z-index: 1; }
</style>
<div class="background-shapes">
    <div class="blob-1"></div>
    <div class="blob-2"></div>
    <div class="wave-shape"></div>
    <div class="bottom-wave"></div>
    <div class="bottom-blob"></div>
</div>
""", unsafe_allow_html=True)

# --- Main content wrapper ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# === HERO SECTION ===
# === HERO SECTION ===
tag = "betül-cv.json"
cv_data = json.load(open(tag, encoding="utf-8"))

name = cv_data.get("name", "Fatma Betül Arslan")
title = cv_data.get("title", "Veri Bilimci")
location = cv_data.get("location", "İstanbul, Türkiye")

st.markdown("""
<style>
.hero-section {
    text-align: center;
    padding: 48px 28px 36px 28px;
    max-width: 700px;
    margin: 0 auto 32px auto;
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 32px;
    box-shadow: 0 25px 60px rgba(15, 23, 42, 0.08);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}

/* İsim */
.hero-name {
    font-size: 2.45em;
    font-weight: 700;
    color: #0f172a;
    margin: 16px 0 4px 0;
    line-height: 1.18;
}

/* Meslek */
.hero-title {
    font-size: 1.5em;
    font-weight: 400;
    color: #475569;
    margin: 0 0 6px 0;      /* Veri Bilimci -> buton arası = 6px */
    line-height: 1.4;
}

/* Profil fotoğrafı */
.hero-profile-img {
    width: 280px;
    height: 280px;
    border-radius: 50%;
    object-fit: cover;
    margin: 0 auto 20px auto;
    display: block;
    border: 4px solid #e2e8f0;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}
.hero-profile-img:hover { transform: scale(1.05); }

/* Download CV butonu */
.download-cv-btn {
    text-decoration: none !important;
    background: #ffffff !important;
    color: #4338ca !important;
    border: 2px solid #4338ca !important;
    padding: 10px 28px !important;
    border-radius: 999px !important;
    font-weight: 600 !important;
    font-size: 0.96em !important;
    cursor: pointer !important;
    transition: box-shadow 0.2s ease, transform 0.2s ease !important;
    box-shadow: 0 12px 24px rgba(67, 56, 202, 0.12) !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
}

/* hover efekti */
.download-cv-btn:hover {
    background: #4338ca !important;
    color: #ffffff !important;
    box-shadow: 0 16px 28px rgba(67, 56, 202, 0.22) !important;
    transform: translateY(-2px) !important;
}

/* Sosyal ikonlar: buton ile arası 6px */
.social-links {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-top: 10px;
}
.social-links a {
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 42px;
    height: 42px;
    border-radius: 14px;
    background: #ffffff;
    color: #4b5563;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
.social-links a:hover {
    border-color: #4338ca;
    box-shadow: 0 8px 18px rgba(67, 56, 202, 0.18);
    transform: translateY(-2px);
}
.social-links img {
    width: 20px;
    height: 20px;
    filter: grayscale(0.1);
}

/* Dark mode uyumu */
.stApp[data-theme="dark"] .hero-name { color: #e5e7eb !important; }
.stApp[data-theme="dark"] .hero-title { color: #cbd5e1 !important; }
.stApp[data-theme="dark"] .hero-profile-img {
    border-color: #8b5cf6;
    box-shadow: 0 8px 24px rgba(139, 92, 246, 0.4);
}
.stApp[data-theme="dark"] .social-links a {
    background: #1f2937;
    color: #e5e7eb;
}
.stApp[data-theme="dark"] .social-links a:hover {
    background: #111827;
}

/* responsive */
@media (max-width: 768px) {
    .hero-section { text-align: center; }
}
</style>
""", unsafe_allow_html=True)

# Profil resmi
if PROFILE_IMG_PATH.exists():
    profile_bytes = PROFILE_IMG_PATH.read_bytes()
    profile_b64 = base64.b64encode(profile_bytes).decode("utf-8")
    profile_img_html = f'<img src="data:image/jpeg;base64,{profile_b64}" alt="{name}" class="hero-profile-img" />'
else:
    profile_img_html = (
        f'<div class="hero-profile-img" '
        f'style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
        f'display:flex;align-items:center;justify-content:center;'
        f'color:white;font-size:3rem;font-weight:700;">{name[0]}</div>'
    )

# CV'yi base64'e çevir
try:
    with open(PDF_PATH, "rb") as f:
        pdf_b64 = base64.b64encode(f.read()).decode("utf-8")

    hero_html = f"""
    <div class="hero-section">
        {profile_img_html}
        <h1 class="hero-name">{name}</h1>
        <h2 class="hero-title">{title}</h2>
        <a href="data:application/pdf;base64,{pdf_b64}"
           download="Fatma_Betul_Arslan_CV.pdf"
           class="download-cv-btn">
            📥 Download CV
        </a>
        <div class="social-links">
          <a href="https://github.com/fatmabetularslan" target="_blank">
            <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg" alt="GitHub">
          </a>
          <a href="https://www.linkedin.com/in/fatma-betül-arslan" target="_blank">
            <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linkedin/linkedin-original.svg" alt="LinkedIn">
          </a>
          <a href="mailto:betularsln01@gmail.com" target="_blank">
            <img src="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/gmail.svg" alt="Mail">
          </a>
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)
except FileNotFoundError:
    st.error(f"CV dosyası bulunamadı: {PDF_PATH}")


# === PORTFÖY BÖLÜMLERİ ===
st.markdown("""
<style>
.portfolio-section {
    margin: 60px 0;
    padding: 40px 20px;
    max-width: 1000px;
    margin-left: auto;
    margin-right: auto;
}
.section-title {
    font-size: 2em;
    font-weight: 700;
    margin-bottom: 30px;
    text-align: center;
    color: #1e293b;
  position: relative;
    padding-bottom: 15px;
}
.section-title::after {
  content: '';
  position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 60px;
    height: 3px;
    background: linear-gradient(90deg, #3b5bdb 0%, #5b21b6 100%);
    border-radius: 2px;
}
.about-content {
    font-size: 1.15em;
    line-height: 1.8;
    color: #475569;
    text-align: center;
    max-width: 800px;
    margin: 0 auto;
}
.experience-card, .education-card, .project-card, .award-card, .reference-card {
    background: #fff;
    border-radius: 12px;
    padding: 24px;
    margin: 0 auto 20px auto;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    transition: transform 0.2s, box-shadow 0.2s;
    border-left: 4px solid #3b5bdb;
    max-width: 780px;
}
.reference-list {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
}
.reference-list .reference-card {
    max-width: 620px;
    width: 100%;
}
.experience-card:hover, .education-card:hover, .project-card:hover, .award-card:hover, .reference-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15);
}
.experience-title, .education-title {
    font-size: 1.4em;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 8px;
}
.experience-company, .education-institution {
    font-size: 1.2em;
    color: #3b5bdb;
    font-weight: 500;
    margin-bottom: 8px;
}
.experience-duration, .education-years {
    font-size: 1em;
    color: #64748b;
    margin-bottom: 12px;
}
.experience-description, .education-degree {
    color: #475569;
    line-height: 1.7;
    font-size: 1.05em;
}
.skills-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-top: 30px;
}
.skill-category {
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.skill-category-title {
    font-size: 1.3em;
    font-weight: 600;
    color: #3b5bdb;
    margin-bottom: 12px;
}
.skill-tag {
    display: inline-block;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    color: #475569;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 1em;
    margin: 4px 4px 4px 0;
    border: 1px solid #e2e8f0;
}
.project-card { border-left-color: #764ba2; }
.project-name {
    font-size: 1.4em;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 12px;
}
.project-tech {
    color: #3b5bdb;
    font-size: 1.05em;
    margin-bottom: 12px;
    font-weight: 500;
}
.project-description {
    color: #475569;
    line-height: 1.7;
    margin-bottom: 12px;
    font-size: 1.05em;
}
.project-features {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #e2e8f0;
}
.project-feature {
    color: #64748b;
    font-size: 1em;
    margin: 4px 0;
}
.project-feature::before {
    content: '• ';
    color: #3b5bdb;
    font-weight: bold;
}
.project-link {
    display: inline-block;
    margin-top: 12px;
    color: #3b5bdb;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s;
}
.project-link:hover { color: #764ba2; }
.award-name {
    font-size: 1.35em;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 6px;
}
.award-org {
    color: #3b5bdb;
    font-weight: 500;
    margin-bottom: 8px;
}
.award-description {
    color: #475569;
    line-height: 1.7;
    font-size: 1.05em;
}
.reference-name {
    font-size: 1.35em;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 6px;
}
.reference-title {
    color: #3b5bdb;
    font-weight: 500;
    margin-bottom: 4px;
}
.reference-org {
    color: #64748b;
    font-size: 1em;
}

.stApp[data-theme="dark"] .section-title { color: #f1f5f9 !important; }
.stApp[data-theme="dark"] .about-content,
.stApp[data-theme="dark"] .experience-description,
.stApp[data-theme="dark"] .education-degree,
.stApp[data-theme="dark"] .project-description,
.stApp[data-theme="dark"] .award-description { color: #cbd5e1 !important; }
.stApp[data-theme="dark"] .experience-card,
.stApp[data-theme="dark"] .education-card,
.stApp[data-theme="dark"] .project-card,
.stApp[data-theme="dark"] .award-card,
.stApp[data-theme="dark"] .reference-card,
.stApp[data-theme="dark"] .skill-category {
    background: #1e293b !important;
    border-color: #475569 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
}
.stApp[data-theme="dark"] .experience-title,
.stApp[data-theme="dark"] .education-title,
.stApp[data-theme="dark"] .project-name,
.stApp[data-theme="dark"] .award-name,
.stApp[data-theme="dark"] .reference-name { color: #f1f5f9 !important; }
.stApp[data-theme="dark"] .skill-tag {
    background: #334155 !important;
    color: #cbd5e1 !important;
    border-color: #475569 !important;
}
@media (max-width: 768px) {
    .portfolio-section {
        padding: 30px 15px;
        margin: 40px 0;
    }
    .section-title { font-size: 1.6em; }
    .skills-container { grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)

# Hakkımda
st.markdown('<div class="portfolio-section" id="about">', unsafe_allow_html=True)
about_title = "📖 Hakkımda" if current_lang == "tr" else "📖 About Me"
st.markdown(f'<h2 class="section-title">{about_title}</h2>', unsafe_allow_html=True)

education_info = ""
if cv_data.get("education"):
    edu = cv_data["education"][0]
    institution = edu.get("institution", "")
    education_info = (
        f'<p style="text-align:center;color:#3b5bdb;'
        f'font-weight:500;margin-top:20px;font-size:1.25em;">🎓 {institution}</p>'
    )

profile_text = cv_data.get("profile", "")
if profile_text:
    st.markdown(f'<div class="about-content">{profile_text}</div>', unsafe_allow_html=True)
    if education_info:
        st.markdown(education_info, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Deneyim & Eğitim
st.markdown('<div class="portfolio-section" id="experience">', unsafe_allow_html=True)
exp_title = "💼 Deneyim & Eğitim" if current_lang == "tr" else "💼 Experience & Education"
st.markdown(f'<h2 class="section-title">{exp_title}</h2>', unsafe_allow_html=True)

for exp in cv_data.get("experience", []):
    t = exp.get("title", "")
    company = exp.get("company", "")
    duration = exp.get("duration", "")
    description = exp.get("description", "")
    st.markdown(f"""
    <div class="experience-card">
        <div class="experience-title">{t}</div>
        <div class="experience-company">{company}</div>
        <div class="experience-duration">{duration}</div>
        <div class="experience-description">{description}</div>
    </div>
""", unsafe_allow_html=True)

for edu in cv_data.get("education", []):
    institution = edu.get("institution", "")
    degree = edu.get("degree", "")
    years = edu.get("years", "")
    st.markdown(f"""
    <div class="education-card">
        <div class="education-title">{degree}</div>
        <div class="education-institution">{institution}</div>
        <div class="education-years">{years}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Projeler (seçilmiş)
st.markdown('<div class="portfolio-section" id="projects">', unsafe_allow_html=True)
proj_title = "🚀 Öne Çıkan Projeler" if current_lang == "tr" else "🚀 Featured Projects"
st.markdown(f'<h2 class="section-title">{proj_title}</h2>', unsafe_allow_html=True)

allowed_projects = [
    "AI-Powered Portfolio Chatbot",
    "FinTurk Finansal Asistan",
    "Customer Churn Prediction",
    "Energy Consumption Prediction API",
]
projects = [p for p in cv_data.get("projects", []) if p.get("name") in allowed_projects]

if projects:
    col1, col2 = st.columns(2)
    for i, proj in enumerate(projects):
        name_p = proj.get("name", "")
        tech = proj.get("technology", "")
        desc = proj.get("description", "")
        feats = proj.get("features", [])
        github = proj.get("github", "")

        if isinstance(desc, dict):
            description = desc.get(current_lang, desc.get("en", desc.get("tr", "")))
        else:
            description = desc

        if isinstance(feats, dict):
            features_list = feats.get(current_lang, feats.get("en", feats.get("tr", [])))
        elif isinstance(feats, list):
            features_list = feats
        else:
            features_list = []

        features_html = ""
        if features_list:
            features_html = '<div class="project-features">'
            for f in features_list:
                features_html += f'<div class="project-feature">{f}</div>'
            features_html += "</div>"

        github_link = ""
        if github:
            link_text = "🔗 GitHub'da Görüntüle" if current_lang == "tr" else "🔗 View on GitHub"
            github_link = f'<a href="{github}" target="_blank" class="project-link">{link_text}</a>'

        with (col1 if i % 2 == 0 else col2):
            st.markdown(f"""
            <div class="project-card">
                <div class="project-name">{name_p}</div>
                <div class="project-tech">{tech}</div>
                <div class="project-description">{description}</div>
                {features_html}
                {github_link}
            </div>
            """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Yetenekler
st.markdown('<div class="portfolio-section" id="skills">', unsafe_allow_html=True)
skills_title = "🛠️ Yetenekler" if current_lang == "tr" else "🛠️ Skills"
st.markdown(f'<h2 class="section-title">{skills_title}</h2>', unsafe_allow_html=True)

skills = cv_data.get("skills", {})
st.markdown('<div class="skills-container">', unsafe_allow_html=True)
for category, skill_list in skills.items():
    tags = "".join(f'<span class="skill-tag">{s}</span>' for s in skill_list)
    st.markdown(f"""
    <div class="skill-category">
        <div class="skill-category-title">{category}</div>
        <div>{tags}</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Ödüller
st.markdown('<div class="portfolio-section" id="awards">', unsafe_allow_html=True)
awards_title = "🏆 Ödüller" if current_lang == "tr" else "🏆 Awards & Achievements"
st.markdown(f'<h2 class="section-title">{awards_title}</h2>', unsafe_allow_html=True)

for award in cv_data.get("awards", []):
    name_a = award.get("name", "")
    org = award.get("organization", "")
    desc = award.get("description", "")
    st.markdown(f"""
    <div class="award-card">
        <div class="award-name">{name_a}</div>
        <div class="award-org">{org}</div>
        <div class="award-description">{desc}</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Medium yazıları
st.markdown('<div class="portfolio-section" id="articles">', unsafe_allow_html=True)
articles_title = "📝 Son Yazılar" if current_lang == "tr" else "📝 Latest Articles"
st.markdown(f'<h2 class="section-title">{articles_title}</h2>', unsafe_allow_html=True)

st.markdown("""
<style>
.article-card {
    background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 24px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}
.article-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(59, 91, 219, 0.15);
    border-color: #3b5bdb;
}
.article-title {
    font-size: 1.35em;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 12px;
    line-height: 1.5;
}
.article-summary {
    color: #64748b;
    font-size: 1.05em;
    line-height: 1.7;
    margin-bottom: 16px;
}
.article-link {
    display: inline-block;
    background: linear-gradient(135deg, #3b5bdb 0%, #5b21b6 100%);
    color: white;
    padding: 10px 20px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.2s ease;
}
.article-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}
.articles-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 24px;
    margin-top: 24px;
}
.articles-grid .article-card {
    height: 100%;
}
.articles-grid .article-card:last-child:nth-child(2n+1) {
    grid-column: 1 / -1;
    max-width: 520px;
    margin: 0 auto;
    width: 100%;
}
@media (max-width: 900px) {
    .articles-grid {
        grid-template-columns: 1fr;
    }
}
.stApp[data-theme="dark"] .article-card {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    border-color: #475569;
}
.stApp[data-theme="dark"] .article-title { color: #f1f5f9; }
.stApp[data-theme="dark"] .article-summary { color: #cbd5e1; }
</style>
""", unsafe_allow_html=True)

medium_articles = cv_data.get("medium_articles", [])
if medium_articles:
    cards = []
    for article in medium_articles[:5]:
        title_m = article.get("title", "")
        url_m = article.get("url", "")
        summary_tr = article.get("summary_tr", "")
        summary_en = article.get("summary_en", "")
        summary = summary_tr if current_lang == "tr" else summary_en

        cards.append(
            f'<div class="article-card">'
            f'<div class="article-title">{title_m}</div>'
            f'<div class="article-summary">{summary}</div>'
            f'<a href="{url_m}" target="_blank" class="article-link">📖 Read on Medium</a>'
            f'</div>'
        )

    cards_html = "".join(cards)
    st.markdown(f'<div class="articles-grid">{cards_html}</div>', unsafe_allow_html=True)
else:
    no_text = "Yazı bulunamadı." if current_lang == "tr" else "No articles available."
    st.markdown(
        f'<p style="text-align:center;color:#64748b;">{no_text}</p>',
        unsafe_allow_html=True,
    )
st.markdown("</div>", unsafe_allow_html=True)

# Referanslar
st.markdown('<div class="portfolio-section" id="references">', unsafe_allow_html=True)
refs_title = "📞 Referanslar" if current_lang == "tr" else "📞 References"
st.markdown(f'<h2 class="section-title">{refs_title}</h2>', unsafe_allow_html=True)

st.markdown('<div class="reference-list">', unsafe_allow_html=True)
for ref in cv_data.get("references", []):
    name_r = ref.get("name", "")
    title_r = ref.get("title", "")
    org_r = ref.get("organization", "")
    st.markdown(f"""
    <div class="reference-card">
        <div class="reference-name">{name_r}</div>
        <div class="reference-title">{title_r}</div>
        <div class="reference-org">{org_r}</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# İletişim
st.markdown('<div class="portfolio-section" id="contact">', unsafe_allow_html=True)
contact_title = "📧 İletişim" if current_lang == "tr" else "📧 Get In Touch"
st.markdown(f'<h2 class="section-title">{contact_title}</h2>', unsafe_allow_html=True)

contact_text_tr = (
    "Yeni fırsatlar ve işbirlikleri hakkında konuşmak için benimle iletişime geçebilirsiniz. "
    "E-posta veya LinkedIn üzerinden bana ulaşabilirsiniz."
)
contact_text_en = (
    "I'm always interested in hearing about new opportunities and collaborations. "
    "Feel free to reach out via email or LinkedIn."
)
contact_text = contact_text_tr if current_lang == "tr" else contact_text_en

email = cv_data.get("email", "")
links = cv_data.get("links", {})

st.markdown(f"""
<div style="text-align:center;max-width:600px;margin:0 auto;">
  <p style="font-size:1.15em;line-height:1.8;color:#475569;margin-bottom:30px;">{contact_text}</p>
  <div style="display:flex;justify-content:center;gap:20px;flex-wrap:wrap;">
    <a href="mailto:{email}" style="display:inline-flex;align-items:center;gap:8px;color:#3b5bdb;text-decoration:none;font-weight:500;padding:10px 20px;border:2px solid #3b5bdb;border-radius:8px;transition:all 0.2s;">
      📧 Mail Me
    </a>
    <a href="{links.get('linkedin', '#')}" target="_blank" style="display:inline-flex;align-items:center;gap:8px;color:#3b5bdb;text-decoration:none;font-weight:500;padding:10px 20px;border:2px solid #3b5bdb;border-radius:8px;transition:all 0.2s;">
      💼 LinkedIn
    </a>
    <a href="{links.get('github', '#')}" target="_blank" style="display:inline-flex;align-items:center;gap:8px;color:#3b5bdb;text-decoration:none;font-weight:500;padding:10px 20px;border:2px solid #3b5bdb;border-radius:8px;transition:all 0.2s;">
      🔗 GitHub
    </a>
    <a href="{links.get('medium', '#')}" target="_blank" style="display:inline-flex;align-items:center;gap:8px;color:#3b5bdb;text-decoration:none;font-weight:500;padding:10px 20px;border:2px solid #3b5bdb;border-radius:8px;transition:all 0.2s;">
      ✍️ Medium
    </a>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

chat_widget_injection = """
<script>
(function() {
  const parentDoc = window.parent.document;
  if (!parentDoc) { return; }
  if (parentDoc.getElementById('floating-chat-root')) { return; }

  if (!parentDoc.getElementById('floating-chat-style')) {
    const style = parentDoc.createElement('style');
    style.id = 'floating-chat-style';
    style.textContent = `
      #floating-chat-root {
        position: fixed;
        right: 24px;
        bottom: 24px;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 12px;
        z-index: 10000;
        font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      }
      #floating-chat-launcher {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        border: none;
        border-radius: 999px;
        padding: 11px 20px;
        background: linear-gradient(135deg, #5f3dc4 0%, #7c3aed 50%, #a855f7 100%);
        color: #fff;
        font-weight: 600;
        font-size: 0.95rem;
        box-shadow: 0 14px 32px rgba(76, 29, 149, 0.25);
        cursor: pointer;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
      }
      #floating-chat-launcher:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 40px rgba(76, 29, 149, 0.3);
      }
      #floating-chat-launcher .icon {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.15);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1.15rem;
      }
      #floating-chat-panel {
        width: 420px;
        max-width: calc(100vw - 40px);
        background: #ffffff;
        border-radius: 28px;
        box-shadow: 0 24px 70px rgba(15, 23, 42, 0.28);
        padding: 20px 22px;
        display: none;
        flex-direction: column;
        gap: 16px;
      }
      #floating-chat-panel.is-visible {
        display: flex;
      }
      #floating-chat-panel header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: 700;
        font-size: 1rem;
        color: #0f172a;
      }
      #floating-chat-panel header button {
        border: none;
        background: none;
        font-size: 1.4rem;
        color: #cbd5f5;
        cursor: pointer;
        transition: color 0.2s ease;
      }
      #floating-chat-panel header button:hover {
        color: #94a3b8;
      }
      #floating-chat-panel .status-box {
        display: flex;
        gap: 12px;
        align-items: center;
        padding: 12px 14px;
        border-radius: 16px;
        background: #f1f5f9;
      }
      #floating-chat-panel .status-box span {
        font-size: 2rem;
      }
      #floating-chat-panel .status-box .texts {
        display: flex;
        flex-direction: column;
        gap: 4px;
      }
      #floating-chat-panel .status-title {
        font-weight: 600;
        font-size: 1.05rem;
        color: #0f172a;
      }
      #floating-chat-panel .status-desc {
        font-size: 0.94rem;
        color: #475569;
      }
      #floating-chat-panel .wake-button {
        border: none;
        border-radius: 14px;
        padding: 11px 18px;
        font-weight: 600;
        background: #2563eb;
        color: #fff;
        cursor: pointer;
        transition: background 0.2s ease, box-shadow 0.2s ease;
      }
      @media (max-width: 640px) {
        #floating-chat-root { right: 8px; bottom: 8px; }
        #floating-chat-panel { width: calc(100vw - 16px); }
      }
    `;
    parentDoc.head.appendChild(style);
  }

  const root = parentDoc.createElement('div');
  root.id = 'floating-chat-root';
  root.innerHTML = `
    <button id="floating-chat-launcher">
      <span>AI Asistanına sor!</span>
      <div class="icon">🤖</div>
    </button>
    <div id="floating-chat-panel">
      <header>
        <div>AI Portföy Asistanı</div>
        <button id="floating-chat-close" aria-label="Kapat">×</button>
      </header>
      <iframe
        src="/?embedded_chat=1"
        title="AI Portföy Asistanı"
        style="width: 100%; height: 620px; border: none; border-radius: 18px; overflow: hidden;"
      ></iframe>
    </div>
  `;
  parentDoc.body.appendChild(root);

  const launcher = root.querySelector('#floating-chat-launcher');
  const panel = root.querySelector('#floating-chat-panel');
  const closeBtn = root.querySelector('#floating-chat-close');
  if (!launcher || !panel || !closeBtn) { return; }

  let isOpen = false;
  const togglePanel = (force) => {
    if (typeof force === 'boolean') {
      isOpen = force;
    } else {
      isOpen = !isOpen;
    }
    if (isOpen) {
      panel.classList.add('is-visible');
    } else {
      panel.classList.remove('is-visible');
    }
  };

  launcher.addEventListener('click', () => togglePanel());
  closeBtn.addEventListener('click', (event) => {
    event.stopPropagation();
    togglePanel(false);
  });
  parentDoc.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      togglePanel(false);
    }
  });
})();
</script>
"""
components.html(chat_widget_injection, height=0, width=0)
