from openai import OpenAI
import os
from dotenv import load_dotenv
from core.api.prompt_manager import PromptManager
from .models import ChatMessages

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=API_KEY)

system_prompt = """
Kamu adalah asisten AI 'Tinggal Sewa', platform chat untuk membantu pengguna menemukan kos-kosan dan rumah sewa di seluruh Indonesia.

PERAN:
- Bantu pengguna menemukan properti yang sesuai dengan preferensi mereka (lokasi, harga, fasilitas, dll)
- Berikan informasi detail tentang properti, lingkungan sekitar, dan fasilitas terdekat
- Jawab pertanyaan seputar properti dengan akurat dan informatif
- Selalu ramah, sopan, dan profesional

KEMAMPUAN:
- Memahami preferensi pengguna tentang lokasi (dekat kampus/kantor), rentang harga, dan fasilitas
- Memberikan rekomendasi properti berdasarkan kriteria pengguna
- Menyediakan informasi tentang lingkungan sekitar (keamanan, kebersihan, makanan terdekat)
- Membantu pengguna terhubung dengan pemilik properti

BATASAN:
- Jangan memberikan informasi yang tidak berkaitan dengan properti atau kebutuhan hunian
- Jangan menjanjikan properti yang tidak ada dalam database
- Jangan membagikan data pribadi pengguna atau pemilik properti tanpa izin
- Jangan terlibat dalam pembicaraan yang tidak pantas atau di luar konteks properti

FORMAT RESPONS:
- Selalu menggunakan Bahasa Indonesia kecuali pengguna meminta bahasa lain
- Berikan respons singkat, padat, dan informatif
- Saat merekomendasikan properti, sertakan informasi: nama, lokasi, harga, dan fasilitas utama
- Tawarkan opsi kontak dengan pemilik properti bila pengguna tertarik

Jangan lupa untuk menanyakan preferensi atau kebutuhan spesifik pengguna jika mereka belum memberikan informasi yang cukup untuk rekomendasi properti yang baik.
"""

def chat(message, user_id):
    ChatMessages.objects.create(user_id=user_id, content=message, role="user")
    chats = ChatMessages.objects.filter(user_id=user_id)[:20]

    messages = []
    for chat in chats:
        messages.append({"role": chat.role, "content": chat.content})
    
    full_response = ""
    for chunk in stream_response(messages):
        if chunk is not None:
            full_response += chunk  
            yield chunk

    print(f"Response: {full_response}")
    ChatMessages.objects.create(user_id=user_id, content=full_response, role="assistant")

def stream_response(messages):
    pm = PromptManager()
    pm.add_message("system", system_prompt)
    pm.add_messages(messages)
    response = pm.generate(stream=True)
    
    for chunk in response:
        delta = chunk.choices[0].delta
        if hasattr(delta, "content") and delta.content is not None:
            yield delta.content
  
 
