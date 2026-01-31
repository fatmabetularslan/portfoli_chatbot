import os
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
from tools.gemini_tool import ask_gemini


class EmailTool:
    """SMTP email functionality"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_user = st.secrets.get("GMAIL_EMAIL", os.getenv("GMAIL_EMAIL"))
        self.email_password = st.secrets.get("GMAIL_APP_PASSWORD", os.getenv("GMAIL_APP_PASSWORD"))
        self.recipient_email = st.secrets.get("RECIPIENT_EMAIL", os.getenv("RECIPIENT_EMAIL"))
        self.linkedin_url = "https://www.linkedin.com/in/fatma-bet%C3%BCl-arslan/"
            
    def _send_confirmation_email(self, sender_email: str, sender_name: str, language: str = "en"):
        """Send confirmation email to the sender with HTML formatting"""
        try:
            profile_pic_url = "https://media.licdn.com/dms/image/v2/D4D03AQFQZ78NewBFGw/profile-displayphoto-shrink_800_800/profile-displayphoto-shrink_800_800/0/1723736388388?e=1756944000&v=beta&t=yYVphvX6ZZTHEdZaPZcbwB3I00xeHJ6eGTt-ajXRvJM"
            # Email content based on language
            if language == "tr":
                subject = "✅ Mesajınız Alındı - Fatma Betül Arslan"
                greeting = f"Merhaba {sender_name},"
                main_text = """
                Portföy chatbotum aracılığıyla gönderdiğiniz mesajınızı aldım. En kısa sürede size geri dönüş yapacağım.
                """
                urgent_text = """
                Eğer acil bir durum varsa, benimle LinkedIn üzerinden iletişime geçebilirsiniz.
                """
                disclaimer = """
                Eğer böyle bir e-posta beklemiyorsanız, birisi yanlışlıkla sizin e-posta adresinizi girmiş olabilir. 
                Lütfen bu mesajı görmezden gelin.
                """
                closing = "Sevgiler,"
                linkedin_text = "LinkedIn'de Bağlan"
                website_text = "Kişisel Website"
                
            else:  # English
                subject = "✅ Your Message Has Been Received - Fatma Betül ARSLAN"
                greeting = f"Hi {sender_name},"
                main_text = """
                I've received your message sent through my portfolio chatbot. I'll get back to you as soon as possible.
                """
                urgent_text = """
                If this is urgent, you can contact me directly on LinkedIn.
                """
                disclaimer = """
                If you did not expect this email, someone may have entered your email address by mistake. 
                Please ignore this message.
                """
                closing = "Best regards,"
                linkedin_text = "Connect on LinkedIn"
                website_text = "Personal Website"

            # HTML email template
            html_body = f"""
            <!DOCTYPE html>
            <html lang="{'tr' if language == 'tr' else 'en'}">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{subject}</title>
            </head>
            <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    
                    <!-- Header -->
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center; color: white;">
                        <div style="margin-bottom: 20px;">
                            <img src="{profile_pic_url}" 
                                alt="Fatma Betül ARSLAN" 
                                style="width: 80px; height: 80px; border-radius: 50%; border: 4px solid rgba(255,255,255,0.8); object-fit: cover;">
                        </div>
                        <h1 style="margin: 0; font-size: 24px; font-weight: 600;">SFatma Betül ARSLAN</h1>
                        <p style="margin: 5px 0 0 0; font-size: 16px; opacity: 0.9;">AI Engineer & Researcher</p>
                    </div>
                    
                    <!-- Content -->
                    <div style="padding: 40px 30px;">
                        <div style="margin-bottom: 30px;">
                            <h2 style="color: #333; font-size: 20px; margin-bottom: 15px;">
                                {greeting}
                            </h2>
                            <p style="color: #555; font-size: 16px; margin-bottom: 20px;">
                                {main_text}
                            </p>
                            <p style="color: #555; font-size: 16px; margin-bottom: 20px;">
                                {urgent_text}
                            </p>
                        </div>
                        
                        <!-- Contact Links -->
                        <div style="margin: 30px 0; text-align: center;">
                            <div style="display: inline-block; margin: 0 10px;">
                                <a href="{self.linkedin_url}" 
                                style="display: inline-block; background-color: #0077b5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 25px; font-weight: 500; transition: background-color 0.3s;">
                                    🔗 {linkedin_text}
                                </a>
                            </div>
                            <div style="display: inline-block; margin: 0 10px;">
                                <a href="https://github.com/fatmabetularslan" 
                                style="display: inline-block; background-color: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 25px; font-weight: 500; transition: background-color 0.3s;">
                                    🌐 {website_text}
                                </a>
                            </div>
                        </div>
                        
                        <!-- Contact Info -->
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; margin: 20px 0;">
                            <h3 style="color: #333; font-size: 16px; margin-bottom: 10px;">📧 Contact Information</h3>
                            <p style="color: #666; margin: 5px 0; font-size: 14px;">
                                <strong>Email:</strong> betularsln01@gmail.com
                            </p>
                            <p style="color: #666; margin: 5px 0; font-size: 14px;">
                                <strong>LinkedIn:</strong> <a href="{self.linkedin_url}" style="color: #0077b5; text-decoration: none;">{self.linkedin_url}</a>
                            </p>
                            <p style="color: #666; margin: 5px 0; font-size: 14px;">
                                <strong>Website:</strong> <a href="https://github.com/fatmabetularslan" style="color: #28a745; text-decoration: none;">https://github.com/fatmabetularslan</a>
                            </p>
                        </div>
                        
                        <div style="margin-top: 30px;">
                            <p style="color: #333; font-size: 16px; margin-bottom: 10px;">
                                {closing}
                            </p>
                            <p style="color: #667eea; font-weight: 600; font-size: 16px;">
                                Fatma Betül ARSLAN
                            </p>
                        </div>
                    </div>
                    
                    <!-- Footer -->
                    <div style="background-color: #f8f9fa; padding: 20px 30px; border-top: 1px solid #e9ecef;">
                        <p style="color: #6c757d; font-size: 12px; margin: 0; text-align: center;">
                            {disclaimer}
                        </p>
                        <p style="color: #6c757d; font-size: 12px; margin: 10px 0 0 0; text-align: center;">
                            This email was automatically sent by the AI Portfolio Assistant.
                        </p>
                    </div>
                    
                </div>
            </body>
            </html>
            """

            # Create confirmation message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_user or ""
            msg['To'] = sender_email or ""
            msg['Subject'] = subject or ""
            
            # Create plain text version as fallback
            plain_text = f"""
    {greeting}

    {main_text}

    {urgent_text}

    {closing}

    Fatma Betül ARSLAN
    
    AI Engineer & Researcher

    Email: betularsln01@gmail.com
    LinkedIn: {self.linkedin_url}
    Website: https://github.com/fatmabetularslan

    {disclaimer}
            """
            
            # Attach both plain text and HTML versions
            text_part = MIMEText(plain_text, 'plain', 'utf-8')
            html_part = MIMEText(html_body, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send confirmation email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user or "", self.email_password or "")
            server.sendmail(self.email_user or "", sender_email or "", msg.as_string())
            server.quit()
            
        except Exception as e:
            print(f"Failed to send confirmation email: {str(e)}")
    def send_email(self, sender_name: str, sender_email: str, subject: str, message: str) -> Dict[str, Any]:
        """Send email via SMTP"""
        try:
            # Debug info
            print(f"SMTP Server: {self.smtp_server}")
            print(f"SMTP Port: {self.smtp_port}")
            print(f"Email User: {self.email_user}")
            print(f"Recipient: {self.recipient_email}")
            
            # Create main message
            msg = MIMEMultipart()
            msg['From'] = self.email_user or ""
            msg['To'] = self.recipient_email or ""
            msg['Subject'] = subject
            msg['Reply-To'] = sender_email
            
            # Email body
            body = f"""
New contact from portfolio chatbot:

From: {sender_name}
Email: {sender_email}

Message:
{message}

---
Sent via Portfolio RAG Chatbot
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send main email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.set_debuglevel(1)
            server.starttls()
            server.login(self.email_user or "", self.email_password or "")
            
            text = msg.as_string()
            server.sendmail(self.email_user or "", self.recipient_email or "", text)
            server.quit()
            
            # Detect language from message (simple check for Turkish characters)
            language = "tr" if any(char in message.lower() for char in ['ç', 'ğ', 'ı', 'ö', 'ş', 'ü']) else "en"
            
            # Send confirmation email
            self._send_confirmation_email(sender_email, sender_name, language)
            
            # Clear CAPTCHA after successful send
            if 'email_captcha' in st.session_state:
                del st.session_state.email_captcha
            
            return {
                "success": True,
                "message": f"Email sent successfully to {self.recipient_email}! Fatma Betül  will get back to you soon."
            }
            
        except smtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "message": "Email authentication failed. Please check GMAIL_EMAIL and GMAIL_APP_PASSWORD (use App Password for Gmail)."
            }
        except smtplib.SMTPException as e:
            return {
                "success": False,
                "message": f"SMTP error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to send email: {str(e)}"
            }

    def generate_cover_letter(self, job_description: str, cv_text: str) -> str:
        """
        İş ilanı ve CV'ye göre Türkçe, kişiselleştirilmiş bir cover letter üretir.
        """
        prompt = f"""
Ben Fatma Betül Arslan'ın yapay zeka asistanıyım. Aşağıdaki iş ilanı ve CV bilgilerine göre, ilgili şirkete başvuru için profesyonel, etkileyici ve kişiselleştirilmiş bir ön yazı (cover letter) hazırla. Yazının başında 'Ben Fatma Betül Arslan'ın yapay zeka asistanıyım.' cümlesiyle başla. Yazı tamamen Türkçe ve özgün olsun.

İş İlanı:
{job_description}

CV:
{cv_text}
"""
        return ask_gemini(prompt)
        # Burada ask_gemini fonksiyonu tanımlı değil. Gerekirse ilgili fonksiyonu import edin veya bu satırı kendi Gemini API çağrınıza göre düzenleyin.
        #return ""