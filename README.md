# Portfolio_AI_Chatbot

Bu proje daha önce Streamlit ile çalışıyordu. Aynı tasarım (CSS class isimleri korunarak) **React** tarafına taşındı.

## Proje yapısı

- **Frontend (React)**: `frontend/`
- **Backend (FastAPI)**: `api_server.py` (+ `tools/`, `rag_system.py`, `betül-cv.json`, `embeddings_data.pkl`)
- **Legacy Streamlit** (artık zorunlu değil): `legacy_streamlit/`

## Çalıştırma

### 1) API (FastAPI)

- **Gerekli**: `GEMINI_API_KEY` veya `GOOGLE_API_KEY`
  - Ortam değişkeni olarak verebilirsin **veya**
  - `.streamlit/secrets.toml` içine koyabilirsin (Streamlit’teki gibi).

Kurulum:

```bash
pip install -r requirements.txt
```

Çalıştırma:

```bash
python api_server.py
```

API şunları sağlar:
- `GET /api/cv` → CV JSON
- `POST /api/chat` → RAG + Gemini cevap
- `/assets/*` ve `/fonts/*` → statik dosyalar (React aynı URL’leri kullanır)

### 2) Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Vite dev server, `vite.config.ts` ile `/api`, `/assets`, `/fonts` isteklerini otomatik olarak `http://localhost:8000` adresine proxy’ler.

## Deploy

### Backend (Render)

- Render → **New** → **Web Service** → GitHub repo seç
- **Root Directory**: boş (repo kökü)
- **Build Command**:

```bash
pip install -r requirements.txt
```

- **Start Command**:

```bash
uvicorn api_server:app --host 0.0.0.0 --port 10000
```

> İstersen Render’ın verdiği portu otomatik kullanmak için `--port $PORT` da kullanabilirsin.

- **Environment variables**:
  - `GEMINI_API_KEY` (veya `GOOGLE_API_KEY`)

- Deploy sonrası sağlık kontrolü:
  - `https://<render-url>/health` → `{"ok":true}`

### Frontend (Vercel)

Backend ayrıysa Vercel’de Environment’a şunu ekle:

- `VITE_API_BASE_URL = https://<render-url>`