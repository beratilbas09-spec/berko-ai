
import streamlit as st
from groq import Groq
import urllib.parse
import requests
import json

# Sayfa Ayarları
st.set_page_config(
    page_title="Berko AI | Gemini Resimli",
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
    st.write("Sohbet: Groq | Resim: Google Imagen API")

# --- ANA SOHBET EKRANI ---
st.title("🧑‍💻 Berko ile Sohbet Et")
st.write("Kanka selam, ben Berko! Naber, ne konuşuyoruz?")

# API Anahtarlarını Kontrol Et
groq_api_key = st.secrets.get("GROQ_API_KEY")
gemini_api_key = st.secrets.get("GEMINI_API_KEY")

if not groq_api_key or not gemini_api_key:
    st.error("API anahtarları eksik! Streamlit Secrets'a GROQ_API_KEY ve GEMINI_API_KEY eklediğinden emin ol.")
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
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            if message.get("type") == "image":
                image_url = message["content"]
                st.image(image_url, caption="Berko'nun Eseri")
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
                        
                        # Google'ın Imagen 3 API'sine direkt HTTP isteği atıyoruz (Kütüphane gerektirmez!)
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={gemini_api_key}"
                        headers = {"Content-Type": "application/json"}
                        payload = {
                            "instances": [{"prompt": resim_promptu}],
                            "parameters": {"sampleCount": 1, "aspectRatio": "1:1"}
                        }
                        
                        response = requests.post(url, headers=headers, data=json.dumps(payload))
                        
                        if response.status_code == 200:
                            res_json = response.json()
                            base64_img = res_json["predictions"][0]["bytesBase64Encoded"]
                            
                            import base64
                            img_bytes = base64.b64decode(base64_img)
                            
                            st.image(img_bytes, caption=f"Berko'nun Eseri: {resim_promptu}")
                            st.download_button(
                                label="📥 Resmi Bilgisayara İndir",
                                data=img_bytes,
                                file_name="berko_gemini.png",
                                mime="image/png"
                            )
                            
                            st.session_state.messages.append({"role": "assistant", "content": img_bytes, "type": "image"})
                        else:
                            st.error(f"Google API Hatası: {response.text}")
                else:
                    st.markdown(berko_yaniti)
                    st.session_state.messages.append({"role": "assistant", "content": berko_yaniti})
                    
            except Exception as e:
                st.error(f"Hata oluştu: {e}")
