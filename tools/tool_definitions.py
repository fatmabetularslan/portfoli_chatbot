# tools/tool_definitions.py

from google.generativeai.types import Tool, FunctionDeclaration
from typing import List, Any, Dict
import streamlit as st
from tools.social_media_tool import SocialMediaAggregator
from tools.job_compatibility_tool import JobCompatibilityAnalyzer
from tools.pdf_generator import JobCompatibilityPDFGenerator
from datetime import datetime
from tools.gemini_tool import generate_cover_letter
from pathlib import Path
import base64

PDF_PATH = Path("assets/Fatma-Betül-ARSLAN-cv.pdf")

# --- CSS: Beyaz büyük butonlar için ---
st.markdown("""
<style>
.cv-action-btn > button {
    background: #fff !important;
    color: #1D3557 !important;
    border: 2px solid #e3e8f0 !important;
    border-radius: 16px !important;
    font-size: 1.25em !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 12px #1d355722;
    margin-bottom: 18px !important;
    padding: 20px 0 !important;
    transition: all 0.18s;
}
.cv-action-btn > button:hover {
    background: #f1f5fa !important;
    color: #274472 !important;
    border-color: #457B9D !important;
}
</style>
""", unsafe_allow_html=True)

class ToolDefinitions:
    """Tool definitions for Gemini function calling."""

    def __init__(self):
        self.social_media_aggregator = SocialMediaAggregator()
        self.job_compatibility_analyzer = None
        self.pdf_generator = JobCompatibilityPDFGenerator()

    def initialize_job_analyzer(self, client, cv_data, rag_system=None):
        try:
            self.job_compatibility_analyzer = JobCompatibilityAnalyzer(cv_data, rag_system)
            return True
        except Exception as e:
            print(f"[ERROR] Job analyzer init failed: {e}")
            return False

    # ========== TOOL DEFINITIONS ==========

    @staticmethod
    def get_email_tool_definition() -> Tool:
        return Tool(function_declarations=[
            FunctionDeclaration(
                name="prepare_email",
                description="Prepare an email to Fatma Betül when someone wants to contact her.",
                parameters={
                    "type": "object",
                    "properties": {
                        "sender_name": {"type": "string", "description": "Sender's full name"},
                        "sender_email": {"type": "string", "description": "Sender's email"},
                        "message": {"type": "string", "description": "Email content"}
                    },
                    "required": ["sender_name", "sender_email", "message"]
                }
            )
        ])

    @staticmethod
    def get_social_media_tool_definition() -> Tool:
        return Tool(function_declarations=[
            FunctionDeclaration(
                name="get_recent_posts",
                description="Fetch Fatma Betül's recent Medium posts.",
                parameters={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Max number of posts (default 5)"},
                        "search_query": {"type": "string", "description": "Optional filter for topic"}
                    },
                    "required": []
                }
            )
        ])

    @staticmethod
    def get_job_compatibility_tool_definition() -> Tool:
        return Tool(function_declarations=[
            FunctionDeclaration(
                name="analyze_job_compatibility",
                description="Compare job description with Fatma Betül's profile and generate a compatibility report.",
                parameters={
                    "type": "object",
                    "properties": {
                        "job_description": {"type": "string", "description": "Full job description text"},
                        "report_language": {"type": "string", "enum": ["en", "tr"], "description": "Report language"},
                        "company_name": {"type": "string", "description": "Company name"}
                    },
                    "required": ["job_description", "report_language", "company_name"]
                }
            )
        ])

    @staticmethod
    def get_cover_letter_tool_definition() -> Tool:
        return Tool(function_declarations=[
            FunctionDeclaration(
                name="generate_cover_letter",
                description="Generate a custom cover letter for Fatma Betül based on job description and CV.",
                parameters={
                    "type": "object",
                    "properties": {
                        "job_description": {"type": "string"},
                        "cv_text": {"type": "string"},
                        "language": {"type": "string", "enum": ["en", "tr"]}
                    },
                    "required": ["job_description", "cv_text", "language"]
                }
            )
        ])

    @staticmethod
    def get_pdf_generation_tool_definition() -> Tool:
        return Tool(function_declarations=[
            FunctionDeclaration(
                name="generate_compatibility_pdf",
                description="Generate PDF report from latest job compatibility result.",
                parameters={"type": "object", "properties": {}}
            )
        ])

    def get_all_tools(self) -> list:
        tools = [
            self.get_email_tool_definition(),
            self.get_social_media_tool_definition(),
            self.get_job_compatibility_tool_definition(),
            self.get_pdf_generation_tool_definition(),
            self.get_cover_letter_tool_definition()
        ]
        return [func for tool in tools for func in tool.function_declarations]

    # ========== TOOL EXECUTION ==========

    def execute_tool(self, tool_name: str, tool_args: Dict) -> Dict[str, Any]:
        if tool_name == "prepare_email":
            tool_args['subject'] = "New Message from Portfolio Bot"
            st.session_state.pending_email = tool_args
            return {"success": True, "message": "Email prepared.", "data": tool_args}
        elif tool_name == "get_recent_posts":
            try:
                posts = self.social_media_aggregator.get_medium_posts(tool_args.get("limit", 5))
                language = "tr" if "tr" in str(st.session_state.get("messages", [])).lower() else "en"
                summary = self.social_media_aggregator.format_posts_for_chat(posts, language)
                return {
                    "success": True,
                    "message": "Posts retrieved.",
                    "data": {"posts": posts, "formatted_response": summary, "render_cards": True}
                }
            except Exception as e:
                return {"success": False, "message": f"Failed to fetch posts: {e}"}
        elif tool_name == "generate_compatibility_pdf":
            report = st.session_state.get("last_compatibility_report")
            if not report:
                return {"success": False, "message": "No report found. Run analysis first."}
            try:
                pdf_bytes = self.pdf_generator.generate_pdf(
                    report,
                    st.session_state.get("last_job_title", "Unknown Position"),
                    "Fatma Betül Arslan",
                    st.session_state.get("last_report_language", "en"),
                    st.session_state.get("last_company_name", "Unknown Company")
                )
                st.session_state.pdf_data = pdf_bytes
                st.session_state.pdf_filename = (
                    f"job_compatibility_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                )
                return {
                    "success": True,
                    "message": "PDF ready.",
                    "data": {"filename": st.session_state.pdf_filename}
                }
            except Exception as e:
                return {"success": False, "message": f"PDF error: {e}"}
        elif tool_name == "analyze_job_compatibility":
                if not self.job_compatibility_analyzer:
                    return {"success": False, "message": "Analyzer not initialized"}
                try:
                    report_data = self.job_compatibility_analyzer.generate_compatibility_report(
                        tool_args["job_description"],
                        tool_args["report_language"],
                        tool_args["company_name"]
                    )

                    # --- PDF ---
                    pdf_bytes = self.pdf_generator.generate_pdf(
                        report_data["report_text"],
                        report_data["job_title"],
                        "Fatma Betül Arslan",
                        tool_args["report_language"],
                        report_data["company_name"]
                    )
                    file_name = f"job_report_{datetime.now():%Y%m%d_%H%M%S}.pdf"

                    # state’e sakla (isteğe bağlı)
                    st.session_state.last_compatibility_report = report_data["report_text"]
                    st.session_state.last_job_title            = report_data["job_title"]
                    st.session_state.last_company_name         = report_data["company_name"]
                    st.session_state.last_report_language      = tool_args["report_language"]

                    report_data.update({
                        "pdf_bytes": pdf_bytes,
                        "filename" : file_name
                    })
                    return {"success": True, "data": report_data}

                except Exception as e:
                    return {"success": False, "message": f"Analysis error: {e}"}

            # 3. Uyumluluk PDF'ini sonradan üret (isteğe bağlı yol) --------------
        elif tool_name == "generate_compatibility_pdf":
                report = st.session_state.get("last_compatibility_report")
                if not report:
                    return {"success": False, "message": "No report found. Run analysis first."}
                try:
                    pdf_bytes = self.pdf_generator.generate_pdf(
                        report,
                        st.session_state.get("last_job_title", "Unknown Position"),
                        "Fatma Betül Arslan",
                        st.session_state.get("last_report_language", "en"),
                        st.session_state.get("last_company_name", "Unknown Company")
                    )
                    filename = f"job_report_{datetime.now():%Y%m%d_%H%M%S}.pdf"
                    return {"success": True, "data": {"pdf_bytes": pdf_bytes, "filename": filename}}
                except Exception as e:
                    return {"success": False, "message": f"PDF error: {e}"}

            # 4. ÖN YAZI -----------------------------------------------------------
        elif tool_name == "generate_cover_letter":
                try:
                    # -- Metni üret
                    text = generate_cover_letter(
                        job_description = tool_args["job_description"],
                        cv_text         = tool_args["cv_text"],
                        language        = tool_args.get("language", "tr"),
                        company_name    = tool_args.get("company_name")
                    )

                    # -- PDF
                    pdf_bytes = self.pdf_generator.generate_pdf(
                        report_content=text,
                        candidate_name="Fatma Betül Arslan",
                        language=tool_args.get("language", "tr"),
                        company_name=tool_args.get("company_name", "Unknown Company"))
                    filename = f"cover_letter_{datetime.now():%Y%m%d_%H%M%S}.pdf"
                    
                    return {
                        "success": True,   
                        "data": {
                            "text"      : text,
                            "pdf_bytes" : pdf_bytes,
                            "filename"  : filename
                        }
                    }
                except Exception as e:
                    return {"success": False, "message": f"Cover letter error: {e}"}

            # 5. Bilinmeyen tool ---------------------------------------------------
        return {"success": False, "message": f"Unknown tool: {tool_name}"}

    # --------- Çift dilli rapor ----------
    
    def generate_bilingual_job_report(self, job_description, company_name="Unknown Company"):
        """
        Hem İngilizce hem Türkçe iş uyumluluk raporu üretir.
        Sonuç: {
            "english_report": ...,
            "turkish_report": ...,
            "metadata": {...}
        }
        """
        if not self.job_compatibility_analyzer:
            return {"error": "Job compatibility analyzer not initialized."}
        en_report = self.job_compatibility_analyzer.generate_compatibility_report(
            job_description, language="en", company_name=company_name
        )
        tr_report = self.job_compatibility_analyzer.generate_compatibility_report(
            job_description, language="tr", company_name=company_name
        )
        return {
            "english_report": en_report.get("report_text", ""),
            "turkish_report": tr_report.get("report_text", ""),
            "metadata": {
                "en": en_report.get("metadata", {}),
                "tr": tr_report.get("metadata", {})
            }
        }
