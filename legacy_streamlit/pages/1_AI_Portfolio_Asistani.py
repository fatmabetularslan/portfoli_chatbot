import streamlit as st

from rag_system import load_cv_index
from tools.tool_definitions import ToolDefinitions
import modern_chatbot

st.set_page_config(
    page_title="AI Portföy Asistanı",
    page_icon="🤖",
    layout="wide",
)


@st.cache_resource(show_spinner=False)
def _init_resources():
    rag = load_cv_index("betül-cv.json")
    tool_def = ToolDefinitions()
    try:
        tool_def.initialize_job_analyzer(None, rag.cv_json, rag)
    except Exception as exc:
        st.warning(f"Job analyzer başlatılamadı: {exc}")
    return rag, tool_def


rag, tool_def = _init_resources()
cv_json = getattr(rag, "cv_json", {})

st.markdown(
    "<style>.stMainBlockContainer {padding-top: 3rem!important;}</style>",
    unsafe_allow_html=True,
)

modern_chatbot.run(tool_def=tool_def, rag=rag, cv_json=cv_json)

