from __future__ import annotations

import json
import os
import pickle
from pathlib import Path
from typing import Any, Literal

import numpy as np
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from dotenv import load_dotenv

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[import]

ROOT = Path(__file__).resolve().parent
CV_PATH = ROOT / "betül-cv.json"
EMBEDDINGS_PATH = ROOT / "embeddings_data.pkl"
SECRETS_PATH = ROOT / ".streamlit" / "secrets.toml"

# .env desteği (anahtar server-side kalmalı)
load_dotenv(ROOT / ".env")
load_dotenv(ROOT / "frontend" / ".env")


def _load_gemini_key() -> str | None:
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if key:
        return key.strip()
    if SECRETS_PATH.exists():
        try:
            with open(SECRETS_PATH, "rb") as f:
                secrets = tomllib.load(f)
            key = secrets.get("GEMINI_API_KEY") or secrets.get("GOOGLE_API_KEY")
            if key:
                return str(key).strip()
        except Exception:
            return None
    return None


GEMINI_KEY = _load_gemini_key()
if GEMINI_KEY:
    os.environ["GOOGLE_API_KEY"] = GEMINI_KEY
    os.environ.setdefault("GEMINI_API_KEY", GEMINI_KEY)

try:
    from google.generativeai.embedding import embed_content  # type: ignore
except Exception:  # pragma: no cover
    embed_content = None


def _load_cv() -> dict[str, Any]:
    with open(CV_PATH, encoding="utf-8") as f:
        return json.load(f)


def _load_embeddings() -> tuple[list[str], np.ndarray, np.ndarray]:
    """
    embeddings_data.pkl (generate_embeddings.py ile üretilen) formatı:
      {
        'chunks': [str, ...],
        'embeddings': np.ndarray (N x 768),
        'cv_json': {...},
        ...
      }
    """
    with open(EMBEDDINGS_PATH, "rb") as f:
        data = pickle.load(f)

    chunks = data.get("chunks") or []
    emb = np.asarray(data.get("embeddings"))
    if emb.ndim != 2:
        raise RuntimeError("embeddings_data.pkl beklenmeyen formatta (embeddings 2D değil).")
    norms = np.linalg.norm(emb, axis=1) + 1e-8
    return list(chunks), emb.astype(np.float32, copy=False), norms.astype(np.float32, copy=False)


CV_JSON: dict[str, Any] = _load_cv() if CV_PATH.exists() else {}
CHUNKS: list[str] = []
EMB: np.ndarray | None = None
EMB_NORMS: np.ndarray | None = None

if EMBEDDINGS_PATH.exists():
    CHUNKS, EMB, EMB_NORMS = _load_embeddings()


def _embed_query(text: str) -> np.ndarray | None:
    if not GEMINI_KEY or embed_content is None:
        return None
    try:
        vec = embed_content(model="models/embedding-001", content=text)["embedding"]
        return np.asarray(vec, dtype=np.float32)
    except Exception:
        return None


def rag_search(query: str, top_k: int = 5) -> list[str]:
    if EMB is None or EMB_NORMS is None or not CHUNKS:
        return [json.dumps(CV_JSON, ensure_ascii=False, indent=2)] if CV_JSON else []

    q = _embed_query(query.lower().strip())
    if q is None:
        # API anahtarı yoksa: basit fallback
        ql = query.lower()
        hits = [c for c in CHUNKS if any(tok in c.lower() for tok in ql.split() if len(tok) > 2)]
        return (hits[:top_k] if hits else CHUNKS[:top_k]) or []

    qn = float(np.linalg.norm(q) + 1e-8)
    sims = (EMB @ q) / (EMB_NORMS * qn)
    idx = np.argsort(sims)[-top_k:][::-1]
    return [CHUNKS[int(i)] for i in idx]


def gemini_generate(prompt: str) -> str:
    key = GEMINI_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        return "⚠️ Gemini API anahtarı bulunamadı (GEMINI_API_KEY / GOOGLE_API_KEY)."

    model = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        r = requests.post(f"{url}?key={key}", headers={"Content-Type": "application/json"}, json=payload, timeout=60)
        j = r.json()
        return j["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"⚠️ Gemini yanıtı alınamadı: {e}"


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[ChatMessage] = Field(default_factory=list)
    lang: Literal["tr", "en"] = "tr"


app = FastAPI(title="Portfolio AI Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_origins=[
        "https://portfoli-chatbot.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

# Statik dosyalar: URL'ler Streamlit ile aynı kalsın
assets_dir = ROOT / "assets"
fonts_dir = ROOT / "fonts"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
if fonts_dir.exists():
    app.mount("/fonts", StaticFiles(directory=str(fonts_dir)), name="fonts")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/api/cv")
def get_cv():
    return CV_JSON


@app.post("/api/chat")
def chat(req: ChatRequest):
    msg = req.message.strip()
    current_lang = req.lang

    recent = req.history[-6:] if len(req.history) > 6 else req.history
    history_text = "\n".join([f"{m.role}: {m.content}" for m in recent])

    retrieved = rag_search(msg, top_k=5)

    # Proje adı geçiyorsa bağlama ekle (Streamlit mantığına yakın)
    proj_blocks: list[str] = []
    msg_lower = msg.lower()
    for proj in (CV_JSON.get("projects") or []):
        if not isinstance(proj, dict):
            continue
        name = str(proj.get("name") or "").strip()
        if not name:
            continue
        if name.lower() in msg_lower:
            proj_blocks.append(
                "Proje Adı: {name}\nTeknolojiler: {tech}\nAçıklama: {desc}\nÖzellikler: {feat}".format(
                    name=name,
                    tech=proj.get("technology", ""),
                    desc=proj.get("description", ""),
                    feat=proj.get("features", ""),
                )
            )

    context_chunks = list(retrieved)
    if proj_blocks:
        context_chunks.append("Eşleşen Projeler:\n" + "\n\n".join(proj_blocks))

    context_text = "\n---\n".join(context_chunks)

    if current_lang == "tr":
        language_prompt = (
            "Sen Fatma Betül'ün AI portföy asistanısın. "
            "Sadece Türkçe cevap ver. İngilizce çeviri yapma. "
            "Kullanıcının sorusuna yanıt verirken aşağıdaki CV bağlamını kullan. "
            "Bağlamda bilgi yoksa bunu açıkça belirt ve uydurma."
        )
        context_label = "CV Bağlamı"
        question_label = "Kullanıcı Sorusu"
    else:
        language_prompt = (
            "You are Fatma Betül's AI portfolio assistant. "
            "Answer only in English. Do not provide Turkish translations. "
            "Use the CV context below. If the context lacks the answer, say so."
        )
        context_label = "CV Context"
        question_label = "User Question"

    prompt = (
        f"{language_prompt}\n\n"
        f"{context_label}:\n{context_text}\n\n"
        f"{question_label}:\n{msg}\n\n"
        f"Son sohbet geçmişi (referans için):\n{history_text}"
    )

    reply = gemini_generate(prompt).strip()
    return {"reply": reply}


if __name__ == "__main__":
    import uvicorn

    # Render/Railway gibi ortamlarda PORT env kullanılır.
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("api_server:app", host="0.0.0.0", port=port, reload=True)

