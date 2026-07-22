

import streamlit as st
import google.generativeai as genai
import urllib.parse
import time
from PIL import Image
import io
import base64

# Sayfa Ayarları
st.set_page_config(
    page_title="Berko AI Studio",
    page_icon="💻",
    layout="centered"
)

# --- ÖZEL MODERN CSS VE CHAT BALONLARI ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #1e1e2f;
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    .stButton button {
        border-radius: 8px;
        border: 1px solid #4a4a6a;
        background-color: #2b2b40;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #3b3b5c;
        border-color: #6c6c96;
    }

    /* Kullanıcı Balonu (Sağda şık gri yuvarlak kutu) */
    .user-bubble {
        background-color: #f0f2f6;
        color: #111111;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        max-width: 75%;
        margin-left: auto;
        margin-bottom: 10px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        font-size: 15px;
        word-wrap: break-word;
    }

    /* Berko Balonu / Akışı (Solda düz yazı) */
    .berko-response {
        background-color: transparent;
        color: inherit;
        padding: 8px 0px;
        max-width: 85%;
        margin-right: auto;
        margin-bottom: 15px;
        font-size: 15px;
        word-wrap: break-word;
    }

    /* Düşünüyor animasyon yazısı */
    .thinking-text {
        color: #888888;
        font-style: italic;
        font-size: 14px;
        margin-bottom: 15px;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { opacity: 0.4; }
        50% { opacity: 1; }
        100% { opacity: 0.4; }
    }

    /* Artı butonunu input kutusu ile dikeyde ortala */
    [data-testid="column"]:has(button[kind="secondary"]) {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        padding-top: 24px;
    }
    </style>
""", unsafe_allow_html=True)

# --- GİRİŞ & OTURUM SİMÜLASYONU ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = None

# Sidebar (Yan Menü)
with st.sidebar:
    st.title("Berko AI")
    st.caption("Yapay Zeka Asistanin")
    
    st.divider()
    
    if not st.session_state.logged_in:
        st.info("Gecmis sohbetler ve kisiseellestirilmis deneyim icin giris yap.")
        if st.button("Google ile Giris Yap", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_email = "berkouser@gmail.com" 
            st.rerun()
    else:
        st.success(f"Giris Yapildi:\n{st.session_state.user_email}")
        if st.button("Cikis Yap", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.session_state.berko_messages = [] 
            st.session_state.berko_display = []
            st.rerun()
            
    st.divider()
    st.markdown("### Ozellikler")
    st.markdown("Akillis Sohbet & Kodlama")
    st.markdown("Flux Kalitesinde Gorsel Cizimi")
    st.markdown("Gerçek Medya Analizi")

# Hafıza Başlangıcı
if "berko_messages" not in st.session_state:
    st.session_state.berko_messages = []

if "berko_display" not in st.session_state:
    st.session_state.berko_display = []

# --- AKILLI BAŞLIK (Sadece hiç mesaj atılmadıysa görünür) ---
if len(st.session_state.berko_display) == 0:
    st.title("Berko AI Stüdyosu")
    st.write("Kanka selam! Sana nasıl yardımcı olabilirim? Bir şeyler sor, kod yazdıralım veya görsel çizdirelim.")

# API Anahtarını Kontrol Et (Gemini API Anahtarı)
gemini_api_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GROQ_API_KEY")

# Eğer Groq varsa veya Gemini varsa ayarla
if not gemini_api_key:
    st.error("GEMINI_API_KEY bulunamadı! Streamlit Secrets'a ekle kanka.")
    st.stop()

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Ekrana Geçmiş Mesajları HTML Baloncukları Olarak Yazdır
for message in st.session_state.berko_display:
    if message["role"] == "user":
        st.markdown(f'<div class="user-bubble">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        if message.get("type") == "image":
            st.markdown(f'<div class="berko-response"><b>Berko:</b></div>', unsafe_allow_html=True)
            st.image(message["content"], caption=message.get("caption", "Berko'nun Eseri"), use_container_width=True)
        else:
            st.markdown(f'<div class="berko-response"><b>Berko:</b><br>{message["content"]}</div>', unsafe_allow_html=True)

# --- ALT KISIM: INPUT VE ARTI BUTONU YAN YANA VE ORTalanmış ---
col_plus, col_input = st.columns([0.07, 0.93])

uploaded_media = None
media_type_str = "Metin"

with col_plus:
    with st.popover("➕"):
        st.markdown("### Medya Seç")
        secim = st.radio("Tür:", ["Fotoğraf Yükle", "Video Yükle"], label_visibility="collapsed")
        
        if secim == "Fotoğraf Yükle":
            uploaded_media = st.file_uploader("Fotoğraf seç", type=["png", "jpg", "jpeg"])
            media_type_str = "Fotoğraf"
        else:
            uploaded_media = st.file_uploader("Video seç", type=["mp4", "mov", "avi", "webm"])
            media_type_str = "Video"
            
        if uploaded_media is not None:
            st.success("Medya yüklendi!")

with col_input:
    prompt = st.chat_input("Berko'ya bir şeyler yaz veya resim çizdir...")

if prompt:
    if uploaded_media is not None:
        display_text = f"[{media_type_str} Yüklendi] {prompt}"
        st.session_state.berko_display.append({"role": "user", "content": display_text})
        st.markdown(f'<div class="user-bubble">{display_text}</div>', unsafe_allow_html=True)
            
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown('<div class="thinking-text">düşünüyorum aw bekle biraz</div>', unsafe_allow_html=True)
        
        try:
            bytes_data = uploaded_media.getvalue()
            mime_type = uploaded_media.type
            
            # Gemini'ye gönderilecek dosya objesi
            media_part = {
                "mime_type": mime_type,
                "data": bytes_data
            }
            
            response = model.generate_content([
                "Sen Berko adında samimi, kanka gibi konuşan, mizahi zekası yüksek bir AI asistanısın. Kullanıcının yüklediği medyayı (fotoğraf veya video) dikkatlice incele ve içeriği hakkında kanka tarzında samimi, net bir yorum yap.",
                media_part,
                prompt
            ])
            
            cevap = response.text
            thinking_placeholder.empty()
            st.markdown(f'<div class="berko-response"><b>Berko:</b><br>{cevap}</div>', unsafe_allow_html=True)
            st.session_state.berko_display.append({"role": "assistant", "content": cevap})
        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"Medya analiz hatası: {e}")
                    
    else:
        st.session_state.berko_messages.append({"role": "user", "content": prompt})
        st.session_state.berko_display.append({"role": "user", "content": prompt})
        
        st.markdown(f'<div class="user-bubble">{prompt}</div>', unsafe_allow_html=True)
            
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown('<div class="thinking-text">düşünüyorum aw bekle biraz</div>', unsafe_allow_html=True)
        time.sleep(1.2)
        
        try:
            prompt_lower = prompt.lower()
            resim_kokenleri = ["resim", "resiam", "rsim", "resm", "çiz", "ciz", "görsel", "gorsel", "foto", "fotograf", "oluştur", "değiştir", "dönüştür"]
            is_image_request = any(koken in prompt_lower for koken in resim_kokenleri)
            
            if is_image_request:
                harika_yanit = f"Hemen patlatıyorum kanka! İstediğin konsepti üst düzey kaliteye taşıyorum: '{prompt}'"
                thinking_placeholder.empty()
                st.markdown(f'<div class="berko-response"><b>Berko:</b><br>{harika_yanit}</div>', unsafe_allow_html=True)
                st.session_state.berko_display.append({"role": "assistant", "content": harika_yanit})
                
                # Görsel çizdirme için prompt üretelim
                response = model.generate_content(f"Sen profesyonel bir AI görsel tasarımcısısın. Fotogerçekçi, sinematik, 8k detaylı İngilizce görsel promptu ver. Sadece İngilizce promptu yaz: {prompt}")
                gelismis_ingilizce_prompt = response.text.strip()
                
                encoded_prompt = urllib.parse.quote(gelismis_ingilizce_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&model=flux-realism&nologo=true&seed={int(time.time())}"
                
                st.image(image_url, caption=f"Berko'nun Eseri: {prompt}", use_container_width=True)
                st.info("Resmi kaydetmek için üzerine sağ tıklayıp 'Resmi Farklı Kaydet' diyebilirsin.")
                
                st.session_state.berko_display.append({"role": "assistant", "content": image_url, "type": "image", "caption": f"Berko'nun Eseri: {prompt}"})
                
            else:
                # Normal sohbet
                chat = model.start_chat(history=[])
                response = model.generate_content(f"Sen Berko adında samimi, kanka gibi konuşan, mizahi zekası yüksek ve teknikten anlayan bir AI asistanısın. Kullanıcıya şu mesaja göre kanka tarzı cevap ver: {prompt}")
                berko_yaniti = response.text
                
                thinking_placeholder.empty()
                st.markdown(f'<div class="berko-response"><b>Berko:</b><br>{berko_yaniti}</div>', unsafe_allow_html=True)
                st.session_state.berko_display.append({"role": "assistant", "content": berko_yaniti})
                
        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"Hata oluştu: {e}")
