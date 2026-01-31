# modern_chatbot.py
import streamlit as st
import time
from datetime import datetime
from tools.gemini_tool import ask_gemini, generate_cover_letter
from common_css import LIGHT_CSS, DARK_CSS
import ast
import re
# ------------------------------------------------------------------ #
# (İstersen bu uzun CSS'i ayrı bir dosyaya da taşıyabilirsin)
CSS = """
<style>
/* —— KISA NOT —— 
   Aşağıya önceki dosyandaki tüm .profile-card, .chat-container,
   .msg-user, .msg-bot, dark-mode ve media-query kurallarını 
   eksiksiz yerleştir.  
*/
body
div[data-baseweb="input"] > div {
{ background: #f5f6fa !important;
border: 2px solid #c6c9d4 !important;  
border-radius: 10px !important;
box-shadow: 0 2px 6px rgba(0,0,0,0.08) !important;

div[data-baseweb="input"]:focus-within > div {
border: 2px solid #6C63FF !important;  /* marka moru */
box-shadow: 0 0 0 3px rgba(108,99,255,0.25) !important;
    }
    /* Placeholder metni daha koyu gri */
    div[data-baseweb="input"] input::placeholder {
        color: #8a8f9c !important; }
...
</style>
"""
# ------------------------------------------------------------------ #

LANG_TEXTS = {
    "tr": {
        "input_placeholder": "Mesajınızı yazın...",
        "send": "Gönder",
        "spinner": "Yanıt oluşturuluyor...",
        "download_cv": "⬇️ CV'yi İndir",
        "dark_mode": "🌙 Karanlık Mod Aktif",
    },
    "en": {
        "input_placeholder": "Type your message...",
        "send": "Send",
        "spinner": "Generating response...",
        "download_cv": "⬇️ Download CV",
        "dark_mode": "🌙 Dark Mode Active",
    },
}

# --- Modern Language Toggle Bar (flag icons, unified, no columns/buttons) ---
def language_and_theme_toggle():
    lang = st.session_state.get("lang", "tr")
    dark = st.session_state.get("dark_mode", False)
    page = st.session_state.get("page", "home")
    st.markdown("""
<style>
.toggle-bar-wrap {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 48px 0 48px 0;
    gap: 48px;
}
.lang-toggle, .theme-toggle {
    display: flex;
    align-items: center;
    background: #f3f4f8;
    border-radius: 40px;
    box-shadow: 0 4px 24px 0 rgba(49,130,206,0.10), 0 0 16px 2px #fff2;
    padding: 8px 18px;
    gap: 0;
    position: relative;
}
.lang-flag-btn, .theme-btn {
    width: 52px;
    height: 52px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.1em;
    background: none;
    border: none;
    margin: 0 6px;
    transition: filter 0.18s, background 0.18s, box-shadow 0.18s;
    cursor: pointer;
    outline: none;
    box-shadow: none;
}
.lang-flag-btn.selected, .theme-btn.selected {
    background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%);
    box-shadow: 0 4px 16px #2563eb33;
    filter: none;
    color: #fff;
}
.lang-flag-btn.unselected, .theme-btn.unselected {
    filter: grayscale(0.7) opacity(0.5);
    background: none;
    color: #222;
}
</style>
""", unsafe_allow_html=True)

    st.markdown(f'''
    <div class="toggle-bar-wrap">
      <form method="GET" style="display: flex; gap: 32px; align-items: center;">
        <div class="lang-toggle">
          <button class="lang-flag-btn{' selected' if lang == 'en' else ' unselected'}" name="setlang" value="en" type="submit">EN</button>
          <button class="lang-flag-btn{' selected' if lang == 'tr' else ' unselected'}" name="setlang" value="tr" type="submit">🇹🇷</button>
        </div>
        <div class="theme-toggle">
          <button class="theme-btn{' selected' if not dark else ' unselected'}" name="settheme" value="light" type="submit">☀️</button>
          <button class="theme-btn{' selected' if dark else ' unselected'}" name="settheme" value="dark" type="submit">🌙</button>
        </div>
      </form>
    </div>
    ''', unsafe_allow_html=True)

    # Query param ile state güncelle
    qp = st.query_params
    rerun_needed = False
    if qp.get("setlang"):
        st.session_state["lang"] = qp["setlang"]
        rerun_needed = True
    if qp.get("settheme"):
        st.session_state["dark_mode"] = qp["settheme"] == "dark"
        rerun_needed = True
    if rerun_needed:
        if page == "chat":
            st.session_state["page"] = "chat"
        qp.clear()
        st.rerun()

def _render_projects_section(cv_json):
    st.markdown("""
    <style>
    .project-accordion {
        margin: 16px 0;
    }
    .project-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 12px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 12px;
        font-weight: 600;
        font-size: 1.1em;
    }
    .project-header:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .project-content {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 8px;
        margin-left: 20px;
    }
    .project-section {
        margin-bottom: 16px;
        padding: 12px;
        background: #f8fafc;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    .section-title {
        color: #667eea;
        font-weight: 600;
        font-size: 1.1em;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-content {
        color: #374151;
        line-height: 1.6;
        padding-left: 8px;
    }
    .project-links {
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid #e5e7eb;
    }
    .project-link {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 6px 12px;
        border-radius: 6px;
        text-decoration: none;
        font-size: 0.9em;
        margin-right: 8px;
        margin-bottom: 4px;
        transition: all 0.2s ease;
    }
    .project-link:hover {
        background: #5a67d8;
        transform: translateY(-1px);
    }
    .project-summary {
        background: #f0f2f6;
        padding: 8px 12px;
        border-radius: 6px;
        margin-bottom: 12px;
        border-left: 3px solid #667eea;
    }
    .stApp[data-theme="dark"] .project-content {
        background: #1e293b !important;
        border-color: #475569 !important;
    }
    .stApp[data-theme="dark"] .project-section {
        background: #334155 !important;
        border-left-color: #8b5cf6 !important;
    }
    .stApp[data-theme="dark"] .section-title {
        color: #8b5cf6 !important;
    }
    .stApp[data-theme="dark"] .section-content {
        color: #e2e8f0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### 🚀 Projeler")

    project_icons = {
        "AI-Powered Portfolio Chatbot": "🚀",
        "Mobile App User Behavior Analysis": "📊",
        "Customer Churn Prediction": "🎯",
        "Movie Recommendation System": "🎬",
        "Natural Language to SQL Query Tool": "💬",
        "Smart Home Energy Management Application": "🏠",
        "Credit Score Prediction": "💰",
        "Energy Consumption Prediction API": "⚡",
        "AdventureWorks Sales Dashboard": "📈",
        "Real-Time Face Recognition App": "👤",
        "Safe Area Detection": "🛡️",
        "Market Prices Automation": "🛒",
        "Simple E-Commerce System with Python": "🛍️"
    }

    for i, proj in enumerate(cv_json.get("projects", [])):
        name = proj.get("name", "")
        tech = proj.get("technology", "")
        desc = proj.get("description", "")
        links = proj.get("links", [])

        icon = project_icons.get(name, "🚀")
        current_lang = st.session_state.get("lang", "tr")
        short_summary = ""

        summaries = {
            "AI-Powered Portfolio Chatbot": ("💬 AI destekli CV tabanlı asistan, job-fit & cover letter üretir",
                                             "💬 AI-powered CV assistant"),
            "Mobile App User Behavior Analysis": ("📱 Kullanıcı davranış analizi ve segmentasyon",
                                                  "📱 User behavior analysis and segmentation"),
            "Customer Churn Prediction": ("📉 Müşteri kaybı tahmin modeli",
                                          "📉 Customer churn prediction model"),
            "Movie Recommendation System": ("🎭 150M+ kayıt ile kişiselleştirilmiş film önerileri",
                                             "🎭 Personalized movie recommendations"),
            "Natural Language to SQL Query Tool": ("🗣️ Doğal dil ile SQL sorguları",
                                                    "🗣️ Natural language to SQL queries"),
            "Smart Home Energy Management Application": ("🏠 Akıllı ev enerji yönetimi",
                                                         "🏠 Smart home energy management"),
            "Credit Score Prediction": ("💳 Kredi skoru tahmin sistemi",
                                        "💳 Credit score prediction"),
            "Energy Consumption Prediction API": ("⚡ Enerji tüketimi tahmin API'si",
                                                  "⚡ Energy consumption prediction API"),
            "AdventureWorks Sales Dashboard": ("📊 Satış optimizasyonu dashboard'u",
                                               "📊 Sales optimization dashboard"),
            "Real-Time Face Recognition App": ("👤 Gerçek zamanlı yüz tanıma uygulaması",
                                               "👤 Real-time face recognition app"),
            "Safe Area Detection": ("🛡️ Güvenli alan tespit sistemi",
                                    "🛡️ Safe area detection system"),
            "Market Prices Automation": ("🛒 Pazar fiyatları otomasyonu",
                                         "🛒 Market prices automation"),
            "Simple E-Commerce System with Python": ("🛍️ Basit e-ticaret sistemi",
                                                     "🛍️ Simple e-commerce system"),
        }

        if name in summaries:
            tr, en = summaries[name]
            short_summary = tr if current_lang == "tr" else en

        expander_title = f"{icon} {name}"

        if short_summary:
            tooltip_css = f"""
            <style>
            .accordion-tooltip-{i} {{
                position: relative;
                margin-bottom: 0 !important;
            }}
            .accordion-tooltip-{i}:hover::after {{
                content: "{short_summary}";
                position: absolute;
                bottom: 130%;
                left: 50%;
                transform: translateX(-50%);
                background: #333;
                color: white;
                padding: 10px 15px;
                border-radius: 8px;
                font-size: 14px;
                z-index: 1000;
                max-width: 300px;
                word-wrap: break-word;
                white-space: normal;
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            }}
            </style>
            """
            st.markdown(tooltip_css, unsafe_allow_html=True)
            st.markdown(f'<div class="accordion-tooltip-{i}">', unsafe_allow_html=True)

        with st.expander(expander_title, expanded=False):
            st.markdown("**🛠️ Teknolojiler:**")
            st.markdown(tech)

            st.markdown("**📝 Açıklama:**")
            if isinstance(desc, dict):
                description = desc.get(current_lang, desc.get("en", desc.get("tr", str(desc))))
            else:
                description = desc
            st.markdown(description)

            features = proj.get("features", "")
            if isinstance(features, dict):
                features = features.get(current_lang, features.get("en", features.get("tr", [])))
            if isinstance(features, str):
                features = [
                    f.strip()
                    for f in features.replace("<br>", "\n").replace("•", "").split("\n")
                    if f.strip()
                ]

            if isinstance(features, list) and features:
                st.markdown("""
                <div class="project-section">
                    <div class="section-title">✨ <strong>Özellikler</strong></div>
                    <div class="section-content">
                """, unsafe_allow_html=True)
                for feature in features:
                    st.markdown(f"<div>• {feature}</div>", unsafe_allow_html=True)
                st.markdown("</div></div>", unsafe_allow_html=True)

            github_url = proj.get("github", "")
            if github_url:
                st.markdown("**🔗 GitHub:**")
                st.markdown(f"[📂 Projeyi İncele]({github_url})")

            if links:
                st.markdown("**🔗 Diğer Linkler:**")
                for link in links:
                    if isinstance(link, dict):
                        url = link.get("url", "")
                        text = link.get("text", "Link")
                    else:
                        url = link
                        text = "Proje Linki"
                    st.markdown(f"[{text}]({url})")

        if short_summary:
            st.markdown("</div>", unsafe_allow_html=True)


def run(*, tool_def, rag, cv_json):
    # Accordion boşluklarını kaldıran CSS
    st.markdown("""
    <style>
    /* Accordion boşluklarını tamamen kaldır */
    .streamlit-expanderHeader {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    .streamlit-expanderContent {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    /* Accordion'lar arası boşluk */
    div[data-testid="stExpander"] {
        margin-bottom: 0 !important;
        margin-top: 0 !important;
        padding-bottom: 0 !important;
        padding-top: 0 !important;
    }
    /* Son accordion'da alt boşluk olmasın */
    div[data-testid="stExpander"]:last-child {
        margin-bottom: 0 !important;
    }
    /* Tüm accordion container'ları için */
    div[data-testid="stExpander"] > div {
        margin: 0 !important;
        padding: 0 !important;
    }
    /* Accordion header ve content arasındaki boşluk */
    div[data-testid="stExpander"] .streamlit-expanderHeader {
        margin: 0 !important;
        padding: 8px 16px !important;
    }
    div[data-testid="stExpander"] .streamlit-expanderContent {
        margin: 0 !important;
        padding: 8px 16px !important;
    }
    
    /* Daha güçlü accordion boşluk kaldırma */
    div[data-testid="stExpander"] {
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
    }
    
    /* Her accordion arasındaki boşluğu kaldır */
    div[data-testid="stExpander"] + div[data-testid="stExpander"] {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Streamlit'in kendi CSS'ini geçersiz kıl */
    .stExpander {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Accordion wrapper'ı için */
    div[data-testid="stExpander"] {
        margin-bottom: 0 !important;
        margin-top: 0 !important;
        padding-bottom: 0 !important;
        padding-top: 0 !important;
        border-spacing: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Tema bazlı CSS
    if st.session_state.dark_mode:
        st.markdown(f"<style>{DARK_CSS}</style>", unsafe_allow_html=True)
    else:
        st.markdown(f"<style>{LIGHT_CSS}</style>", unsafe_allow_html=True)

    for k, v in {
        "lang": "tr",
        "dark_mode": False,
        "chat_history": [],
        "show_cover_form": False,
        "show_job_form": False,
        "welcome_message_shown": False,
        "typing_animation": False,
        "show_projects": False,
    }.items():
        st.session_state.setdefault(k, v)

    # --- Modern Language Toggle Bar (sağ üstte, sabit) ---
    st.markdown("""
    <style>
    .top-right-toggles {
        position: fixed;
        top: 64px;
        right: 32px;
        display: flex;
        gap: 16px;
        z-index: 1000;
        background: rgba(255,255,255,0.85);
        box-shadow: 0 4px 24px 0 rgba(49,130,206,0.10), 0 0 16px 2px #fff2;
        border-radius: 32px;
        padding: 8px 18px;
        align-items: center;
    }
    .toggle-btn {
        width: 38px;
        height: 38px;
        font-size: 1.1em;
        border-radius: 18px;
        border: none;
        background: none;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: background 0.18s, color 0.18s;
        color: #222;
        margin: 0 2px;
    }
    .toggle-btn.selected {
        background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%);
        color: #fff;
    }
    .back-btn-fixed {
        position: fixed;
        left: 32px;
        top: 64px;
        z-index: 1001;
    }
    @media (max-width: 600px) {
        .top-right-toggles { right: 8px; top: 32px; }
        .back-btn-fixed { left: 8px; top: 32px; }
    }
    </style>
    """, unsafe_allow_html=True)

    lang = st.session_state.get("lang", "tr")
    dark = st.session_state.get("dark_mode", False)
    page = st.session_state.get("page", "chat")
    st.markdown(f'''
    <div class="top-right-toggles">
      <form method="GET" style="display: flex; gap: 8px; align-items: center; margin:0;">
        <button class="toggle-btn{' selected' if lang == 'en' else ''}" name="setlang" value="en" type="submit">EN</button>
        <button class="toggle-btn{' selected' if lang == 'tr' else ''}" name="setlang" value="tr" type="submit">TR</button>
        <button class="toggle-btn{' selected' if not dark else ''}" name="settheme" value="light" type="submit">🌞</button>
        <button class="toggle-btn{' selected' if dark else ''}" name="settheme" value="dark" type="submit">🌙</button>
      </form>
    </div>
    ''', unsafe_allow_html=True)

    # Query param ile state güncelle
    qp = st.query_params
    rerun_needed = False
    if qp.get("setlang"):
        st.session_state["lang"] = qp["setlang"]
        rerun_needed = True
    if qp.get("settheme"):
        st.session_state["dark_mode"] = qp["settheme"] == "dark"
        rerun_needed = True
    if rerun_needed:
        st.session_state["page"] = page
        qp.clear()
        st.rerun()

    # Geri butonu kaldırıldı - artık ayrı sayfa değil, scroll ile erişiliyor

    # AI Asistan başlığı kaldırıldı - artık modal header'da gösteriliyor

    # --- Welcome Mesajı (Hemen görünür, animasyon yok) ---
    if not st.session_state.get("welcome_message_shown", False):
            welcome_text = {
                "tr": {
                    "title": "👋 Merhaba!",
                "message": "Ben Fatma Betül'ün AI destekli portföy asistanıyım. CV'sini, projelerini ve deneyimlerini senin için hızlıca özetleyebilirim. Başlamak için aşağıdaki başlıklardan birini seçebilir veya bana doğrudan bir soru yazabilirsin.",
                    "question": "Ne hakkında bilgi almak istersin?"
                },
                "en": {
                    "title": "👋 Hello!",
                "message": "I'm Fatma Betül's AI-powered portfolio assistant. I can quickly summarize her CV, projects, and professional experience for you. To begin, you can select one of the sections below or simply ask me a question directly.",
                "question": "What would you like to learn more about?"
                }
            }
            
            current_lang = st.session_state.get("lang", "tr")
            text = welcome_text[current_lang]
            
            with st.chat_message("🤖"):
                st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 18px; border-radius: 12px; margin: 8px 0;">
                <div style="font-size: 1.1em; font-weight: 600; margin-bottom: 6px;">{text['title']}</div>
                <div style="font-size: 0.95em; line-height: 1.4; margin-bottom: 8px;">{text['message']}</div>
                <div style="font-size: 1em; font-weight: 500; color: rgba(255,255,255,0.9);">{text['question']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.session_state["welcome_message_shown"] = True

    # --- Küçük Chip Tarzı Butonlar (İki Sütunlu) ---
    st.markdown("""
    <style>
    .cv-chip-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
        margin: 16px 0 24px 0;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .cv-chip-container div.stButton {
        width: 100% !important;
        margin: 0 !important;
    }
    
    .cv-chip-container div.stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2) !important;
        width: 100% !important;
        min-width: auto !important;
        max-width: 100% !important;
        min-height: 44px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
    }
    
    .cv-chip-container div.stButton > button:hover {
        cursor: pointer !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
    }
    
    .cv-chip-container div.stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Dark mode için */
    .stApp[data-theme="dark"] .cv-chip-container div.stButton > button {
        background: linear-gradient(135deg, #4c1d95 0%, #7c3aed 100%) !important;
        box-shadow: 0 2px 8px rgba(124, 58, 237, 0.3) !important;
    }
    
    .stApp[data-theme="dark"] .cv-chip-container div.stButton > button:hover {
        background: linear-gradient(135deg, #5b21b6 0%, #8b5cf6 100%) !important;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.4) !important;
    }
    
    /* Mobil responsive */
    @media (max-width: 600px) {
        .cv-chip-container {
            grid-template-columns: 1fr;
            gap: 8px;
        }
        .cv-chip-container div.stButton > button {
            font-size: 0.9rem !important;
            padding: 10px 16px !important;
            min-height: 40px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    articles_placeholder = st.container()

    icon_map = {
        "eğitim": "🎓",
        "deneyim": "💼",
        "projeler": "🚀",
        "ödüller": "🏆",
        "referanslar": "📞"
    }
    
    # Dil desteği için section isimleri
    section_names = {
        "tr": {
            "eğitim": "Eğitim",
            "deneyim": "Deneyim",
            "projeler": "Projeler",
            "ödüller": "Ödüller",
            "referanslar": "Referanslar"
        },
        "en": {
            "eğitim": "Education",
            "deneyim": "Experience",
            "projeler": "Projects",
            "ödüller": "Awards",
            "referanslar": "References"
        }
    }
    
    current_lang = st.session_state.get("lang", "tr")
    cv_sections = ["eğitim", "deneyim", "projeler", "ödüller", "referanslar"]
    st.markdown('<div class="cv-chip-container">', unsafe_allow_html=True)
    for section in cv_sections:
        section_display = section_names[current_lang].get(section, section.capitalize())
        if st.button(f"{icon_map[section]} {section_display}", key=f"cv_section_{section}_modern"):
            lines = []
            if section == "eğitim":
                for edu in cv_json.get("education", []):
                    inst = edu.get("institution", "")
                    degree = edu.get("degree", "")
                    years = edu.get("years", "")
                    lines.append(
                        f"<b>🎓 {inst}</b> <br><i>{degree}</i> <span style='color:#888'>({years})</span>"
                    )
            elif section == "deneyim":
                for exp in cv_json.get("experience", []):
                    title = exp.get("title", "")
                    company = exp.get("company", "")
                    duration = exp.get("duration", "")
                    desc = exp.get("description", "")
                    lines.append(
                        f"<b>💼 {title}</b> <br><i>{company}</i> <span style='color:#888'>({duration})</span><br>{desc}"
                    )
            elif section == "projeler":
                st.session_state.show_projects = True
            elif section == "ödüller":
                for award in cv_json.get("awards", []):
                    name = award.get("name", "")
                    org = award.get("organization", "")
                    lines.append(f"<b>🏆 {name}</b> <br><i>{org}</i>")
            elif section == "referanslar":
                for ref in cv_json.get("references", []):
                    name = ref.get("name", "")
                    title = ref.get("title", "")
                    org = ref.get("organization", "")
                    lines.append(f"<b>📞 {name}</b> <br><i>{title}</i> <span style='color:#888'>({org})</span>")
            if lines:
                st.markdown("""
                <style>
                .cv-info-block {
                  margin: 12px 0;
                  padding: 12px 16px;
                  border-radius: 14px;
                  background: #f3f4f8;
                  color: #333;
                  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
                }
                </style>
                """, unsafe_allow_html=True)
                response = "".join(f"<div class='cv-info-block'>{line}</div>" for line in lines)
                with articles_placeholder:
                    st.session_state.chat_history.append({"role": "user", "content": section.capitalize()})
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
        
    # --- Eski, büyük, yatay butonlar ve ilgili kodlar tamamen kaldırıldı ---

    # ---------- Chat geçmişi ----------
    # ---------- Projeler Accordion ----------
    if False and st.session_state.get("show_projects", False):
        st.markdown("""
        <style>
        .project-accordion {
            margin: 16px 0;
        }
        .project-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px 20px;
            border-radius: 12px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 600;
            font-size: 1.1em;
        }
        .project-header:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        .project-content {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 8px;
            margin-left: 20px;
        }
        .project-section {
            margin-bottom: 16px;
            padding: 12px;
            background: #f8fafc;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .section-title {
            color: #667eea;
            font-weight: 600;
            font-size: 1.1em;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .section-content {
            color: #374151;
            line-height: 1.6;
            padding-left: 8px;
        }
        .project-links {
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #e5e7eb;
        }
        .project-link {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 6px 12px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.9em;
            margin-right: 8px;
            margin-bottom: 4px;
            transition: all 0.2s ease;
        }
        .project-link:hover {
            background: #5a67d8;
            transform: translateY(-1px);
        }
        /* Proje entry'leri için tutarlı boşluk - tüm wrapper'lar */
        .project-entry {
            margin: 0 !important;
            margin-bottom: 6px !important;
            display: block !important;
        }
        /* Son proje için margin sıfırla */
        .project-entry:last-child,
        div[class*="project-entry-wrapper-"]:last-child {
            margin-bottom: 0 !important;
        }
        /* Tüm wrapper'lar için tutarlı margin - hem wrapper hem accordion */
        div[class*="project-entry-wrapper-"] {
            margin: 0 !important;
            margin-bottom: 6px !important;
            display: block !important;
        }
        div[class*="project-entry-wrapper-"]:last-child {
            margin-bottom: 0 !important;
        }
        /* Accordion'dan sonra boşluk için - her accordion'un altına 6px */
        div[class*="project-entry-wrapper-"] [data-testid="stExpander"],
        div[class*="project-entry-wrapper-"] > div[data-testid="stExpander"],
        div[class*="project-entry-wrapper-"] > div > div[data-testid="stExpander"] {
            margin: 0 !important;
            margin-bottom: 6px !important;
            margin-top: 0 !important;
        }
        div[class*="project-entry-wrapper-"]:last-child [data-testid="stExpander"],
        div[class*="project-entry-wrapper-"]:last-child > div[data-testid="stExpander"],
        div[class*="project-entry-wrapper-"]:last-child > div > div[data-testid="stExpander"] {
            margin-bottom: 0 !important;
        }
        /* Streamlit accordion'ları için margin - her accordion'un altına 6px - çok spesifik */
        div[class*="project-entry-wrapper-"] [data-testid="stExpander"],
        div[class*="project-entry-wrapper-"] > div[data-testid="stExpander"],
        div[class*="project-entry-wrapper-"] > div > div[data-testid="stExpander"] {
            margin: 0 !important;
            margin-bottom: 6px !important;
            margin-top: 0 !important;
        }
        div[class*="project-entry-wrapper-"]:last-child [data-testid="stExpander"],
        div[class*="project-entry-wrapper-"]:last-child > div[data-testid="stExpander"],
        div[class*="project-entry-wrapper-"]:last-child > div > div[data-testid="stExpander"] {
            margin-bottom: 0 !important;
        }
        /* Accordion'un parent div'leri için de margin kontrolü */
        div[class*="project-entry-wrapper-"] > div {
            margin-bottom: 0 !important;
        }
        /* Streamlit'in kendi margin'lerini override et - wrapper'lar arası */
        div[class*="project-entry-wrapper-"] + div[class*="project-entry-wrapper-"] {
            margin-top: 0 !important;
        }
        
        /* Accordion başlık özeti için */
        .expander-header small {
            display: block;
            margin-top: 4px;
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        /* Proje özeti kutusu */
        .project-summary {
            background: #f0f2f6;
            padding: 8px 12px;
            border-radius: 6px;
            margin-bottom: 12px;
            border-left: 3px solid #667eea;
        }
        
        /* Dark mode için accordion başlık özeti */
        .stApp[data-theme="dark"] .expander-header small {
            color: #cbd5e1 !important;
        }
        
        /* Dark mode için proje özeti */
        .stApp[data-theme="dark"] .project-summary {
            background: #334155 !important;
            border-left-color: #8b5cf6 !important;
        }
        .stApp[data-theme="dark"] .project-summary small {
            color: #e2e8f0 !important;
        }
        
        /* Dark mode için */
        .stApp[data-theme="dark"] .project-content {
            background: #1e293b !important;
            border-color: #475569 !important;
        }
        .stApp[data-theme="dark"] .project-section {
            background: #334155 !important;
            border-left-color: #8b5cf6 !important;
        }
        .stApp[data-theme="dark"] .section-title {
            color: #8b5cf6 !important;
        }
        .stApp[data-theme="dark"] .section-content {
            color: #e2e8f0 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🚀 Projeler")
        
        # Projeleri accordion olarak göster
        for i, proj in enumerate(cv_json.get("projects", [])):
            name = proj.get("name", "")
            tech = proj.get("technology", "")
            desc = proj.get("description", "")
            links = proj.get("links", [])
            
            # Sabit proje ikonları (görsel tutarlılık için)
            project_icons = {
                "AI-Powered Portfolio Chatbot": "🚀",
                "Mobile App User Behavior Analysis": "📊", 
                "Customer Churn Prediction": "🎯",
                "Movie Recommendation System": "🎬",
                "Natural Language to SQL Query Tool": "💬",
                "Smart Home Energy Management Application": "🏠",
                "Credit Score Prediction": "💰",
                "Energy Consumption Prediction API": "⚡",
                "AdventureWorks Sales Dashboard": "📈",
                "Real-Time Face Recognition App": "👤",
                "Safe Area Detection": "🛡️",
                "Market Prices Automation": "🛒",
                "Simple E-Commerce System with Python": "🛍️"
            }
            
            icon = project_icons.get(name, "🚀")  # Sabit ikonlar
            
            # Kısa özet oluştur (dil desteği ile)
            current_lang = st.session_state.get("lang", "tr")
            short_summary = ""
            
            if "AI-Powered Portfolio Chatbot" in name:
                short_summary = "💬 AI destekli CV tabanlı asistan, job-fit & cover letter üretir" if current_lang == "tr" else "💬 AI-powered CV-based assistant, generates job-fit & cover letters"
            elif "Mobile App User Behavior Analysis" in name:
                short_summary = "📱 Kullanıcı davranış analizi ve segmentasyon" if current_lang == "tr" else "📱 User behavior analysis and segmentation"
            elif "Customer Churn Prediction" in name:
                short_summary = "📉 Müşteri kaybı tahmin modeli" if current_lang == "tr" else "📉 Customer churn prediction model"
            elif "Movie Recommendation System" in name:
                short_summary = "🎭 150M+ kayıt ile kişiselleştirilmiş film önerileri" if current_lang == "tr" else "🎭 Personalized movie recommendations with 150M+ records"
            elif "Natural Language to SQL Query Tool" in name:
                short_summary = "🗣️ Doğal dil ile SQL sorguları" if current_lang == "tr" else "🗣️ Natural language to SQL queries"
            elif "Smart Home Energy Management" in name:
                short_summary = "🏠 Akıllı ev enerji yönetimi" if current_lang == "tr" else "🏠 Smart home energy management"
            elif "Credit Score Prediction" in name:
                short_summary = "💳 Kredi skoru tahmin sistemi" if current_lang == "tr" else "💳 Credit score prediction system"
            elif "Energy Consumption Prediction API" in name:
                short_summary = "⚡ Enerji tüketimi tahmin API'si" if current_lang == "tr" else "⚡ Energy consumption prediction API"
            elif "AdventureWorks Sales Dashboard" in name:
                short_summary = "📊 Satış optimizasyonu dashboard'u" if current_lang == "tr" else "📊 Sales optimization dashboard"
            elif "Real-Time Face Recognition App" in name:
                short_summary = "👤 Gerçek zamanlı yüz tanıma uygulaması" if current_lang == "tr" else "👤 Real-time face recognition app"
            elif "Safe Area Detection" in name:
                short_summary = "🛡️ Güvenli alan tespit sistemi" if current_lang == "tr" else "🛡️ Safe area detection system"
            elif "Market Prices Automation" in name:
                short_summary = "🛒 Pazar fiyatları otomasyonu" if current_lang == "tr" else "🛒 Market prices automation"
            elif "Simple E-Commerce System" in name:
                short_summary = "🛍️ Basit e-ticaret sistemi" if current_lang == "tr" else "🛍️ Simple e-commerce system"
            
            # GitHub linki varsa özete ekle (artık eklemiyoruz)
            # github_url = proj.get("github", "")
            # if github_url:
            #     short_summary += " [GitHub]"
            
            # Accordion başlığı
            expander_title = f"{icon} {name}"
            
            # Tüm projeleri aynı wrapper ile sar
            wrapper_class = f"project-entry-wrapper-{i}"
            if short_summary:
                tooltip_css = f"""
                <style>
                .{wrapper_class} {{
                    position: relative;
                    margin-bottom: 6px !important;
                }}
                .{wrapper_class}:last-child {{
                    margin-bottom: 0 !important;
                }}
                .{wrapper_class} .streamlit-expanderHeader {{
                    margin-bottom: 0 !important;
                    padding-bottom: 8px !important;
                }}
                .{wrapper_class}:hover::after {{
                    content: "{short_summary}";
                    position: absolute;
                    bottom: 130%;
                    left: 50%;
                    transform: translateX(-50%);
                    background: #333;
                    color: white;
                    padding: 10px 15px;
                    border-radius: 8px;
                    font-size: 14px;
                    z-index: 1000;
                    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
                    max-width: 300px;
                    word-wrap: break-word;
                    white-space: normal;
                }}
                .{wrapper_class}:hover::before {{
                    content: "";
                    position: absolute;
                    bottom: 125%;
                    left: 50%;
                    transform: translateX(-50%);
                    border: 6px solid transparent;
                    border-top-color: #333;
                    z-index: 1000;
                }}
                </style>
                """
                st.markdown(tooltip_css, unsafe_allow_html=True)
            else:
                # Tooltip olmayan projeler için de aynı margin
                no_tooltip_css = f"""
                <style>
                .{wrapper_class} {{
                    margin-bottom: 6px !important;
                }}
                .{wrapper_class}:last-child {{
                    margin-bottom: 0 !important;
                }}
                </style>
                """
                st.markdown(no_tooltip_css, unsafe_allow_html=True)
            
            # Accordion'u wrapper ile sar
            st.markdown(f'<div class="{wrapper_class} project-entry">', unsafe_allow_html=True)
            with st.expander(expander_title, expanded=False):
                # Teknolojiler bölümü
                st.markdown("**🛠️ Teknolojiler:**")
                st.markdown(tech)
                
                # Açıklama bölümü
                st.markdown("**📝 Açıklama:**")
                # Dil desteği için açıklamayı kontrol et
                if isinstance(desc, dict):
                    # Çoklu dil desteği varsa
                    current_lang = st.session_state.get("lang", "tr")
                    description = desc.get(current_lang, desc.get("en", desc.get("tr", str(desc))))
                else:
                    # Tek dil (string) ise
                    description = desc
                st.markdown(description)
                
                # Özellikler bölümü
                features = proj.get("features", "")
                features_list = []

                # Dil desteği için özellikleri kontrol et
                if isinstance(features, dict):
                    # Çoklu dil desteği varsa
                    current_lang = st.session_state.get("lang", "tr")
                    features = features.get(current_lang, features.get("en", features.get("tr", [])))

                if isinstance(features, list):
                    features_list = features
                elif isinstance(features, str):
                    features_clean = features.replace("<br>", "\n").replace("•", "")
                    features_list = [f.strip() for f in features_clean.split("\n") if f.strip()]

                if features_list:
                    features_html = """
                    <div class="project-section">
                        <div class="section-title">✨ <strong>Özellikler</strong></div>
                        <div class="section-content">
                    """
                    for feature in features_list:
                        features_html += f"<div>• {feature}</div>"

                    features_html += """
                        </div>
                    </div>
                    """  # 🔐 Kapanışlar burada net

                    st.markdown(features_html, unsafe_allow_html=True)
                
                # GitHub linki
                github_url = proj.get("github", "")
                if github_url:
                    st.markdown("**🔗 GitHub:**")
                    st.markdown(f"[📂 Projeyi İncele]({github_url})")
                
                # Diğer linkler
                if links:
                    st.markdown("**🔗 Diğer Linkler:**")
                    for link in links:
                        if isinstance(link, dict):
                            url = link.get("url", "")
                            text = link.get("text", "Link")
                        else:
                            url = link
                            text = "Proje Linki"
                        st.markdown(f"[{text}]({url})")
            st.markdown('</div>', unsafe_allow_html=True)

    # --- Cover letter PDF indir butonu ---
    if "cover_pdf_bytes" in st.session_state:
        st.download_button(
            "💾 Ön Yazıyı PDF Olarak İndir",
            data      = st.session_state.cover_pdf_bytes,
            file_name = st.session_state.cover_pdf_name,
            mime      = "application/pdf",
            key       = "cover_pdf_dl"
        )

    # --- Cover letter formu ---
    if st.session_state.get("show_cover_form"):
        _cover_letter_form(tool_def, rag)
        st.stop()

    # ---------- Aktif formlar ----------
    if st.session_state.show_cover_form:
        _cover_letter_form(tool_def, rag)
        st.stop()
    if st.session_state.show_job_form:
        _job_compatibility_flow(tool_def, LANG_TEXTS[st.session_state.lang])
        st.stop()

    # --- Chat geçmişi state kontrolü ---
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # --- 1) Girdiyi anında yakala ---
    # ---------- Chat geçmişi ----------
    # --- 2) Ekrana mevcut geçmişi bas ---
    for m in st.session_state.chat_history:
        if isinstance(m, dict):
            role = m.get("role", "assistant")
            content = m.get("content", "")
        elif isinstance(m, tuple) and len(m) == 2:
            role, content = m
        else:
            continue  # Beklenmeyen tipte veri varsa atla
        with st.chat_message("🧑‍💼" if role == "user" else "🤖"):
            st.markdown(content, unsafe_allow_html=True)

    user_msg = st.chat_input(LANG_TEXTS[st.session_state.lang]["input_placeholder"])

    # Kullanıcı 'cover letter yaz', 'ön yazı', 'cover letter', veya 'ön yazı yaz' derse formu aç
    trigger_phrases = ["cover letter yaz", "ön yazı", "cover letter", "ön yazı yaz"]
    if user_msg and any(p in user_msg.lower() for p in trigger_phrases):
        st.session_state.show_cover_form = True
        st.rerun()

    if user_msg and (not st.session_state.get("last_user_msg") or st.session_state.last_user_msg != user_msg):
        st.session_state.chat_history.append({"role": "user", "content": user_msg})
        st.session_state.last_user_msg = user_msg
        
        # Son 3 mesajı al (çok uzun geçmiş olmasın)
        recent_history = st.session_state.chat_history[-6:] if len(st.session_state.chat_history) > 6 else st.session_state.chat_history
        history_text = "\n".join([
                f"{m['role']}: {m['content']}" for m in recent_history if isinstance(m, dict)
            ])
        
        # RAG sonuçlarını çıkar
        retrieved_chunks = rag.search_similar_chunks(user_msg, top_k=5)

        # Kullanıcının sorusunda proje adı geçiyorsa ilgili projeyi doğrudan bağlama ekle
        project_context_blocks = []
        projects = cv_json.get("projects", [])
        msg_lower = user_msg.lower()
        for proj in projects:
            name = proj.get("name", "")
            if not name:
                continue
            name_tokens = [tok for tok in re.split(r"[^a-z0-9çğıöşü]+", name.lower()) if len(tok) > 2]
            if not name_tokens:
                continue
            match_count = sum(1 for tok in name_tokens if tok in msg_lower)
            if name.lower() in msg_lower or match_count >= max(1, len(name_tokens) // 2):
                tech = proj.get("technology", "")
                desc = proj.get("description", "")
                features = proj.get("features", "")
                formatted = (
                    f"Proje Adı: {name}\n"
                    f"Teknolojiler: {tech}\n"
                    f"Açıklama: {desc}\n"
                    f"Özellikler: {features}"
                )
                project_context_blocks.append(formatted)

        # Eğitim bilgilerini her zaman (özellikle 'eğitim', 'education', 'üniversite' vb. geçtiğinde)
        education_block = ""
        edu_list = cv_json.get("education", [])
        if edu_list:
            parts = []
            for edu in edu_list:
                inst = edu.get("institution", "")
                degree = edu.get("degree", "")
                years = edu.get("years", "")
                parts.append(f"{inst} - {degree} ({years})")
            education_block = "Eğitim Bilgileri:\n" + "\n".join(parts)

        context_chunks = list(retrieved_chunks)

        # Kullanıcı sorusu eğitimle ilgiliyse eğitim bloğunu bağlama özellikle ekle
        if any(word in msg_lower for word in ["eğitim", "school", "university", "üniversite"]):
            if education_block:
                context_chunks.append(education_block)

        if project_context_blocks:
            context_chunks.append("Eşleşen Projeler:\n" + "\n\n".join(project_context_blocks))
        elif projects:
            # RAG başarısız olursa en azından ilk birkaç projeyi ver
            fallback_projects = []
            for proj in projects[:5]:
                fallback_projects.append(
                    f"Proje Adı: {proj.get('name','')}\nTeknolojiler: {proj.get('technology','')}\nAçıklama: {proj.get('description','')}"
                )
            context_chunks.append("Örnek Projeler:\n" + "\n\n".join(fallback_projects))

        context_text = "\n---\n".join(context_chunks)
        
        # Dil seçimine göre prompt oluştur
        current_lang = st.session_state.get("lang", "tr")
        if current_lang == "tr":
            language_prompt = (
                "Sen Fatma Betül'ün AI portföy asistanısın. "
                "Sadece Türkçe cevap ver. İngilizce çeviri yapma. "
                "Kullanıcının sorusuna yanıt verirken aşağıdaki CV bağlamını kullan. "
                "Bağlamda bilgi yoksa bunu açıkça belirt ve uydurma."
            )
            question_label = "Kullanıcı Sorusu"
            context_label = "CV Bağlamı"
        else:
            language_prompt = (
                "You are Fatma Betül's AI portfolio assistant. "
                "Answer only in English. Do not provide Turkish translations. "
                "Use the CV context below. If the context lacks the answer, say so."
            )
            question_label = "User Question"
            context_label = "CV Context"
        
        full_prompt = (
            f"{language_prompt}\n\n"
            f"{context_label}:\n{context_text}\n\n"
            f"{question_label}:\n{user_msg}\n\n"
            f"Son sohbet geçmişi (referans için):\n{history_text}"
        )
        assistant_reply = ask_gemini(full_prompt)
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
        st.rerun()

    if st.session_state.get("show_projects", False):
        _render_projects_section(cv_json)



# ------------------------------------------------------------------ #
def _cover_letter_form(tool_def, rag):
    with st.form("cover_letter"):
        st.info("📄 Ön yazıyı oluşturun:")
        job_desc = st.text_area("💼 İş Tanımı")
        company  = st.text_input("🏢 Şirket")
        lang     = st.selectbox("🌐 Dil", ["tr", "en"])
        submitted = st.form_submit_button("✍️ Oluştur")

    if not submitted:
        return

    cv_text = "\n".join(rag.search_similar_chunks("özgeçmiş"))
    res = tool_def.execute_tool("generate_cover_letter", {
        "job_description": job_desc,
        "cv_text": cv_text,
        "language": lang,
        "company_name": company,
    })

    if res["success"]:
        letter_text = res["data"]["text"]
        st.session_state.chat_history.append({"role": "assistant", "content": letter_text})
        st.session_state.cover_pdf_bytes = res["data"]["pdf_bytes"]
        st.session_state.cover_pdf_name  = res["data"]["filename"]
        st.session_state.show_cover_form = False
        st.rerun()
    else:
        st.session_state.chat_history.append({"role": "assistant", "content": f"❌ {res['message']}"})
        st.session_state.show_cover_form = False
        st.rerun()



def _job_compatibility_flow(tool_def, LTXT):
    with st.form("job_form"):
        st.info("📊 İş uyum analizi için iş ilanını girin.")
        job_desc = st.text_area("💼 İş Tanımı")
        company = st.text_input("🏢 Şirket Adı")
        lang = st.selectbox("🌐 Dil", ["tr", "en"])
        submitted = st.form_submit_button("🚀 Analizi Başlat")
    if not submitted:
        return

    result = tool_def.execute_tool(
        "analyze_job_compatibility",
        {
            "job_description": job_desc,
            "report_language": lang,
            "company_name": company,
        },
    )
    reply = (
        result["data"]["report_text"]
        if result.get("success")
        else "Analiz oluşturulamadı 😕"
    )
    st.session_state.chat_history.append({"role": "bot", "content": reply})
