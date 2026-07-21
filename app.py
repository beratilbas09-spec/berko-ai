
import streamlit as st
from groq import Groq

# Tarayıcı sekmesinin adını ve robot logosunu ayarlama
st.set_page_config(
    page_title="Berko",
    page_icon="🤖"
)

st.title("🤖 Berko ile Sohbet Et")
st.write("Kanka selam, ben Berko! Ne konuşuyoruz?")

client = Groq(api_key="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")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "Senin adın Berko. Sana adın veya ismin sorulduğunda kesinlikle Berko olduğunu söyle. Kullanıcılara samimi, arkadaş canlısı ve biraz da esprili bir tarzda yanıt veren bir yapay zeka asistanısın."
        }
    ]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Berko'ya bir şeyler yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages
            )
            berko_yaniti = response.choices[0].message.content
            st.markdown(berko_yaniti)
            st.session_state.messages.append({"role": "assistant", "content": berko_yaniti})
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")