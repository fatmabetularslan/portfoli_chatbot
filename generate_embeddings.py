#!/usr/bin/env python3
"""
Local embedding generator script
Bu script CV verilerini okuyup embedding'leri hesaplar ve dosya olarak kaydeder.
Deploy sırasında API limiti olmayacak çünkü embedding'ler önceden hesaplanmış olacak.
"""

import json
import numpy as np
import pickle
import os
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - fallback for <3.11
    import tomli as tomllib  # type: ignore[import]


def _load_gemini_key():
    """
    Tries to find the Gemini API key from environment variables or
    .streamlit/secrets.toml so that embedding generation works outside Streamlit.
    """
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if key:
        return key.strip()

    secrets_path = Path(__file__).resolve().parent / ".streamlit" / "secrets.toml"
    if secrets_path.exists():
        try:
            with open(secrets_path, "rb") as f:
                secrets = tomllib.load(f)
            key = secrets.get("GEMINI_API_KEY") or secrets.get("GOOGLE_API_KEY")
            if key:
                return str(key).strip()
        except Exception as exc:  # pragma: no cover - strictly best-effort
            print(f"⚠️ secrets.toml okunurken hata: {exc}")
    return None


GEMINI_KEY = _load_gemini_key()
if not GEMINI_KEY:
    raise RuntimeError(
        "Gemini API anahtarı bulunamadı. Lütfen GOOGLE_API_KEY veya GEMINI_API_KEY "
        "ortam değişkenini ayarlayın ya da .streamlit/secrets.toml içinde tanımlayın."
    )

# google.generativeai kütüphanesi embed_content çağrılarında GOOGLE_API_KEY değişkenini arıyor.
os.environ["GOOGLE_API_KEY"] = GEMINI_KEY
os.environ.setdefault("GEMINI_API_KEY", GEMINI_KEY)

from google.generativeai.embedding import embed_content

def build_chunks(cv_json):
    """CV verilerini chunk'lara böler"""
    chunks = []
    
    for section, content in cv_json.items():
        if section in ['name', 'title', 'location', 'email', 'phone']:
            # Kişisel bilgileri tek chunk'ta birleştir
            if section == 'name':
                personal_info = f"Kişisel Bilgiler: {content}"
                if 'title' in cv_json:
                    personal_info += f" - {cv_json['title']}"
                if 'location' in cv_json:
                    personal_info += f" - {cv_json['location']}"
                chunks.append(personal_info)
        elif section == 'profile':
            chunks.append(f"Profil: {content}")
        elif section == 'education':
            # Eğitim bilgilerini tek chunk'ta birleştir
            edu_text = "Eğitim: "
            for edu in content:
                edu_text += f"{edu['institution']} - {edu['degree']} ({edu['years']}); "
            chunks.append(edu_text.strip())
        elif section == 'experience':
            # Her deneyimi ayrı chunk yap
            for exp in content:
                exp_text = f"Deneyim: {exp['title']} at {exp['company']} ({exp['duration']}) - {exp['description']}"
                chunks.append(exp_text)
        elif section == 'skills':
            # Yetenekleri kategorilere göre grupla
            for category, skills in content.items():
                skills_text = f"Yetenekler - {category}: {', '.join(skills)}"
                chunks.append(skills_text)
        elif section == 'projects':
            # Her projeyi ayrı chunk yap
            for project in content:
                if isinstance(project, dict):
                    proj_text = f"Proje: {project.get('name', '')} - {project.get('description', '')}"
                    chunks.append(proj_text)
        elif section == 'links':
            # Linkleri tek chunk'ta birleştir
            links_text = "Linkler: " + " | ".join([f"{k}: {v}" for k, v in content.items()])
            chunks.append(links_text)
        else:
            # Diğer bölümler için genel yaklaşım
            if isinstance(content, (str, int, float)):
                chunks.append(f"{section}: {content}")
    
    return chunks

def generate_embeddings(chunks, api_key=None):
    """Chunk'lar için embedding'leri hesapla"""
    print(f"🔄 {len(chunks)} chunk için embedding hesaplanıyor...")
    
    embeddings = []
    for i, chunk in enumerate(chunks):
        print(f"   📝 Chunk {i+1}/{len(chunks)}: {chunk[:50]}...")
        
        try:
            # Google API ile embedding hesapla
            result = embed_content(model="models/embedding-001", content=chunk)
            embedding = np.asarray(result["embedding"])
            embeddings.append(embedding)
            
            # Progress göster
            if (i + 1) % 5 == 0:
                print(f"   ✅ {i+1}/{len(chunks)} tamamlandı")
                
        except Exception as e:
            print(f"   ❌ Hata (chunk {i+1}): {str(e)}")
            # Sıfır vektör ekle (fallback)
            embeddings.append(np.zeros(768))
    
    print(f"✅ Tüm embedding'ler hesaplandı!")
    return np.vstack(embeddings)

def save_embeddings_data(chunks, embeddings, cv_json, output_file="embeddings_data.pkl"):
    """Embedding verilerini dosyaya kaydet"""
    data = {
        'chunks': chunks,
        'embeddings': embeddings,
        'cv_json': cv_json,
        'alias': {
            "deneyim": "experience", "tecrübe": "experience",
            "eğitim": "education",  "projeler": "projects",
            "ödüller": "awards",    "yetenek": "skills",
        }
    }
    
    with open(output_file, 'wb') as f:
        pickle.dump(data, f)
    
    print(f"💾 Embedding verileri '{output_file}' dosyasına kaydedildi")
    print(f"   📊 {len(chunks)} chunk, {embeddings.shape[0]}x{embeddings.shape[1]} embedding")

def main():
    """Ana fonksiyon"""
    print("🚀 Local Embedding Generator")
    print("=" * 50)
    
    # CV dosyasını oku
    cv_file = "betül-cv.json"
    if not os.path.exists(cv_file):
        print(f"❌ CV dosyası bulunamadı: {cv_file}")
        return
    
    print(f"📖 CV dosyası okunuyor: {cv_file}")
    with open(cv_file, 'r', encoding='utf-8') as f:
        cv_json = json.load(f)
    
    # Chunk'ları oluştur
    print("🔨 Chunk'lar oluşturuluyor...")
    chunks = build_chunks(cv_json)
    print(f"   📝 {len(chunks)} chunk oluşturuldu")
    
    # Embedding'leri hesapla
    embeddings = generate_embeddings(chunks)
    
    # Dosyaya kaydet
    save_embeddings_data(chunks, embeddings, cv_json)
    
    print("\n🎉 Tamamlandı!")
    print("📁 Şimdi bu dosyaları Streamlit Cloud'a upload edebilirsiniz:")
    print("   - embeddings_data.pkl")
    print("   - betül-cv.json")

if __name__ == "__main__":
    main()
