

import streamlit as st
from groq import Groq
import urllib.parse
import time
from PIL import Image
import io
import base64

# Sayfa Ayarları
st.set_page_config(
    page_title="Berko AI | Süper Medya",
    page_icon="🧑‍💻",
    layout="centered"
)

# --- GİRİŞ & OTURUM SİMÜLASYONU ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = None

# Sidebar (Yan Menü)
with st.sidebar:
    st.title("🧑‍💻 Berko AI")
    
    if not st.session_state.logged_in:
        st.info("Geçmiş sohbetler için giriş yap.")
        if st.button("🌐 Google ile Giriş Yap", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_email = "berkouser@gmail.com" 
            st.rerun()
    else:
        st.success(f"Giriş Yapıldı: {st.session_state.user_email}")
        if st.button("Çıkış Yap", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.session_state.berko_messages = [] 
            st.session_state.berko_display = []
            st.rerun()
            
    st.divider()
    st.write("Sohbet & Vizyon: Groq Llama 3.2/3.3")
    st.write("Resim Üretim: Flux Ultra Motoru")

# --- ANA SOHBET EKRANI ---
st.title("🧑‍💻 Berko ile Sohbet Et & Çiz")
st.write("Kanka selam, ben Berko! Fotoğraf yükle, üzerinde konuşalım ya da resim patlatalım.")

# API Anahtarını Kontrol Et
groq_api_key = st.secrets.get("GROQ_API_KEY")

if not groq_api_key:
    st.error("GROQ_API_KEY bulunamadı! Streamlit Secrets'a ekle.")
    st.stop()

client = Groq(api_key=groq_api_key)

# Hafıza Başlangıcı
if "berko_messages" not in st.session_state:
    st.session_state.berko_messages = [
        {
            "role": "system",
            "content": "Sen Berko adında samimi, kanka gibi konuşan, mizahi zekası yüksek bir AI asistanısın."
        }
    ]

if "berko_display" not in st.session_state:
    st.session_state.berko_display = []

# --- GÖRSEL YÜKLEME ALANI (FILE UPLOADER) ---
uploaded_file = st.file_uploader("📷 Bir fotoğraf yükle (Üzerinde konuşalım / Değiştirelim)", type=["png", "jpg", "jpeg"])

uploaded_image_base64 = None
if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    st.image(uploaded_file, caption="Yüklediğin Görsel", width=300)
    # Vision modeli için base64 çevirisi
    uploaded_image_base64 = base64.b64encode(image_bytes).decode("utf-8")

# Ekrana Geçmiş Mesajları Yazdır
for message in st.session_state.berko_display:
    with st.chat_message(message["role"]):
        if message.get("type") == "image":
            st.image(message["content"], caption=message.get("caption", "Berko'nun Eseri"), use_container_width=True)
        else:
            st.markdown(message["content"])

# Kullanıcıdan Mesaj Al
if prompt := st.chat_input("Berko'ya bir şeyler yaz veya fotoğraf hakkında soru sor..."):
    
    # Kullanıcı görsel yüklediyse ve mesaj attıysa Vision modelini kullanacağız
    if uploaded_image_base64:
        st.session_state.berko_display.append({"role": "user", "content": f"[Fotoğraf Yüklendi] {prompt}"})
        with st.chat_message("user"):
            st.markdown(f"📷 *[Fotoğraf yüklendi]* {prompt}")
            
        with st.chat_message("assistant"):
            with st.spinner("Berko yüklediğin fotoğrafa bakıyor..."):
                try:
                    # Groq Vision Modeli (Görseli anlayan model)
                    vision_completion = client.chat.completions.create(
                        model="llama-3.2-90b-vision-preview",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": f"Kullanıcının yüklediği bu görsel hakkında samimi, kanka tarzında yorum yap ve şu isteğini yerine getir: {prompt}"},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{uploaded_image_base64}"
                                        },
                                    },
                                ],
                            }
                        ],
                        temperature=0.7,
                    )
                    cevap = vision_completion.choices[0].message.content
                    st.markdown(cevap)
                    st.session_state.berko_display.append({"role": "assistant", "content": cevap})
                except Exception as e:
                    st.error(f"Görsel analiz hatası: {e}")
                    
    else:
        # Normal Metin / Resim Üretim Akışı
        st.session_state.berko_messages.append({"role": "user", "content": prompt})
        st.session_state.berko_display.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Berko düşünüyor ve işlem yapıyor..."):
                try:
                    resim_kokenleri = ["resim", "resiam", "rsim", "resm", "çiz", "ciz", "görsel", "gorsel", "foto", "fotograf", "oluştur", "yap", "değiştir", "dönüştür"]
                    prompt_lower = prompt.lower()
                    is_image_request = any(koken in prompt_lower for koken in resim_kokenleri)
                    
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
                        
                        # Süper Prompt Üretici
                        cevirici_istegi = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {
                                    "role": "system", 
                                    "content": (
                                        "Sen profesyonel bir AI görsel tasarımcısısın. Kullanıcının isteğini alıp; "
                                        "fotogerçekçi, sinematik ışıklandırma, 8k çözünürlük, kusursuz detaylar içeren devasa ve profesyonel bir "
                                        "İngilizce görsel promptuna çevir. Sadece İngilizce promptu ver."
                                    )
                                },
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.7
                        )
                        gelismis_ingilizce_prompt = cevirici_istegi.choices[0].message.content.strip()
                        
                        # Daha gelişmiş, yüksek kaliteli ve şık alternatif görsel URL uç noktası (Flux Realism / Ultra Modeli)
                        encoded_prompt = urllib.parse.quote(gelismis_ingilizce_prompt)
                        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&model=flux-realism&nologo=true&seed={int(time.time())}"
                        
                        st.image(image_url, caption=f"Berko'nun Eseri: {prompt}", use_container_width=True)
                        
                        with st.expander("🔍 Üretilen Profesyonel Prompt"):
                            st.code(gelismis_ingilizce_prompt, language="text")
                            
                        st.info("💡 Resmi kaydetmek için üzerine sağ tıklayıp 'Resmi Farklı Kaydet' diyebilirsin.")
                        
                        st.session_state.berko_messages.append({"role": "assistant", "content": harika_yanit})
                        st.session_state.berko_display.append({"role": "assistant", "content": image_url, "type": "image", "caption": f"Berko'nun Eseri: {prompt}"})
                    else:
                        st.markdown(berko_yaniti)
                        st.session_state.berko_messages.append({"role": "assistant", "content": berko_yaniti})
                        st.session_state.berko_display.append({"role": "assistant", "content": berko_yaniti})
                        
                except Exception as e:
                    st.error(f"Hata oluştu: {e}")
