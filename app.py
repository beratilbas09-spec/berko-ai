
from groq import Groq

# Groq istemcisi (Groq API Key'ini buraya koy)
groq_client = Groq(api_key="BURAYA_GROQ_API_KEY_YAZ")

# Görsel analiz isteği
response = groq_client.chat.completions.create(
    model="llama-3.2-11b-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Bu görselde ne var? Türkçe açıkla."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{uploaded_file_base64}"
                    },
                },
            ],
        }
    ],
)

berko_yaniti = response.choices[0].message.content
