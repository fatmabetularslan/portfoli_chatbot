import { useEffect, useMemo, useRef, useState } from 'react'

type Lang = 'tr' | 'en'
type Theme = 'light' | 'dark'

type CvJson = {
  name?: string
  title?: string
  location?: string
  profile?: string
  email?: string
  links?: Record<string, string>
  education?: Array<{ institution?: string; degree?: string; years?: string }>
  experience?: Array<{ title?: string; company?: string; duration?: string; description?: string }>
  projects?: Array<{
    name?: string
    technology?: string
    description?: string | Record<string, string>
    features?: string[] | Record<string, string[]>
    github?: string
  }>
  skills?: Record<string, string[]>
  awards?: Array<{ name?: string; organization?: string; description?: string }>
  medium_articles?: Array<{ title?: string; url?: string; summary_tr?: string; summary_en?: string }>
  references?: Array<{ name?: string; title?: string; organization?: string }>
}

function getStored<T>(key: string, fallback: T): T {
  try {
    const v = localStorage.getItem(key)
    return v ? (JSON.parse(v) as T) : fallback
  } catch {
    return fallback
  }
}

function setStored<T>(key: string, value: T) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch {
    // ignore
  }
}

function scrollToId(id: string) {
  const el = document.getElementById(id)
  if (!el) return
  const offset = 70
  const rectTop = el.getBoundingClientRect().top
  const top = rectTop + window.pageYOffset - offset
  window.scrollTo({ top, behavior: 'smooth' })
}

function pickLocalized<T>(val: T | Record<string, T> | undefined, lang: Lang, fallbackLang: Lang = 'en'): T | undefined {
  if (val == null) return undefined
  if (typeof val === 'object' && !Array.isArray(val)) {
    const obj = val as Record<string, T>
    return obj[lang] ?? obj[fallbackLang] ?? obj.tr ?? obj.en
  }
  return val as T
}

export default function App() {
  const [lang, setLang] = useState<Lang>(() => getStored('lang', 'tr'))
  const [theme, setTheme] = useState<Theme>(() => getStored('theme', 'light'))
  const [cv, setCv] = useState<CvJson | null>(null)
  const [profileImgOk, setProfileImgOk] = useState(true)

  useEffect(() => {
    setStored('lang', lang)
  }, [lang])

  useEffect(() => {
    setStored('theme', theme)
  }, [theme])

  useEffect(() => {
    ;(async () => {
      try {
        const r = await fetch('/api/cv')
        if (!r.ok) throw new Error('api cv failed')
        const data = (await r.json()) as CvJson
        setCv(data)
        return
      } catch {
        // API yoksa (sadece frontend çalışıyorsa) public içindeki dosyadan oku
        try {
          const r2 = await fetch('/betul-cv.json')
          if (!r2.ok) throw new Error('public cv failed')
          const data2 = (await r2.json()) as CvJson
          setCv(data2)
        } catch {
          setCv(null)
        }
      }
    })()
  }, [])

  const navTexts = useMemo(
    () => ({
      tr: {
        home: 'Ana Sayfa',
        about: 'Hakkımda',
        experience: 'Deneyim',
        projects: 'Projeler',
        skills: 'Yetenekler',
        awards: 'Ödüller',
        articles: 'Yazılar',
        references: 'Referanslar',
        contact: 'İletişim',
      },
      en: {
        home: 'Home',
        about: 'About',
        experience: 'Experience',
        projects: 'Projects',
        skills: 'Skills',
        awards: 'Awards',
        articles: 'Articles',
        references: 'References',
        contact: 'Contact',
      },
    }),
    [],
  )

  const texts = navTexts[lang]

  const name = cv?.name ?? 'Fatma Betül Arslan'
  const title = cv?.title ?? 'Veri Bilimci'

  const allowedProjects = useMemo(
    () => new Set(['AI-Powered Portfolio Chatbot', 'FinTurk Finansal Asistan', 'Customer Churn Prediction', 'Energy Consumption Prediction API']),
    [],
  )

  const featuredProjects = useMemo(() => {
    const projects = cv?.projects ?? []
    return projects.filter((p) => p?.name && allowedProjects.has(p.name))
  }, [cv, allowedProjects])

  const [chatOpen, setChatOpen] = useState(false)
  const [chatInput, setChatInput] = useState('')
  const [chatMessages, setChatMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>(() => [])
  const [chatLoading, setChatLoading] = useState(false)
  const chatBodyRef = useRef<HTMLDivElement | null>(null)
  const chatBottomRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setChatOpen(false)
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [])

  // Yeni mesaj gelince (veya panel açılınca) en alta kaydır
  useEffect(() => {
    if (!chatOpen) return
    const bottom = chatBottomRef.current
    if (!bottom) return
    // layout tamamlandıktan sonra kaydır
    requestAnimationFrame(() => bottom.scrollIntoView({ block: 'end' }))
  }, [chatOpen, chatMessages.length, chatLoading])

  async function sendChat() {
    const msg = chatInput.trim()
    if (!msg || chatLoading) return
    setChatInput('')
    const next = [...chatMessages, { role: 'user' as const, content: msg }]
    setChatMessages(next)
    setChatLoading(true)
    try {
      const resp = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, history: next, lang }),
      })
      const data = await resp.json()
      setChatMessages((prev) => [...prev, { role: 'assistant', content: data?.reply ?? '' }])
    } catch {
      setChatMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: lang === 'tr' ? '⚠️ Yanıt alınamadı. Sunucu çalışıyor mu?' : '⚠️ Could not get a response. Is the server running?',
        },
      ])
    } finally {
      setChatLoading(false)
    }
  }

  return (
    <div className="stApp" data-theme={theme}>
      <div className="background-shapes">
        <div className="blob-1" />
        <div className="blob-2" />
        <div className="wave-shape" />
        <div className="bottom-wave" />
        <div className="bottom-blob" />
      </div>

      <div className="nav-menu">
        <div className="nav-menu-content">
          <div className="nav-menu-links">
            <a
              href="#"
              className="nav-link"
              onClick={(e) => {
                e.preventDefault()
                window.scrollTo({ top: 0, behavior: 'smooth' })
              }}
            >
              {texts.home}
            </a>
            <a
              href="#about"
              className="nav-link"
              onClick={(e) => {
                e.preventDefault()
                scrollToId('about')
              }}
            >
              {texts.about}
            </a>
            <a
              href="#experience"
              className="nav-link"
              onClick={(e) => {
                e.preventDefault()
                scrollToId('experience')
              }}
            >
              {texts.experience}
            </a>
            <a
              href="#projects"
              className="nav-link"
              onClick={(e) => {
                e.preventDefault()
                scrollToId('projects')
              }}
            >
              {texts.projects}
            </a>
            <a
              href="#skills"
              className="nav-link"
              onClick={(e) => {
                e.preventDefault()
                scrollToId('skills')
              }}
            >
              {texts.skills}
            </a>
            <a
              href="#awards"
              className="nav-link"
              onClick={(e) => {
                e.preventDefault()
                scrollToId('awards')
              }}
            >
              {texts.awards}
            </a>
            <a
              href="#articles"
              className="nav-link"
              onClick={(e) => {
                e.preventDefault()
                scrollToId('articles')
              }}
            >
              {texts.articles}
            </a>
            <a
              href="#references"
              className="nav-link"
              onClick={(e) => {
                e.preventDefault()
                scrollToId('references')
              }}
            >
              {texts.references}
            </a>
            <a
              href="#contact"
              className="nav-link"
              onClick={(e) => {
                e.preventDefault()
                scrollToId('contact')
              }}
            >
              {texts.contact}
            </a>
          </div>
          <div className="nav-menu-toggles">
            <button className={`nav-toggle-btn ${lang === 'en' ? 'selected' : ''}`} onClick={() => setLang('en')} title="English" type="button">
              EN
            </button>
            <button className={`nav-toggle-btn ${lang === 'tr' ? 'selected' : ''}`} onClick={() => setLang('tr')} title="Türkçe" type="button">
              🇹🇷
            </button>
            <button className={`nav-toggle-btn ${theme === 'light' ? 'selected' : ''}`} onClick={() => setTheme('light')} title="Light Mode" type="button">
              ☀️
            </button>
            <button className={`nav-toggle-btn ${theme === 'dark' ? 'selected' : ''}`} onClick={() => setTheme('dark')} title="Dark Mode" type="button">
              🌙
            </button>
          </div>
        </div>
      </div>

      <div className="main-content">
        <div className="hero-section">
          {profileImgOk ? (
            <img
              src="/assets/vesika.jpg"
              alt={name}
              className="hero-profile-img"
              onError={() => setProfileImgOk(false)}
            />
          ) : (
            <div
              className="hero-profile-img"
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '3rem',
                fontWeight: 700,
              }}
            >
              {name?.[0] ?? 'F'}
            </div>
          )}
          <h1 className="hero-name">{name}</h1>
          <h2 className="hero-title">{title}</h2>
          <a href="/Fatma-Betul-ARSLAN-CV.pdf" download className="download-cv-btn">
            📥 Download CV
          </a>
          <div className="social-links">
            <a href="https://github.com/fatmabetularslan" target="_blank" rel="noreferrer">
              <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg" alt="GitHub" />
            </a>
            <a href="https://www.linkedin.com/in/fatma-betül-arslan" target="_blank" rel="noreferrer">
              <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linkedin/linkedin-original.svg" alt="LinkedIn" />
            </a>
            <a href="mailto:betularsln01@gmail.com" target="_blank" rel="noreferrer">
              <img src="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/gmail.svg" alt="Mail" />
            </a>
          </div>
        </div>

        <div className="portfolio-section" id="about">
          <h2 className="section-title">{lang === 'tr' ? '📖 Hakkımda' : '📖 About Me'}</h2>
          {cv?.profile ? <div className="about-content">{cv.profile}</div> : null}
          {cv?.education?.[0]?.institution ? (
            <p style={{ textAlign: 'center', color: '#3b5bdb', fontWeight: 500, marginTop: 20, fontSize: '1.25em' }}>
              🎓 {cv.education[0].institution}
            </p>
          ) : null}
        </div>

        <div className="portfolio-section" id="experience">
          <h2 className="section-title">{lang === 'tr' ? '💼 Deneyim & Eğitim' : '💼 Experience & Education'}</h2>

          {(cv?.experience ?? []).map((exp, i) => (
            <div className="experience-card" key={`exp-${i}`}>
              <div className="experience-title">{exp.title}</div>
              <div className="experience-company">{exp.company}</div>
              <div className="experience-duration">{exp.duration}</div>
              <div className="experience-description">{exp.description}</div>
            </div>
          ))}

          {(cv?.education ?? []).map((edu, i) => (
            <div className="education-card" key={`edu-${i}`}>
              <div className="education-title">{edu.degree}</div>
              <div className="education-institution">{edu.institution}</div>
              <div className="education-years">{edu.years}</div>
            </div>
          ))}
        </div>

        <div className="portfolio-section" id="projects">
          <h2 className="section-title">{lang === 'tr' ? '🚀 Öne Çıkan Projeler' : '🚀 Featured Projects'}</h2>
          <div className="projects-grid">
            {featuredProjects.map((proj, i) => {
              const description = pickLocalized<string>(proj.description as any, lang, 'en') ?? ''
              const features = pickLocalized<string[]>(proj.features as any, lang, 'en') ?? []
              const featuresHtml = Array.isArray(features) && features.length ? (
                <div className="project-features">
                  {features.map((f, idx) => (
                    <div className="project-feature" key={`feat-${i}-${idx}`}>
                      {f}
                    </div>
                  ))}
                </div>
              ) : null
              const linkText = lang === 'tr' ? "🔗 GitHub'da Görüntüle" : '🔗 View on GitHub'
              return (
                <div className="project-card" key={`proj-${i}`}>
                  <div className="project-name">{proj.name}</div>
                  <div className="project-tech">{proj.technology}</div>
                  <div className="project-description">{description}</div>
                  {featuresHtml}
                  {proj.github ? (
                    <a className="project-link" href={proj.github} target="_blank" rel="noreferrer">
                      {linkText}
                    </a>
                  ) : null}
                </div>
              )
            })}
          </div>
        </div>

        <div className="portfolio-section" id="skills">
          <h2 className="section-title">{lang === 'tr' ? '🛠️ Yetenekler' : '🛠️ Skills'}</h2>
          <div className="skills-container">
            {cv?.skills
              ? Object.entries(cv.skills).map(([category, list]) => (
                  <div className="skill-category" key={category}>
                    <div className="skill-category-title">{category}</div>
                    <div>
                      {(list ?? []).map((s) => (
                        <span className="skill-tag" key={`${category}-${s}`}>
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                ))
              : null}
          </div>
        </div>

        <div className="portfolio-section" id="awards">
          <h2 className="section-title">{lang === 'tr' ? '🏆 Ödüller' : '🏆 Awards & Achievements'}</h2>
          {(cv?.awards ?? []).map((a, i) => (
            <div className="award-card" key={`award-${i}`}>
              <div className="award-name">{a.name}</div>
              <div className="award-org">{a.organization}</div>
              <div className="award-description">{a.description}</div>
            </div>
          ))}
        </div>

        <div className="portfolio-section" id="articles">
          <h2 className="section-title">{lang === 'tr' ? '📝 Son Yazılar' : '📝 Latest Articles'}</h2>
          {cv?.medium_articles?.length ? (
            <div className="articles-grid">
              {cv.medium_articles.slice(0, 5).map((a, i) => {
                const summary = lang === 'tr' ? a.summary_tr : a.summary_en
                return (
                  <div className="article-card" key={`art-${i}`}>
                    <div className="article-title">{a.title}</div>
                    <div className="article-summary">{summary}</div>
                    <a className="article-link" href={a.url} target="_blank" rel="noreferrer">
                      📖 Read on Medium
                    </a>
                  </div>
                )
              })}
            </div>
          ) : (
            <p style={{ textAlign: 'center', color: '#64748b' }}>{lang === 'tr' ? 'Yazı bulunamadı.' : 'No articles available.'}</p>
          )}
        </div>

        <div className="portfolio-section" id="references">
          <h2 className="section-title">{lang === 'tr' ? '📞 Referanslar' : '📞 References'}</h2>
          <div className="reference-list">
            {(cv?.references ?? []).map((r, i) => (
              <div className="reference-card" key={`ref-${i}`}>
                <div className="reference-name">{r.name}</div>
                <div className="reference-title">{r.title}</div>
                <div className="reference-org">{r.organization}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="portfolio-section" id="contact">
          <h2 className="section-title">{lang === 'tr' ? '📧 İletişim' : '📧 Get In Touch'}</h2>
          <div style={{ textAlign: 'center', maxWidth: 600, margin: '0 auto' }}>
            <p style={{ fontSize: '1.15em', lineHeight: 1.8, color: '#475569', marginBottom: 30 }}>
              {lang === 'tr'
                ? 'Yeni fırsatlar ve işbirlikleri hakkında konuşmak için benimle iletişime geçebilirsiniz. E-posta veya LinkedIn üzerinden bana ulaşabilirsiniz.'
                : "I'm always interested in hearing about new opportunities and collaborations. Feel free to reach out via email or LinkedIn."}
            </p>
            <div style={{ display: 'flex', justifyContent: 'center', gap: 20, flexWrap: 'wrap' }}>
              <a
                href={`mailto:${cv?.email ?? ''}`}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                  color: '#3b5bdb',
                  textDecoration: 'none',
                  fontWeight: 500,
                  padding: '10px 20px',
                  border: '2px solid #3b5bdb',
                  borderRadius: 8,
                  transition: 'all 0.2s',
                }}
              >
                📧 Mail Me
              </a>
              <a
                href={cv?.links?.linkedin ?? '#'}
                target="_blank"
                rel="noreferrer"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                  color: '#3b5bdb',
                  textDecoration: 'none',
                  fontWeight: 500,
                  padding: '10px 20px',
                  border: '2px solid #3b5bdb',
                  borderRadius: 8,
                  transition: 'all 0.2s',
                }}
              >
                💼 LinkedIn
              </a>
              <a
                href={cv?.links?.github ?? '#'}
                target="_blank"
                rel="noreferrer"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                  color: '#3b5bdb',
                  textDecoration: 'none',
                  fontWeight: 500,
                  padding: '10px 20px',
                  border: '2px solid #3b5bdb',
                  borderRadius: 8,
                  transition: 'all 0.2s',
                }}
              >
                🔗 GitHub
              </a>
              <a
                href={cv?.links?.medium ?? '#'}
                target="_blank"
                rel="noreferrer"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                  color: '#3b5bdb',
                  textDecoration: 'none',
                  fontWeight: 500,
                  padding: '10px 20px',
                  border: '2px solid #3b5bdb',
                  borderRadius: 8,
                  transition: 'all 0.2s',
                }}
              >
                ✍️ Medium
              </a>
            </div>
          </div>
        </div>
      </div>

      <div id="floating-chat-root">
        <button id="floating-chat-launcher" type="button" onClick={() => setChatOpen((v) => !v)}>
          <span>{lang === 'tr' ? 'AI Asistanına sor!' : 'Ask the AI assistant!'}</span>
          <div className="icon">🤖</div>
        </button>
        <div id="floating-chat-panel" className={chatOpen ? 'is-visible' : ''}>
          <header>
            <div>{lang === 'tr' ? 'AI Portföy Asistanı' : 'AI Portfolio Assistant'}</div>
            <button id="floating-chat-close" aria-label="Kapat" type="button" onClick={() => setChatOpen(false)}>
              ×
            </button>
          </header>

          <div className="chat-body" ref={chatBodyRef}>
            {chatMessages.length === 0 ? (
              <div className="chat-empty">
                {lang === 'tr'
                  ? "Merhaba! CV, projeler ve deneyimlerle ilgili soru sorabilirsin."
                  : "Hi! Ask anything about the CV, projects, and experience."}
              </div>
            ) : null}

            {chatMessages.map((m, i) => (
              <div key={`m-${i}`} className={`chat-msg ${m.role}`}>
                <div className="chat-msg-bubble">{m.content}</div>
              </div>
            ))}

            {chatLoading ? <div className="chat-loading">{lang === 'tr' ? 'Yanıt oluşturuluyor…' : 'Generating…'}</div> : null}
            <div ref={chatBottomRef} />
          </div>

          <div className="chat-input-row">
            <input
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder={lang === 'tr' ? 'Mesajınızı yazın…' : 'Type your message…'}
              onKeyDown={(e) => {
                if (e.key === 'Enter') void sendChat()
              }}
            />
            <button type="button" onClick={() => void sendChat()} disabled={chatLoading}>
              {lang === 'tr' ? 'Gönder' : 'Send'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

