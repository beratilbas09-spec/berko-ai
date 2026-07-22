




import streamlit as st
from groq import Groq
import urllib.parse
import time
from PIL import Image
import io
import base64

# Sayfa Ayarları
st.set_page_config(
    page_title="Berko AI | Medya & Şarkı Fabrikası",
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
    st.write("Müzik: Suno / Udio Şarkı Fabrikası")

# --- ANA SOHBET EKRANI ---
st.title("🧑‍💻 Berko ile Sohbet, Çizim & Şarkı Üretimi")
st.write("Kanka selam, ben Berko! Fotoğraf yükle, resim çizdir veya Suno/Udio için kusursuz şarkı paketleri hazırla.")

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
        else:
            st.markdown(message["content"])

# Kullanıcıdan Mesaj Al
if prompt := st.chat_input("Berko'ya bir şeyler yaz, resim çizdir veya şarkı iste..."):
    
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
                    
                    # MÜZİK / ŞARKI KONTROLÜ
                    muzik_kokenleri = ["müzik", "muzik", "şarkı", "sarki", "beste", "melodi", "beat", "ritim", "suno", "udio"]
                    is_music_request = any(koken in prompt_lower for koken in muzik_kokenleri)
                    
                    # RESİM KONTROLÜ
                    resim_kokenleri = ["resim", "resiam", "rsim", "resm", "çiz", "ciz", "görsel", "gorsel", "foto", "fotograf", "oluştur", "değiştir", "dönüştür"]
                    is_image_request = any(koken in prompt_lower for koken in resim_kokenleri) and not is_music_request
                    
                    if is_music_request:
                        # PROFESYONEL SUNO/UDIO ŞARKI PAKETİ ÜRETİCİSİ
                        muzik_giris = f"Hemen patlatıyorum kanka! İstediğin konseptte Suno/Udio için kusursuz bir şarkı paketi hazırlıyorum: '{prompt}'"
                        st.markdown(muzik_giris)
                        
                        suno_ureteci = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "Sen profesyonel bir müzik prodüktörüsün. Kullanıcının isteğine göre iki şey üret:\n"
                                        "1. **Style of Music (Tarz):** Suno/Udio için İngilizce tarz etiketleri (örn: energetic drift phonk, heavy bass, dark atmospheric, 140 bpm).\n"
                                        "2. **Lyrics (Şarkı Sözleri):** [Verse], [Chorus] etiketleriyle tam profesyonel şarkı sözleri.\n"
                                        "Markdown formatında, kopyalamaya hazır şekilde sun."
                                    )
                                },
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.7
                        )
                        suno_sonucu = suno_ureteci.choices[0].message.content.strip()
                        
                        st.markdown("### 🎸 Suno / Udio İçin Hazır Paket:")
                        st.markdown(suno_sonucu)
                        st.success("✨ Bu tarzı ve sözleri kopyalayıp doğrudan **suno.com** veya **udio.com** adresine yapıştırarak saniyesinde profesyonel vokalistli şarkı üretebilirsin kanka!")
                        
                        st.session_state.berko_messages.append({"role": "assistant", "content": muzik_giris + "\n\n" + suno_sonucu})
                        st.session_state.berko_display.append({"role": "assistant", "content": muzik_giris + "\n\n" + suno_sonucu})
                        
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
                        chat_completion = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=st.session_state.berko_messages,
                            temperature=0.7,
                        )
                        berko_yaniti = chat_completion.choices[0].message.content
                        st.markdown(berko_yaniti)
                        st.session_state.berko_messages.append({"role": "assistant", "content": berko_yaniti})
                        st.session_state.berko_display.append({"role": "assistant", "content": berko_yaniti})
                        
                except Exception as e:
                    st.error(f"Hata oluştu: {e}")
