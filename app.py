

# Create a Python script to update app.py code for Streamlit dark/light theme fix
# The user wants a light theme (white background) so they can see elements clearly.

updated_code = '''import streamlit as st
from groq import Groq
from openai import OpenAI
import urllib.parse
import time
from PIL import Image
import io
import base64
import requests

# Sayfa Ayarları
st.set_page_config(
    page_title="Berko AI Studio",
    page_icon="bane.jpg",
    layout="centered"
)

# Google Doğrulama Kodu
st.markdown(
    '<meta name="google-site-verification" content="QHKdEcPEF68ahnKS-ncSUNcbOKoYDH4Z_g0yBYCmc4Y" />',
    unsafe_allow_html=True
)

# --- CSS: BEYAZ / AÇIK TEMA KODLARI ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stStatusWidget"] {visibility: hidden;}
    
    /* Beyaz / Açık Arka Plan */
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    
    /* Sol Menü (Sidebar) Açık Tema */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        color: #212529;
        border-right: 1px solid #e9ecef;
    }
    [data-testid="stSidebar"] * {
        color: #212529 !important;
    }
    
    /* Butonlar */
    .stButton button {
        border-radius: 8px;
        border: 1px solid #ced4da;
        background-color: #ffffff;
        transition: all 0.3s ease;
        color: #212529 !important;
    }
    .stButton button:hover {
        background-color: #e9ecef;
        border-color: #adb5bd;
    }

    /* Sohbet Giriş Kutusu */
    [data-testid="stChatInput"] {
        background-color: #ffffff !important;
        border: 1px solid #ced4da !important;
        border-radius: 30px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    
    [data-testid="stChatInput"] textarea {
        color: #212529 !important;
        background-color: transparent !important;
    }
    
    [data-testid="stChatInput"] div {
        background-color: transparent !important;
    }

    [data-testid="stBottom"], [data-testid="stBottomBlockContainer"] {
        background-color: #f8f9fa !important;
    }
    
    /* Popover */
    [data-testid="stPopover"] button {
        border-radius: 20px !important;
        background-color: #ffffff !important;
        border: 1px solid #ced4da !important;
        color: #212529 !important;
    }

    /* Kullanıcı Baloncuğu */
    .user-bubble {
        background-color: #0d6efd;
        color: #ffffff;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        max-width: 75%;
        margin-left: auto;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        font-size: 15px;
        word-wrap: break-word;
    }

    /* Berko Yanıtı */
    .berko-response {
        background-color: transparent;
        color: #212529;
        padding: 8px 0px;
        max-width: 85%;
        margin-right: auto;
        margin-bottom: 15px;
        font-size: 15px;
        word-wrap: break-word;
    }

    .thinking-text {
        color: #6c757d;
        font-style: italic;
        font-size: 14px;
        margin-bottom: 15px;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { opacity: 0.4; }
        50% { opacity: 1; }
        100% { opacity: 0.4; }
    }
    
    .img-preview-container {
        background-color: #ffffff;
        border: 1px solid #ced4da;
        border-radius: 12px;
        padding: 8px 12px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    </style>
""", unsafe_allow_html=True)

# Oturum Başlangıcı
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

# Dosya Deposu Hafızası
if "shared_files" not in st.session_state:
    st.session_state.shared_files = []

with st.sidebar:
    st.title("Berko AI")
    st.caption("Yapay Zeka Asistanın")
    st.divider()
    
    if not st.session_state.logged_in:
        st.info("Geçmiş sohbetler ve kişiselleştirilmiş deneyim için giriş yap.")
        if st.button("Google ile Giriş Yap", use_container_width=True):
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
            st.session_state.uploaded_image = None
            st.rerun()
            
    st.divider()
    
    # --- DOSYA DEPOSU & İNDİRME ALANI ---
    st.markdown("### 📁 Dosya Deposu & Arama")
    search_query = st.text_input("Dosya Ara...", placeholder="Dosya adı yaz...")
    
    new_shared_file = st.file_uploader("Sitemize Dosya Ekle", key="sidebar_file_uploader")
    if new_shared_file is not None:
        file_bytes = new_shared_file.read()
        if not any(f['name'] == new_shared_file.name for f in st.session_state.shared_files):
            st.session_state.shared_files.append({
                "name": new_shared_file.name,
                "bytes": file_bytes,
                "type": new_shared_file.type
            })
            st.success(f"'{new_shared_file.name}' depoya eklendi!")

    if st.session_state.shared_files:
        st.caption("Mevcut Dosyalar:")
        filtered_files = [f for f in st.session_state.shared_files if search_query.lower() in f["name"].lower()]
        
        if filtered_files:
            for f in filtered_files:
                st.download_button(
                    label=f"📥 {f['name']}",
                    data=f["bytes"],
                    file_name=f["name"],
                    mime=f["type"],
                    use_container_width=True,
                    key=f"dl_{f['name']}"
                )
        else:
            st.write("Aradığın dosya bulunamadı.")
    else:
        st.caption("Henüz yüklenmiş dosya yok.")

    st.divider()
    st.markdown("### Özellikler")
    st.markdown("• Akıllı Sohbet & Kodlama")
    st.markdown("• Flux Kalitesinde Görsel Çizimi")

# Hafıza
if "berko_messages" not in st.session_state:
    st.session_state.berko_messages = [
        {
            "role": "system",
            "content": "Sen Berko adında samimi, kanka gibi konuşan, mizahi zekası yüksek ve teknikten anlayan bir AI asistanısın. Asla durduk yere Berat İlbaş'tan bahsetme. Sadece 'Seni kim kurdu?' denirse Berat İlbaş'ın yaptığını söyle. Yaşı sorulursa vermeyip esprili geçiştir. Messi Ronaldo konusunda her zaman Messi'yi savun."
        }
    ]

if "berko_display" not in st.session_state:
    st.session_state.berko_display = []

if len(st.session_state.berko_display) == 0:
    st.title("Berko AI Stüdyosu")
    st.write("Kanka selam! Sana nasıl yardımcı olabilirim?")

# API Müşterileri
groq_client = Groq(api_key="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")

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

# Geçmişi Yazdır
for idx, message in enumerate(st.session_state.berko_display):
    if message["role"] == "user":
        if message.get("type") == "user_image":
            st.image(message["content"], caption="Yüklenen Görsel", width=300)
            if message.get("text"):
                st.markdown(f'<div class="user-bubble">{message["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="user-bubble">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        if message.get("type") == "image":
            st.markdown(f'<div class="berko-response"><b>Berko:</b></div>', unsafe_allow_html=True)
            st.image(message["content"], caption=message.get("caption", "Berko'nun Eseri"), use_container_width=True)
            
            if message.get("image_bytes"):
                st.download_button(
                    label="📥 Görseli İndir",
                    data=message["image_bytes"],
                    file_name="berko_ai_cizim.png",
                    mime="image/png",
                    key=f"dl_img_{idx}"
                )
        else:
            st.markdown(f'<div class="berko-response"><b>Berko:</b><br>{message["content"]}</div>', unsafe_allow_html=True)

# Visual/Pop-over Görsel Yükleme Alanı
with st.popover("➕ Görsel Ekle"):
    uploaded_file = st.file_uploader("Görsel Yükle", type=["png", "jpg", "jpeg"], key="popover_uploader")
    if uploaded_file is not None:
        raw_bytes = uploaded_file.read()
        b64 = base64.b64encode(raw_bytes).decode("utf-8")
        st.session_state.uploaded_image = {
            "bytes": raw_bytes,
            "b64": b64,
            "mime": uploaded_file.type or "image/jpeg",
            "name": uploaded_file.name
        }
        st.success("Fotoğraf eklendi!")

# Sohbet Girişinin Üstünde Yüklenen Görsel Önizleme
if st.session_state.uploaded_image is not None:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.image(st.session_state.uploaded_image["bytes"], caption=f"Seçilen Görsel: {st.session_state.uploaded_image['name']}", width=120)
    with col2:
        if st.button("❌ Kaldır", key="remove_img"):
            st.session_state.uploaded_image = None
            st.rerun()

prompt = st.chat_input("Berko'ya bir şeyler yaz veya resim çizdir...")

if prompt:
    if st.session_state.uploaded_image is not None:
        current_img = st.session_state.uploaded_image
        
        st.image(current_img["bytes"], caption="Yüklenen Görsel", width=300)
        st.markdown(f'<div class="user-bubble">{prompt}</div>', unsafe_allow_html=True)
        
        st.session_state.berko_display.append({
            "role": "user", 
            "type": "user_image", 
            "content": current_img["bytes"], 
            "text": prompt
        })
            
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown('<div class="thinking-text">bkl biraz knk resme bakıyorum...</div>', unsafe_allow_html=True)
        
        try:
            response = openrouter_client.chat.completions.create(
                model="google/gemini-2.0-flash-exp:free",
                messages=[
                    {
                        "role": "system",
                        "content": "Sen Berko adında samimi, kanka gibi konuşan bir AI asistanısın. Asla iç ses, analiz adımları yazma. Doğrudan Türkçe kanka tarzında cevap ver."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{current_img['mime']};base64,{current_img['b64']}"
                                },
                            },
                        ],
                    }
                ],
            )
            cevap = response.choices[0].message.content
            thinking_placeholder.empty()
            st.markdown(f'<div class="berko-response"><b>Berko:</b><br>{cevap}</div>', unsafe_allow_html=True)
            st.session_state.berko_display.append({"role": "assistant", "content": cevap})
            
            st.session_state.uploaded_image = None
            st.rerun()

        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"Görsel analiz hatası: {e}")
                    
    else:
        st.session_state.berko_messages.append({"role": "user", "content": prompt})
        st.session_state.berko_display.append({"role": "user", "content": prompt})
        
        st.markdown(f'<div class="user-bubble">{prompt}</div>', unsafe_allow_html=True)
            
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown('<div class="thinking-text">bkl biraz knk</div>', unsafe_allow_html=True)
        time.sleep(0.5)
        
        try:
            prompt_lower = prompt.lower()
            resim_kokenleri = ["resim", "resiam", "rsim", "resm", "çiz", "ciz", "görsel", "gorsel", "foto", "fotograf", "oluştur", "değiştir", "dönüştür"]
            is_image_request = any(koken in prompt_lower for koken in resim_kokenleri)
            
            chat_completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.berko_messages,
                temperature=0.7,
            )
            berko_yaniti = chat_completion.choices[0].message.content
            
            thinking_placeholder.empty()
            
            if is_image_request:
                harika_yanit = f"Hemen patlatıyorum kanka! İstediğin konsepti üst düzey kaliteye taşıyorum: '{prompt}'"
                st.markdown(f'<div class="berko-response"><b>Berko:</b><br>{harika_yanit}</div>', unsafe_allow_html=True)
                st.session_state.berko_display.append({"role": "assistant", "content": harika_yanit})
                
                cevirici_istegi = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Sen profesyonel bir AI görsel tasarımcısısın. Sadece İngilizce prompt yaz."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                gelismis_ingilizce_prompt = cevirici_istegi.choices[0].message.content.strip()
                
                encoded_prompt = urllib.parse.quote(gelismis_ingilizce_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&model=flux-realism&nologo=true&seed={int(time.time())}"
                
                img_data = requests.get(image_url).content
                
                st.image(image_url, caption=f"Berko'nun Eseri: {prompt}", use_container_width=True)
                
                st.download_button(
                    label="📥 Görseli İndir",
                    data=img_data,
                    file_name="berko_ai_cizim.png",
                    mime="image/png",
                    key=f"dl_img_new_{int(time.time())}"
                )
                
                st.session_state.berko_messages.append({"role": "assistant", "content": harika_yanit})
                st.session_state.berko_display.append({
                    "role": "assistant", 
                    "content": image_url, 
                    "type": "image", 
                    "caption": f"Berko'nun Eseri: {prompt}",
                    "image_bytes": img_data
                })
                
            else:
                st.markdown(f'<div class="berko-response"><b>Berko:</b><br>{berko_yaniti}</div>', unsafe_allow_html=True)
                st.session_state.berko_messages.append({"role": "assistant", "content": berko_yaniti})
                st.session_state.berko_display.append({"role": "assistant", "content": berko_yaniti})
                
        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"Hata oluştu: {e}")
'''

with open("app.py", "w", encoding="utf-8") as f:
    f.write(updated_code)

print("Code successfully updated with white theme CSS!")
