# Portfolio_AI_Chatbot

Bu proje daha önce Streamlit ile çalışıyordu. Aynı tasarım (CSS class isimleri korunarak) **React** tarafına taşındı.

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