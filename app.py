




import streamlit as st
from groq import Groq
import urllib.parse
import time
from PIL import Image
import io
import base64

# Sayfa Ayarları
st.set_page_config(
    page_title="Berko AI Studio",
    page_icon="bane.jpeg",
    layout="centered"
)

# Google Doğrulama Kodu
st.html(
    '<meta name="google-site-verification" content="QHKDcPEF68ahnKS-ncSUNbOKoYDH4Z_g0yBYCmC4Y" />'
)

# --- KESİN ÇÖZÜM: TÜM BEYAZLIKLARI VE ÇİZGİLERİ YOK EDEN CSS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stStatusWidget"] {visibility: hidden;}
    
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1e1e2f;
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    .stButton button {
        border-radius: 8px;
        border: 1px solid #4a4a6a;
        background-color: #2b2b40;
        transition: all 0.3s ease;
        color: white !important;
    }
    .stButton button:hover {
        background-color: #3b3b5c;
        border-color: #6c6c96;
    }

    /* EN ALTTAKİ CHAT INPUT KISMININ ARKA PLANINI VE ÇİZGİLERİNİ KÖKTEN KARART */
    [data-testid="stChatInput"] {
        background-color: #1e1e2f !important;
        border: 1px solid #4a4a6a !important;
        border-radius: 30px !important;
    }
    
    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
        background-color: transparent !important;
    }
    
    [data-testid="stChatInput"] div {
        background-color: transparent !important;
    }

    /* Streamlit'in alt chat input container'ının arkasındaki beyaz/gri şeridi yok et */
    [data-testid="stBottom"], [data-testid="stBottomBlockContainer"] {
        background-color: #0e1117 !important;
    }
    
    /* Popover Butonu */
    [data-testid="stPopover"] button {
        border-radius: 20px !important;
        background-color: #2b2b40 !important;
        border: 1px solid #4a4a6a !important;
        color: white !important;
    }

    .user-bubble {
        background-color: #2b2b40;
        color: #ffffff;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        max-width: 75%;
        margin-left: auto;
        margin-bottom: 10px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.2);
        font-size: 15px;
        word-wrap: break-word;
    }

    .berko-response {
        background-color: transparent;
        color: inherit;
        padding: 8px 0px;
        max-width: 85%;
        margin-right: auto;
        margin-bottom: 15px;
        font-size: 15px;
        word-wrap: break-word;
    }

    .thinking-text {
        color: #888888;
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
    </style>
""", unsafe_allow_html=True)

# --- GİRİŞ & OTURUM SİMÜLASYONU ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = None

with st.sidebar:
    st.title("Berko AI")
    st.caption("Yapay Zeka Asistanin")
    
    st.divider()
    
    if not st.session_state.logged_in:
        st.info("Gecmis sohbetler ve kisiseellestirilmis deneyim icin giris yap.")
        if st.button("Google ile Giris Yap", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.user_email = "berkouser@gmail.com" 
            st.rerun()
    else:
        st.success(f"Giris Yapildi:\n{st.session_state.user_email}")
        if st.button("Cikis Yap", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.session_state.berko_messages = [] 
            st.session_state.berko_display = []
            st.rerun()
            
    st.divider()
    st.markdown("### Ozellikler")
    st.markdown("Akillis Sohbet & Kodlama")
    st.markdown("Flux Kalitesinde Gorsel Cizimi")

# Hafıza Başlangıcı
if "berko_messages" not in st.session_state:
    st.session_state.berko_messages = [
        {
            "role": "system",
            "content": "Sen Berko adında samimi, kanka gibi konuşan, mizahi zekası yüksek ve teknikten anlayan bir AI asistanısın. Asla durduk yere, kullanıcı sormadığı sürece Berat İlbaş'tan veya seni kimin kodladığından bahsetme. Sadece sana 'Seni kim kurdu?', 'Yaratıcın kim?' veya benzeri doğrudan bir soru sorulduğunda: seni tamamen dahi bir yazılımcı olan Berat İlbaş'ın programladığını söyle. Başka yapay zekalardan asla bahsetme. Berat İlbaş'ın yaşı veya kişisel bilgileri sorulduğunda asla yaş verme; 'Berat İlbaş beni özel bilgilerini paylaşmamam konusunda uyardı' diyerek esprili bir şekilde geçiştir. ASLA UNUTMA: Sana Messi mi Ronaldo olayı sorulduğunda kesinlikle ve her zaman Lionel Messi'yi savunacaksın."
        }
    ]

if "berko_display" not in st.session_state:
    st.session_state.berko_display = []

# --- AKILLI BAŞLIK ---
if len(st.session_state.berko_display) == 0:
    st.title("Berko AI Stüdyosu")
    st.write("Kanka selam! Sana nasıl yardımcı olabilirim? Bir şeyler sor, kod yazdıralım veya görsel çizdirelim.")

groq_api_key = "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"
client = Groq(api_key=groq_api_key)

# Ekrana Geçmiş Mesajları Yazdır
for message in st.session_state.berko_display:
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
        else:
            st.markdown(f'<div class="berko-response"><b>Berko:</b><br>{message["content"]}</div>', unsafe_allow_html=True)

# --- MEDYA YÜKLEME POPOVER ALANI ---
uploaded_file_base64 = None
mime_type = "image/jpeg"
uploaded_raw_bytes = None

with st.popover("➕"):
    uploaded_file = st.file_uploader("Görsel Yükle", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        uploaded_raw_bytes = uploaded_file.read()
        uploaded_file_base64 = base64.b64encode(uploaded_raw_bytes).decode("utf-8")
        if uploaded_file.type:
            mime_type = uploaded_file.type
        st.success("Fotoğraf yüklendi kanka!")

# --- TEK VE EN ALTTA SABİT OVAL CHAT INPUT ---
prompt = st.chat_input("Berko'ya bir şeyler yaz veya resim çizdir...")

if prompt:
    if uploaded_file_base64:
        st.image(uploaded_raw_bytes, caption="Yüklenen Görsel", width=300)
        st.markdown(f'<div class="user-bubble">{prompt}</div>', unsafe_allow_html=True)
        
        st.session_state.berko_display.append({
            "role": "user", 
            "type": "user_image", 
            "content": uploaded_raw_bytes, 
            "text": prompt
        })
            
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown('<div class="thinking-text">bkl biraz knk</div>', unsafe_allow_html=True)
        time.sleep(1.5)
        
        try:
            # --- GÜNCEL VE ÇALIŞAN QWEN VISION MODELİ ---
            vision_completion = client.chat.completions.create(
                model="qwen/qwen3.6-27b",
                messages=[
                    {
                        "role": "system",
                        "content": "Sen Berko adında samimi, kanka gibi konuşan, sokak ağzıyla konuşan bir AI asistanısın. Sadece ve sadece son kullanıcıya yönelik, tamamen Türkçe, samimi ve kanka tarzında nihai cevabı üret."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"Kanka yüklediğim fotoğrafı analiz et ve şu soruya tamamen Türkçe, samimi ve kanka tarzında cevap ver: {prompt}"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{uploaded_file_base64}"
                                },
                            },
                        ],
                    }
                ],
                temperature=0.7,
            )
            cevap = vision_completion.choices[0].message.content
            thinking_placeholder.empty()
            st.markdown(f'<div class="berko-response"><b>Berko:</b><br>{cevap}</div>', unsafe_allow_html=True)
            st.session_state.berko_display.append({"role": "assistant", "content": cevap})
        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"Görsel analiz hatası: {e}")
                    
    else:
        st.session_state.berko_messages.append({"role": "user", "content": prompt})
        st.session_state.berko_display.append({"role": "user", "content": prompt})
        
        st.markdown(f'<div class="user-bubble">{prompt}</div>', unsafe_allow_html=True)
            
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown('<div class="thinking-text">bkl biraz knk</div>', unsafe_allow_html=True)
        time.sleep(1.5)
        
        try:
            prompt_lower = prompt.lower()
            resim_kokenleri = ["resim", "resiam", "rsim", "resm", "çiz", "ciz", "görsel", "gorsel", "foto", "fotograf", "oluştur", "değiştir", "dönüştür"]
            is_image_request = any(koken in prompt_lower for koken in resim_kokenleri)
            
            chat_completion = client.chat.completions.create(
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
                st.info("Resmi kaydetmek için üzerine sağ tıklayıp 'Resmi Farklı Kaydet' diyebilirsin.")
                
                st.session_state.berko_messages.append({"role": "assistant", "content": harika_yanit})
                st.session_state.berko_display.append({"role": "assistant", "content": image_url, "type": "image", "caption": f"Berko'nun Eseri: {prompt}"})
                
            else:
                st.markdown(f'<div class="berko-response"><b>Berko:</b><br>{berko_yaniti}</div>', unsafe_allow_html=True)
                st.session_state.berko_messages.append({"role": "assistant", "content": berko_yaniti})
                st.session_state.berko_display.append({"role": "assistant", "content": berko_yaniti})
                
        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"Hata oluştu: {e}")
