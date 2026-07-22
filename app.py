
import streamlit as st
from groq import Groq
from google import genai
from google.genai import types

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
    st.write("Sohbet: Groq (Llama 3.3) | Resim: Google Gemini")

# --- ANA SOHBET EKRANI ---
st.title("🧑‍💻 Berko ile Sohbet Et")
st.write("Kanka selam, ben Berko! Naber, ne konuşuyoruz?")

# API Anahtarlarını Kontrol Et
groq_api_key = st.secrets.get("GROQ_API_KEY")
gemini_api_key = st.secrets.get("GEMINI_API_KEY")

if not groq_api_key or not gemini_api_key:
    st.error("API anahtarları eksik! Lütfen Streamlit Secrets'a GROQ_API_KEY ve GEMINI_API_KEY ekle.")
    st.stop()

# İstemcileri Başlat
client = Groq(api_key=groq_api_key)
google_client = genai.Client(api_key=gemini_api_key)

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
                image_data = message["content"]
                st.image(image_data, caption="Berko'nun Eseri")
                st.download_button(
                    label="📥 Resmi Bilgisayara İndir",
                    data=image_data,
                    file_name="berko_gemini_eseri.png",
                    mime="image/png",
                )
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
                        
                        # Google Imagen modeliyle resmi üret
                        result = google_client.models.generate_images(
                            model='imagen-3.0-generate-002',
                            prompt=resim_promptu,
                            config=types.GenerateImagesConfig(
                                number_of_images=1,
                                output_mime_type="image/png",
                                aspect_ratio="1:1",
                            )
                        )
                        
                        for generated_image in result.generated_images:
                            image_bytes = generated_image.image.image_bytes
                            
                            st.image(image_bytes, caption=f"Berko'nun Eseri: {resim_promptu}")
                            st.download_button(
                                label="📥 Resmi Bilgisayara İndir",
                                data=image_bytes,
                                file_name="berko_gemini_eseri.png",
                                mime="image/png",
                            )
                            
                            st.session_state.messages.append({"role": "assistant", "content": image_bytes, "type": "image"})
                else:
                    st.markdown(berko_yaniti)
                    st.session_state.messages.append({"role": "assistant", "content": berko_yaniti})
                    
            except Exception as e:
                st.error(f"Hata oluştu: {e}")
