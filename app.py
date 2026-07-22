

import streamlit as st
from groq import Groq
import urllib.parse

# Sayfa Ayarları
st.set_page_config(
    page_title="Berko AI | Resimli",
    page_icon="🧑‍💻",
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
    st.write("Sohbet: Groq | Resim: Ücretsiz Motor")

# --- ANA SOHBET EKRANI ---
st.title("🧑‍💻 Berko ile Sohbet Et")
st.write("Kanka selam, ben Berko! Naber, ne konuşuyoruz?")

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
            "content": "Sen Berko adında samimi, kanka gibi konuşan, mizahi zekası yüksek bir AI asistanısın. Kullanıcı sohbet etmek istediğinde sadece normal bir insan gibi sohbet et. Asla durduk yere resim üretmeye çalışama."
        }
    ]

if "berko_display" not in st.session_state:
    st.session_state.berko_display = []

# Ekrana Geçmiş Mesajları Yazdır
for message in st.session_state.berko_display:
    with st.chat_message(message["role"]):
        if message.get("type") == "image":
            st.image(message["content"], caption=message.get("caption", "Berko'nun Eseri"))
        else:
            st.markdown(message["content"])

# Kullanıcıdan Mesaj Al
if prompt := st.chat_input("Berko'ya bir şeyler yaz..."):
    st.session_state.berko_messages.append({"role": "user", "content": prompt})
    st.session_state.berko_display.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Berko düşünüyor..."):
            try:
                # Kullanıcı resim kelimesi geçirmiş mi kontrol edelim
                resim_kelimeleri = ["resim yap", "çiz", "görsel oluştur", "resmet", "fotoğrafını yap", "oluştur"]
                is_image_request = any(kelime in prompt.lower() for kelime in resim_kelimeleri)
                
                chat_completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.berko_messages,
                    temperature=0.7,
                )
                berko_yaniti = chat_completion.choices[0].message.content
                
                # Eğer kullanıcı gerçekten resim istemişse resmi bas, istemediyse sadece normal sohbet etsin
                if is_image_request:
                    st.markdown(berko_yaniti)
                    st.session_state.berko_display.append({"role": "assistant", "content": berko_yaniti})
                    
                    # İngilizce prompt çevirisi için ufak bir özet alalım veya kullanıcının promptunu kullanalım
                    resim_promptu = prompt
                    encoded_prompt = urllib.parse.quote(resim_promptu)
                    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true"
                    
                    st.image(image_url, caption=f"Berko'nun Eseri: {resim_promptu}")
                    st.info("💡 Resmi kaydetmek için resmin üzerine sağ tıklayıp 'Resmi Farklı Kaydet' diyebilirsin.")
                    
                    st.session_state.berko_messages.append({"role": "assistant", "content": berko_yaniti})
                    st.session_state.berko_display.append({"role": "assistant", "content": image_url, "type": "image", "caption": f"Berko'nun Eseri: {resim_promptu}"})
                else:
                    # Normal sohbet
                    st.markdown(berko_yaniti)
                    st.session_state.berko_messages.append({"role": "assistant", "content": berko_yaniti})
                    st.session_state.berko_display.append({"role": "assistant", "content": berko_yaniti})
                    
            except Exception as e:
                st.error(f"Hata oluştu: {e}")
