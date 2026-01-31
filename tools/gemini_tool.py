import requests
import streamlit as st
import os

# ✅ API anahtarını Streamlit secrets üzerinden al
api_key = st.secrets["GEMINI_API_KEY"]

# -----------------------------------
# Genel amaçlı Gemini API fonksiyonu
# -----------------------------------
def ask_gemini(prompt: str) -> str:
    model = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(f"{url}?key={api_key}", headers=headers, json=data)
    resp_json = response.json()

    try:
        return resp_json["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"⚠️ Gemini yanıtı alınırken hata oluştu: {str(e)}\n\nYanıt: {resp_json}"

# -----------------------------------
# Ön Yazı (Cover Letter) Üretici
# -----------------------------------


def generate_cover_letter(
    *, job_description: str, cv_text, language: str = "tr", company_name: str | None = None
) -> str:
    # -- cv_text liste geldiyse string’e çevir
    if isinstance(cv_text, list):
        cv_text = "\n".join(cv_text)

    # -- prompt
    if language == "tr":
        company_line = f"Şirket Adı: {company_name}\n" if company_name else \
                       "# Şirket adını iş ilanından otomatik çıkar.\n"
        prompt = f"""
Aşağıdaki **iş ilanı** ve **CV** bilgilerini kullanarak; tamamen Türkçe,
profesyonel ve özgün bir ön yazı yaz.

{company_line}
İş İlanı:
{job_description.strip()}

CV Bilgileri:
{cv_text.strip()}

# Kurallar
- 2000 kelimeyi geçmesin
- Köşeli parantezli şablon ifadeler bırakma
"""
    else:
        company_line = f"Company: {company_name}\n" if company_name else \
                       "# Extract company & position from the job description.\n"
        prompt = f"""
Using the **job description** and **CV** below, craft a UNIQUE English cover letter.

{company_line}
Job Description:
{job_description.strip()}

CV Details:
{cv_text.strip()}

# Rules
- Max 2000 words
- Do NOT leave placeholders like [Company]
"""

    # -- Gemini Flash API
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.95,
            "maxOutputTokens": 2000
        }
        #  !! safetySettings gönderilmez
    }

    resp = requests.post(
        f"{url}?key={api_key}",
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=60
    )
    resp.raise_for_status()                 # 400/401/403 ise Exception fırlatır
    text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    if language == "tr":
        # Teşekkür cümlesini bul ve sonrasına AI notunu ekle
        tesekkur = "Zamanınız ve dikkatiniz için teşekkür ederim."
        if tesekkur in text:
            parts = text.split(tesekkur, 1)
            text = parts[0] + tesekkur + "\n\nBu mektup, kendi geliştirdiğim AI portföy asistanı tarafından derlenmiştir.\n\nSaygılarımla,\nFatma Betül Arslan"
        else:
            text = text.lstrip() + "\n\nBu mektup, kendi geliştirdiğim AI portföy asistanı tarafından derlenmiştir.\n\nSaygılarımla,\nFatma Betül Arslan"
    else:
        thanks = "Thank you for your time and consideration."
        if thanks in text:
            parts = text.split(thanks, 1)
            text = parts[0] + thanks + "\n\nThis letter was compiled by my self-developed AI portfolio assistant.\n\nSincerely,\nFatma Betül Arslan"
        else:
            text = text.lstrip() + "\n\nThis letter was compiled by my self-developed AI portfolio assistant.\n\nSincerely,\nFatma Betül Arslan"
    return text

# -----------------------------------
# (Opsiyonel test): API modellerini yazdır
# -----------------------------------
if __name__ == "__main__":
    test_url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
    response = requests.get(test_url)
    print("📌 Kullanılabilir Gemini modelleri:")
    print(response.json())
