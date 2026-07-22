




import streamlit as st
from groq import Groq
import urllib.parse
import time
from PIL import Image
import io
import base64

# Sayfa Ayarları
st.set_page_config(
    page_title="Berko AI | Akıllı Asistan",
    page_icon="🧑‍💻",
    layout="centered"
)

# --- ÖZEL CSS İLE ARAYÜZÜ ŞEKİLLENDİRME ---
st.markdown("""
    <style>
    /* Sidebar arka planı ve genel düzen */
    [data-testid="stSidebar"] {
        background-color: #1e1e2f;
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    /* Butonları şıklaştır */
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
    </style>
""", unsafe_allow_html=True)

# --- GİRİŞ & OTURUM SİMÜLASYONU ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = None

# Sidebar (Yan Menü) - Sadeleştirilmiş ve şık
with st.sidebar:
    st.title("🧑‍💻 Berko AI")
    st.caption("Yapay Zeka Asistanın")
    
    st.divider()
    
    if not st.session_state.logged_in:
        st.info("Geçmiş sohbetler ve kişiselleştirilmiş deneyim için giriş yap.")
        if st.button("🌐 Google ile Giriş Yap", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_email = "berkouser@gmail.com" 
            st.rerun()
    else:
        st.success(f"Giriş Yapıldı:\n{st.session_state.user_email}")
        if st.button("Çıkış Yap", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.session_state.berko_messages = [] 
            st.session_state.berko_display = []
            st.rerun()
            
    st.divider()
    st.markdown("### 🚀 Özellikler")
    st.markdown("💬 Akıllı Sohbet & Kodlama")
    st.markdown("🎨 Flux Kalitesinde Görsel Çizimi")
    st.markdown("📷 Fotoğraf Analizi")

# --- ANA SOHBET EKRANI ---
st.title("🧑‍💻 Berko AI Stüdyosu")
st.write("Kanka selam! Sana nasıl yardımcı olabilirim? Bir şeyler sor, kod yazdıralım veya görsel çizdirelim.")

# API Anahtarını Kontrol Et
groq_api_key = st.secrets.get("GROQ_API_KEY")

if not groq_api_key:
    st.error("GROQ_API_KEY bulunamadı! Streamlit Secrets'a ekle kanka.")
    st.stop()

client = Groq(api_key=groq_api_key)

# Hafıza Başlangıcı
if "berko_messages" not in st.session_state:
    st.session_state.berko_messages = [
        {
            "role": "system",
            "content": "Sen Berko adında samimi, kanka gibi konuşan, mizahi zekası yüksek ve teknkten anlayan bir AI asistanısın."
        }
    ]

if "berko_display" not in st.session_state:
    st.session_state.berko_display = []

# --- GÖRSEL YÜKLEME ALANI ---
uploaded_file = st.file_uploader("📷 Bir fotoğraf yükle (Üzerine konuşalım)", type=["png", "jpg", "jpeg"])

uploaded_image_base64 = None
if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    st.image(uploaded_file, caption="Yüklediğin Görsel", width=300)
    uploaded_image_base64 = base64.b64encode(image_bytes).decode("utf-8")

# Ekrana Geçmiş Mesajları Yazdır
for message in st.session_state.berko_display:
    with st.chat_message(message["role"]):
        if message.get("type") == "image":
            st.image(message["content"], caption=message.get("caption", "Berko'nun Eseri"), use_container_width=True)
        else:
            st.markdown(message["content"])

# Kullanıcıdan Mesaj Al
if prompt := st.chat_input("Berko'ya bir şeyler yaz veya resim çizdir..."):
    
    if uploaded_image_base64:
        st.session_state.berko_display.append({"role": "user", "content": f"[Fotoğraf Yüklendi] {prompt}"})
        with st.chat_message("user"):
            st.markdown(f"📷 *[Fotoğraf yüklendi]* {prompt}")
            
        with st.chat_message("assistant"):
            with st.spinner("Berko fotoğrafa bakıyor ve yorum yapıyor..."):
                try:
                    analiz_istegi = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "Kullanıcı bir fotoğraf yükledi. Kanka tarzında samimi ve mizahi bir yorum yap."},
                            {"role": "user", "content": f"Görsel hakkında soru/yorum: '{prompt}'"}
                        ],
                        temperature=0.7,
                    )
                    cevap = analiz_istegi.choices[0].message.content
                    st.markdown(cevap)
                    st.session_state.berko_display.append({"role": "assistant", "content": cevap})
                except Exception as e:
                    st.error(f"Analiz hatası: {e}")
                    
    else:
        st.session_state.berko_messages.append({"role": "user", "content": prompt})
        st.session_state.berko_display.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Berko düşünüyor..."):
                try:
                    prompt_lower = prompt.lower()
                    
                    # RESİM KONTROLÜ
                    resim_kokenleri = ["resim", "resiam", "rsim", "resm", "çiz", "ciz", "görsel", "gorsel", "foto", "fotograf", "oluştur", "değiştir", "dönüştür"]
                    is_image_request = any(koken in prompt_lower for koken in resim_kokenleri)
                    
                    # Genel sohbet yanıtı
                    chat_completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=st.session_state.berko_messages,
                        temperature=0.7,
                    )
                    berko_yaniti = chat_completion.choices[0].message.content
                    
                    if is_image_request:
                        harika_yanit = f"Hemen patlatıyorum kanka! İstediğin konsepti üst düzey kaliteye taşıyorum: '{prompt}'"
                        st.markdown(harika_yanit)
                        st.session_state.berko_display.append({"role": "assistant", "content": harika_yanit})
                        
                        cevirici_istegi = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {"role": "system", "content": "Sen profesyonel bir AI görsel tasarımcısısın. Fotogerçekçi, sinematik, 8k detaylı İngilizce görsel promptu ver. Sadece İngilizce promptu yaz."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.7
                        )
                        gelismis_ingilizce_prompt = cevirici_istegi.choices[0].message.content.strip()
                        
                        encoded_prompt = urllib.parse.quote(gelismis_ingilizce_prompt)
                        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&model=flux-realism&nologo=true&seed={int(time.time())}"
                        
                        st.image(image_url, caption=f"Berko'nun Eseri: {prompt}", use_container_width=True)
                        st.info("💡 Resmi kaydetmek için üzerine sağ tıklayıp 'Resmi Farklı Kaydet' diyebilirsin.")
                        
                        st.session_state.berko_messages.append({"role": "assistant", "content": harika_yanit})
                        st.session_state.berko_display.append({"role": "assistant", "content": image_url, "type": "image", "caption": f"Berko'nun Eseri: {prompt}"})
                        
                    else:
                        st.markdown(berko_yaniti)
                        st.session_state.berko_messages.append({"role": "assistant", "content": berko_yaniti})
                        st.session_state.berko_display.append({"role": "assistant", "content": berko_yaniti})
                        
                except Exception as e:
                    st.error(f"Hata oluştu: {e}")
