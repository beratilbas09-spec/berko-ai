
import streamlit as st
from groq import Groq
# OpenAI kütüphanesini kaldırdık, artık gerek yok.

# Sayfa Ayarları
st.set_page_config(
    page_title="Berko AI | Ücretsiz Resimli",
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
            # Simüle edilmiş Google girişi
            st.session_state.logged_in = True
            st.session_state.user_email = "berkouser@gmail.com" 
            st.rerun()
    else:
        st.success(f"Giriş Yapıldı: {st.session_state.user_email}")
        if st.button("Çıkış Yap", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.session_state.messages = [] 
            st.rerun()
            
    st.divider()
    st.write("Resimler ücretsiz Pollinations AI ile oluşturulur.")


# --- ANA SOHBET EKRANI ---
st.title("🧑‍💻 Berko ile Sohbet Et")
st.write("Kanka selam, ben Berko! Naber, ne konuşuyoruz?")

# API Anahtarını Kontrol Et
groq_api_key = st.secrets.get("GROQ_API_KEY")

if not groq_api_key:
    st.error("GROQ_API_KEY bulunamadı! Streamlit Secrets'a ekle.")
    st.stop()

client = Groq(api_key=groq_api_key)

# Sohbet Geçmişini Başlat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "Sen Berko adında samimi, kanka gibi konuşan, mizahi zekası yüksek bir AI asistanısın. Resim yapma isteği aldığında, 'Hemen hallediyorum kanka!' gibi bir tepki verip, ardından şu formatta bir metin yazarak resmi oluşturmalısın: [RESİM OLUŞTUR: kullanıcını_resim_isteği]. Bu özel etiketi sakın unutma."
        }
    ]

# Geçmiş Mesajları Ekrana Yazdır
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            # Metin içeriğini göster
            st.markdown(message["content"])
            
            # Eğer bu bir resim URL'i ise, resmi ve indirme butonunu göster
            if message.get("type") == "image":
                image_url = message["content"]
                st.image(image_url, caption="Berko'nun eseri")
                st.markdown(f"[📥 Resmi İndir]({image_url})", unsafe_allow_html=True)

# Kullanıcıdan Mesaj Al
if prompt := st.chat_input("Berko'ya bir şeyler yaz..."):
    # Kullanıcı mesajını kaydet ve göster
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Berko düşünüyor..."):
            try:
                # Groq'dan yanıt al
                chat_completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.messages,
                    temperature=0.7,
                )
                berko_yaniti = chat_completion.choices[0].message.content
                st.markdown(berko_yaniti)
                st.session_state.messages.append({"role": "assistant", "content": berko_yaniti})

                # --- ÜCRETSİZ RESİM OLUŞTURMA KONTROLÜ (Pollinations AI) ---
                if "[RESİM OLUŞTUR:" in berko_yaniti:
                    # Metin içinden resmi oluşturacak isteği ayıkla
                    start_tag = "[RESİM OLUŞTUR:"
                    end_tag = "]"
                    start_index = berko_yaniti.find(start_tag) + len(start_tag)
                    end_index = berko_yaniti.find(end_tag, start_index)
                    
                    if end_index > start_index:
                        resim_istege = berko_yaniti[start_index:end_index].strip()
                        
                        # Ücretsiz Pollinations AI resim URL'ini oluştur
                        import urllib.parse
                        encoded_prompt = urllib.parse.quote(resim_istege)
                        # width/height ile boyutu ayarla
                        pollinations_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true"
                        
                        st.write("✨ İşte eserin kanka!")
                        st.image(pollinations_url, caption=resim_istege)
                        st.markdown(f"[📥 Resmi İndir]({pollinations_url})", unsafe_allow_html=True)

                        # Sohbet geçmişine resim URL'ini kaydet (type='image')
                        st.session_state.messages.append({"role": "assistant", "content": pollinations_url, "type": "image"})
            
            except Exception as e:
                st.error(f"Hata oluştu: {e}")
