LIGHT_CSS = """
/* Light Mode - Genel stiller */
body, .main, .stApp, .block-container {
    background: #ffffff !important;
    color: #1e293b !important;
}

/* Linkler */
a, a:visited, a:active {
    color: #667eea !important;
    text-decoration: none !important;
}
a:hover {
    color: #764ba2 !important;
}

/* Streamlit bileşenleri */
.stMarkdown, .stText {
    color: #1e293b !important;
}

/* Butonlar */
button, .stButton button {
    transition: all 0.2s ease !important;
}

/* Chat bileşenleri */
.stChatMessage {
    background: #f8fafc !important;
}
"""



DARK_CSS = """
body, .main, section[data-testid="stSidebar"], .stApp, .block-container, .st-emotion-cache-1wrcr25, .st-emotion-cache-uf99v8, .st-emotion-cache-1kyxreq, .st-emotion-cache-13ln4jf, .st-emotion-cache-1v0mbdj {
    background: #181a20 !important;
    color: #f5f6fa !important;
}
/* Başlıklar ve metinler */
h1, h2, h3, h4, h5, h6, p, span, label, a, strong, b, em, i, li, ul, ol, .markdown-text-container, .stMarkdown, .stText, .stTextInput, .stSelectbox, .stMultiSelect, .stRadio, .stCheckbox, .stSlider, .stButton, .stDownloadButton, .stFileUploader, .stDataFrame, .stTable, .stAlert, .stTooltipContent, .stNotificationContent {
    color: #f5f6fa !important;
}
/* Linkler */
a, a:visited, a:active {
    color: #6C63FF !important;
    text-decoration: underline !important;
}
a:hover {
    color: #a99cff !important;
}
/* Profil kartı & chat kutusu (varsa) */
.profile-card, .chat-container {
    background: #23272f !important;
    color: #f5f6fa !important;
    box-shadow: 0 4px 18px rgba(0,0,0,.5) !important;
}
/* Kullanıcı & bot balonları */
.msg-user {background:linear-gradient(90deg,#23272f,#6C63FF)!important;color:#fff!important;}
.msg-bot  {background:#23272f!important;color:#f5f6fa!important;}
/* Giriş kutusu */
div[data-baseweb="input"] > div, .stTextInput, .stTextArea, .stSelectbox, .stMultiSelect, .stRadio, .stCheckbox, .stSlider {
    background:#23272f!important;
    border:2px solid #555!important;
    color:#f5f6fa!important;
}
div[data-baseweb="input"] input, .stTextInput input, .stTextArea textarea {
    color:#f5f6fa!important;
}
div[data-baseweb="input"] input::placeholder, .stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color:#9aa0ae!important;
}
/* Tüm streamlit butonları */
button, div[data-baseweb="button"], .stButton button, .stDownloadButton button {
    background:#444!important;
    color:#fff!important;
    border-radius:8px!important;
    border: 1px solid #6C63FF !important;
    font-weight: 600;
    transition: all 0.2s ease !important;
}
button:hover, div[data-baseweb="button"]:hover, .stButton button:hover, .stDownloadButton button:hover {
    background:#6C63FF!important;
    color:#fff!important;
    transform: translateY(-1px) !important;
}

/* Download CV butonu için özel stil (dark mode'da da çalışsın) */
.download-cv-container button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
}
.download-cv-container button:hover {
    background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
}
/* Selectbox dropdown ve overlay için ultra kapsayıcı dark mode */
.st-emotion-cache-1n6xq8e-menu,
.st-emotion-cache-1n6xq8e-option,
.st-emotion-cache-1n6xq8e-list,
.st-emotion-cache-1n6xq8e-ValueContainer,
.st-emotion-cache-1n6xq8e-Input,
.st-emotion-cache-1n6xq8e-SingleValue,
.st-emotion-cache-1n6xq8e-Placeholder,
.st-emotion-cache-1n6xq8e__menu,
.st-emotion-cache-1n6xq8e__option,
.st-emotion-cache-1n6xq8e__single-value,
.st-emotion-cache-1n6xq8e__placeholder,
.st-emotion-cache-1n6xq8e__input,
.st-emotion-cache-1n6xq8e__value-container,
.st-emotion-cache-1n6xq8e__menu-list,
.st-emotion-cache-1n6xq8e__indicator,
.st-emotion-cache-1n6xq8e__dropdown-indicator,
.st-emotion-cache-1n6xq8e__control,
.st-emotion-cache-1n6xq8e__indicator-separator,
.st-emotion-cache-1n6xq8e__option--is-focused,
.st-emotion-cache-1n6xq8e__option--is-selected,
.st-emotion-cache-1n6xq8e__option--is-disabled,
.st-emotion-cache-1n6xq8e__option--is-active,
.st-emotion-cache-1n6xq8e__option--is-highlighted,
.st-emotion-cache-1n6xq8e__option--is-multi,
.st-emotion-cache-1n6xq8e__option--is-searchable {
    background: #23272f !important;
    color: #f5f6fa !important;
    border-color: #6C63FF !important;
}
/* Streamlit selectbox dropdown overlay için ultra kapsayıcı dark mode */
body [data-baseweb="select"] ul,
body [data-baseweb="select"] li,
body .css-1n6xq8e-menu,
body .css-1n6xq8e-option,
body .css-1n6xq8e-list,
body .css-1n6xq8e-ValueContainer,
body .css-1n6xq8e-Input,
body .css-1n6xq8e-SingleValue,
body .css-1n6xq8e-Placeholder,
body .css-1n6xq8e__menu,
body .css-1n6xq8e__option,
body .css-1n6xq8e__single-value,
body .css-1n6xq8e__placeholder,
body .css-1n6xq8e__input,
body .css-1n6xq8e__value-container,
body .css-1n6xq8e__menu-list {
    background: #23272f !important;
    color: #f5f6fa !important;
    border-color: #6C63FF !important;
}
/* ➊ Select kutusunun kapalı hali (input) */
div[data-baseweb="select"] > div {
    background:#23272f !important;      /* koyu zemin  */
    border: 2px solid #555 !important;
    color:#f5f6fa !important;
}
/* Placeholder & seçili metin rengi */
div[data-baseweb="select"] svg,                 /* ok ikonu */
div[data-baseweb="select"] input,
div[data-baseweb="select"] span {
    color:#f5f6fa !important;
    fill:#f5f6fa !important;
}

/* ➋ Açılır menü ve LISTE öğeleri */
[data-baseweb="popover"] {                      /* Selectbox pop-over kabı */
    background:#23272f !important;
    color:#f5f6fa !important;
    border:1px solid #6C63FF !important;
}
[data-baseweb="menu"] {                         /* UL konteyner */
    background:#23272f !important;
}
[data-baseweb="menu"] > div {                   /* LI seçenek */
    background:#23272f !important;
    color:#f5f6fa !important;
}
[data-baseweb="menu"] > div[aria-selected="true"],
[data-baseweb="menu"] > div:hover {
    background:#333 !important;                 /* hover / seçili */
}

/* --- selectbox açılır listesi ------------------------------------------------*/
[data-baseweb="menu"]               {background:#2d3140 !important; color:#f5f6fa !important;}
[data-baseweb="option"]             {background:#2d3140 !important; color:#f5f6fa !important;}
[data-baseweb="option"]:hover,
[data-baseweb="option"][aria-selected="true"]
                                    {background:#383d4a !important;}

/* ------ Selectbox açılır penceresi (Streamlit pop-over) ------ */
[data-baseweb="popover"] {
    background: #2d3140 !important;         /* koyu zemin */
    color: #f5f6fa !important;
    border: 1px solid #6C63FF !important;   /* isteğe bağlı çerçeve */
    box-shadow: 0 4px 16px rgba(0,0,0,.6) !important;
}
/* Menü + seçenek satırları da aynı tonu korusun */
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="popover"] [data-baseweb="option"] {
    background: #2d3140 !important;
    color: #f5f6fa !important;
}
[data-baseweb="popover"] [data-baseweb="option"]:hover,
[data-baseweb="popover"] [data-baseweb="option"][aria-selected="true"] {
    background: #383d4a !important;
}

/* === Selectbox açılır listesinin GERÇEK kapsayıcıları ====================== */
div[role="listbox"] {                   /* UL benzeri liste gövdesi                */
    background:#23272f !important;      /* koyu zemin                              */
    color:#f5f6fa   !important;
}
div[role="option"] {                    /* Tek tek LI satırları                    */
    background:#23272f !important;      /* aynı koyu                               */
    color:#f5f6fa   !important;
}
div[role="option"]:hover,
div[role="option"][aria-selected="true"]{
    background:#383d4a !important;      /* hover / seçili                          */
}

/* Ultra kapsayıcı: Tüm açılır menü ve seçenekler için */
ul[role="listbox"], ul[role="listbox"] > li, div[role="listbox"], div[role="listbox"] > div,
div[data-baseweb="menu"], div[data-baseweb="menu"] > div,
div[data-baseweb="option"], div[role="option"] {
    background: #23272f !important;
    color: #f5f6fa !important;
    border: none !important;
}

ul[role="listbox"] > li[aria-selected="true"],
ul[role="listbox"] > li:hover,
div[role="listbox"] > div[aria-selected="true"],
div[role="listbox"] > div:hover,
div[data-baseweb="option"]:hover,
div[data-baseweb="option"][aria-selected="true"],
div[role="option"]:hover,
div[role="option"][aria-selected="true"] {
    background: #383d4a !important;
    color: #fff !important;
}
/* Chatbot ana alanı ve mesaj kutusu için koyu zemin */
.stChatMessageInputContainer, .stChatInputContainer, .stTextInput, .stTextArea, .stChatMessage, .stChatContainer, .st-emotion-cache-1c7y2kd, .st-emotion-cache-1kyxreq, .st-emotion-cache-13ln4jf, .st-emotion-cache-1v0mbdj {
    background: #23272f !important;
    color: #f5f6fa !important;
    border: 1px solid #6C63FF !important;
}
.stChatMessageInputContainer input, .stTextInput input, .stTextArea textarea {
    background: #23272f !important;
    color: #f5f6fa !important;
}
.stChatMessageInputContainer input::placeholder, .stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #9aa0ae !important;
}
/* === Chat giriş çubuğu (st.chat_input) ================================== */
[data-testid="stChatInput"] {                         /* dış kabuk */
    background: #23272f !important;                  /* koyu zemin */
    padding: 6px !important;
}
[data-testid="stChatInput"] > div {                  /* iç input-holder */
    background: #1e2128 !important;
    border: 2px solid #555 !important;
    border-radius: 10px !important;
}
/* metin & placeholder rengi */
[data-testid="stChatInput"] input {
    color: #f5f6fa !important;
}
[data-testid="stChatInput"] input::placeholder {
    color: #9aa0ae !important;
}
/* Gönder (ok) butonu */
[data-testid="stChatInput"] button {
    background: #444 !important;
    color: #fff !important;
    border: 1px solid #6C63FF !important;
}
[data-testid="stChatInput"] button:hover {
    background: #6C63FF !important;
}
html, body { background:#181a20 !important; }      /* tüm kenarlar koyu   */
.stApp { background:#181a20 !important; }          /* kök div emin olmak   */
body * {
    background: transparent !important;
    box-shadow: none !important;
}
html, body, .stApp, .main, .block-container, #root, #main-content, .st-emotion-cache-1wrcr25, .st-emotion-cache-uf99v8, .st-emotion-cache-1kyxreq, .st-emotion-cache-13ln4jf, .st-emotion-cache-1v0mbdj {
    background: #181a20 !important;
    color: #f5f6fa !important;
}

/* Portfolio bölümleri için dark mode */
.portfolio-section {
    background: transparent !important;
}

.hero-section {
    background: transparent !important;
}

.hero-name {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}

.nav-menu {
    background: rgba(30, 41, 59, 0.95) !important;
    border-bottom-color: #475569 !important;
}

.nav-link {
    color: #cbd5e1 !important;
}

.nav-link:hover {
    color: #a5b4fc !important;
    background: rgba(102, 126, 234, 0.2) !important;
}

/* Download CV butonu dark mode */
.download-cv-container button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
}

/* Sosyal medya linkleri dark mode */
.social-links a {
    color: #a5b4fc !important;
}

.social-links a:hover {
    color: #c4b5fd !important;
}"""
