
import streamlit as st
from groq import Groq
import urllib.parse
import requests

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
            "content": "Sen Berko adında samimi, kanka gibi konuşan, mizahi zekası yüksek bir AI asistanısın. Kullanıcı senden resim yapmanı istediğinde sadece kısa bir cümle kur ve ardından kesinlikle şu formatta resmi belirt: [RESİM: ingilizce_resim_aciklamasi]. Örnek: [RESİM: a cute cat playing guitar]. Başka hiçbir şey yazma."
        }
    ]

# Geçmiş Mesajları Ekrana Yazdır
for i, message in enumerate(st.session_state.messages):
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            if message.get("type") == "image":
                image_url = message["content"]
                st.image(image_url, caption="Berko'nun eseri")
                
                # Doğrudan indirme butonu
                try:
                    img_data = requests.get(image_url).content
                    st.download_button(
                        label="📥 Resmi Bilgisayara İndir",
                        data=img_data,
                        file_name="berko_eseri.png",
                        mime="image/png",
                        key=f"history_download_{i}"
                    )
                except:
                    st.write("İndirme butonu hazırlanamadı.")
            else:
                st.markdown(message["content"])

# Kullanıcıdan Mesaj Al
if prompt := st.chat_input("Berko'ya bir şeyler yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Berko düşünüyor ve çiziyor..."):
            try:
                chat_completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.messages,
                    temperature=0.7,
                )
                berko_yaniti = chat_completion.choices[0].message.content
                
                # Resim etiketini kontrol et ve ayıkla
                if "[RESİM:" in berko_yaniti:
                    start_idx = berko_yaniti.find("[RESİM:") + len("[RESİM:")
                    end_idx = berko_yaniti.find("]", start_idx)
                    
                    if end_idx > start_idx:
                        resim_promptu = berko_yaniti[start_idx:end_idx].strip()
                        temiz_yanit = berko_yaniti[:berko_yaniti.find("[RESİM:")].strip()
                        
                        if temiz_yanit:
                            st.markdown(temiz_yanit)
                            st.session_state.messages.append({"role": "assistant", "content": temiz_yanit})
                        
                        # Pollinations AI URL oluştur
                        encoded_prompt = urllib.parse.quote(resim_promptu)
                        pollinations_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true"
                        
                        st.image(pollinations_url, caption=resim_promptu)
                        
                        # Gerçek indirme butonu
                        try:
                            img_data = requests.get(pollinations_url).content
                            st.download_button(
                                label="📥 Resmi Bilgisayara İndir",
                                data=img_data,
                                file_name="berko_eseri.png",
                                mime="image/png",
                                key=f"new_download"
                            )
                        except:
                            st.write("İndirilemedi.")
                        
                        st.session_state.messages.append({"role": "assistant", "content": pollinations_url, "type": "image"})
                else:
                    st.markdown(berko_yaniti)
                    st.session_state.messages.append({"role": "assistant", "content": berko_yaniti})
                    
            except Exception as e:
                st.error(f"Hata oluştu: {e}")
