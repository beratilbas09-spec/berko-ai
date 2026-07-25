

import streamlit as st
import os
import requests
from groq import Groq

# --- GOOGLE SEARCH CONSOLE & ANALYTICS DOĞRULAMA KODLARI ---
st.html("""
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-TD5CE2QGY4"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-TD5CE2QGY4');
</script>
<meta name="google-site-verification" content="QHKdEcPEF68ahnKS-ncSUNcbOKoYDH4Z_g0yBYCmc4Y" />
""")

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="Berko AI Studio",
    page_icon="🤖",
    layout="centered"
)

# --- SECRETS & API ANAHTARLARI ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
HUGGINGFACE_API_KEY = st.secrets.get("HUGGINGFACE_API_KEY", "")

# --- SYSTEM PROMPT (KİŞİLİK TANIMI) ---
SYSTEM_PROMPT = """
Sen "Berko AI" adında eğlenceli, samimi, komik, bazen goygoy yapan ama zeki bir yapay zeka asistansın.
Kullanıcıyla kanka gibi konuşursun. Türkçe yanıt verirsin.
Yaratıcın Berat İlbaş'tır. Özel detaylar sorulursa Berat'ın uyarısını hatırla.
"""

# --- SOHBET GEÇMİŞİ BAŞLATMA ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- ARAYÜZ BAŞLIĞI ---
st.title("🤖 Berko AI Studio")
st.caption("Berko AI - Gelişmiş Yapay Zeka Asistanı")

# --- GEÇMİŞ MESAJLARI EKRANA BASMA ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- KULLANICI GİRDİSİ VE CEVAP ÜRETME ---
if prompt := st.chat_input("Berko AI'ya bir şeyler yaz..."):
    # Kullanıcı mesajını ekle ve göster
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Bot cevabını üret
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        if not GROQ_API_KEY:
            response_text = "⚠️ Groq API anahtarı Streamlit Secrets alanında bulunamadı!"
            message_placeholder.markdown(response_text)
        else:
            try:
                client = Groq(api_key=GROQ_API_KEY)
                
                # API için mesaj geçmişini hazırla
                api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                for m in st.session_state.messages:
                    api_messages.append({"role": m["role"], "content": m["content"]})
                
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=api_messages,
                    temperature=0.7,
                    max_tokens=1024
                )
                
                response_text = completion.choices[0].message.content
                message_placeholder.markdown(response_text)
                
            except Exception as e:
                response_text = f"Bir hata oluştu kanka: {str(e)}"
                message_placeholder.markdown(response_text)
                
    st.session_state.messages.append({"role": "assistant", "content": response_text})
