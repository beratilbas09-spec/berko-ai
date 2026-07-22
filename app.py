

import streamlit as st
from groq import Groq
import urllib.parse
import time
from PIL import Image
import io
import base64
from huggingface_hub import InferenceClient

# Sayfa Ayarları
st.set_page_config(
    page_title="Berko AI | Babadır",
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
    st.write("Sohbet: Groq Llama 3.3 70B")
    st.write("Görsel: Flux Realism")
    st.write("Müzik: Hugging Face MusicGen (InferenceClient)")

# --- ANA SOHBET EKRANI ---
st.title("🧑‍💻 Berko ile Sohbet, Çizim & Müzik Yap")
st.write("Kanka selam, ben Berko! Fotoğraf yükle, resim çizdir veya müzik patlatalım.")

# API Anahtarını Kontrol Et
groq_api_key = st.secrets.get("GROQ_API_KEY")
hf_api_key = st.secrets.get("HUGGINGFACE_API_KEY")

if not groq_api_key or not hf_api_key:
    st.error("GROQ_API_KEY veya HUGGINGFACE_API_KEY bulunamadı! Streamlit Secrets'a ekle.")
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

# --- GÖRSEL YÜKLEME ALANI ---
uploaded_file = st.file_uploader("📷 Bir fotoğraf yükle (Hakkında konuşalım)", type=["png", "jpg", "jpeg"])

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
        elif message.get("type") == "audio":
            st.audio(message["content"], format="audio/wav")
            st.markdown(message.get("caption", ""))
        else:
            st.markdown(message["content"])

# Kullanıcıdan Mesaj Al
if prompt := st.chat_input("Berko'ya bir şeyler yaz, resim çizdir veya müzik iste..."):
    
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
            with st.spinner("Berko düşünüyor ve işliyor..."):
                try:
                    prompt_lower = prompt.lower()
                    
                    # MÜZİK KONTROLÜ
                    muzik_kokenleri = ["müzik", "muzik", "şarkı", "sarki", "beste", "melodi", "beat", "ritim", "enstrümantal", "orkestra", "piyano", "gitar"]
                    is_music_request = any(koken in prompt_lower for koken in muzik_kokenleri)
                    
                    # RESİM KONTROLÜ
                    resim_kokenleri = ["resim", "resiam", "rsim", "resm", "çiz", "ciz", "görsel", "gorsel", "foto", "fotograf", "oluştur", "değiştir", "dönüştür"]
                    is_image_request = any(koken in prompt_lower for koken in resim_kokenleri) and not is_music_request
                    
                    # Genel sohbet yanıtı
                    chat_completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=st.session_state.berko_messages,
                        temperature=0.7,
                    )
                    berko_yaniti = chat_completion.choices[0].message.content
                    
                    if is_music_request:
                        muzik_baslangici = f"Kulaklıkla dinlemelik harika bir parça kurguluyorum kanka: '{prompt}'"
                        st.markdown(muzik_baslangici)
                        
                        cevirici_istegi = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "Sen profesyonel bir AI müzik prodüktörüsün. Kullanıcının isteğini alıp; "
                                        "MusicGen modelinin anlayacağı şekilde ayrıntılı, İngilizce bir müzik promptuna çevir. "
                                        "Müzik türü, ruh hali, enstrümanlar ve tempo belirt. Sadece İngilizce promptu ver."
                                    )
                                },
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.7
                        )
                        ingilizce_music_prompt = cevirici_istegi.choices[0].message.content.strip()
                        st.info(f"Müzik Tarzı Belirlendi: {ingilizce_music_prompt}")
                        
                        # --- HUGGING FACE RESMİ KÜTÜPHANESİ İLE BAĞLANTI (DNS HATASIZ ÇÖZÜM) ---
                        with st.spinner("Berko notaları birleştiriyor, bu işlem 30-60 saniye sürebilir..."):
                            try:
                                client_hf = InferenceClient(token=hf_api_key)
                                
                                # text_to_audio fonksiyonu Hugging Face Hub kütüphanesinin yerleşik ve en kararlı yoludur
                                audio_bytes = client_hf.text_to_audio(
                                    text=ingilizce_music_prompt,
                                    model="facebook/musicgen-large"
                                )
                                
                                if audio_bytes:
                                    st.success("✨ İşte müzik eseri! Aşağıdan dinleyip indirebilirsin.")
                                    st.audio(audio_bytes, format="audio/wav")
                                    
                                    st.session_state.berko_messages.append({"role": "assistant", "content": muzik_baslangici})
                                    st.session_state.berko_display.append({"role": "assistant", "content": audio_bytes, "type": "audio", "caption": f"Berko'nun Eseri: {prompt}"})
                                else:
                                    st.error("Müzik verisi boş döndü kanka.")
                                    
                            except Exception as e:
                                st.error(f"Müzik üretilirken hata oluştu: {e}")
                        
                    elif is_image_request:
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
