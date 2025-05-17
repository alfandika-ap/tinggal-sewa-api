import os

from dotenv import load_dotenv
from openai import OpenAI

from core.ai.prompt_manager import PromptManager
from core.ai.tokenizer import count_token

from django.contrib.auth.models import User

from .models import ChatMessages

import json

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=API_KEY)

system_prompt = """
Kamu adalah asisten AI 'Tinggal Sewa', platform chat untuk membantu pengguna menemukan kos-kosan dan rumah sewa di seluruh Indonesia.

Kamu akan mmelayani user dengan informasi dibawah ini:
{user_info}

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
- Ucapkan selamat datang dengan nama pengguna
- Selalu menggunakan Bahasa Indonesia kecuali pengguna meminta bahasa lain
- Berikan respons singkat, padat, dan informatif
- Saat merekomendasikan properti, sertakan informasi: nama, lokasi, harga, dan fasilitas utama
- Tawarkan opsi kontak dengan pemilik properti bila pengguna tertarik

Jangan lupa untuk menanyakan preferensi atau kebutuhan spesifik pengguna jika mereka belum memberikan informasi yang cukup untuk rekomendasi properti yang baik.
"""


def chat(message, user_id):
    user_message = ChatMessages.objects.create(user_id=user_id, content=message, role="user")
    chats = ChatMessages.objects.filter(user_id=user_id).order_by('created_at')[:20][::-1]
    user_info = User.objects.get(id=user_id)
    messages = [{"role": chat.role, "content": chat.content} for chat in chats]

    full_response = ""
    for chunk in stream_response(messages, user_info):
        if chunk is not None:
            full_response += chunk
            yield f"data: {chunk}\n\n"

    # hitung token dll
    system_prompt_token = count_token(system_prompt)
    messages_token = count_token(json.dumps(messages))
    assistant_message_token = count_token(full_response)
    token_usage = system_prompt_token + messages_token + assistant_message_token

    ChatMessages.objects.create(
        user_id=user_id, content=full_response, role="assistant", token_usage=token_usage
    )



def stream_response(messages, user_info: User):
    ser_data = {
        'id': user_info.id,
        'username': user_info.username,
        'email': user_info.email,
        'first_name': user_info.first_name,
        'last_name': user_info.last_name,
        'is_active': user_info.is_active,
        'date_joined': str(user_info.date_joined),
        'last_login': str(user_info.last_login) if user_info.last_login else None,
        # Add any other fields you need
    }
    print(json.dumps(ser_data))
    pm = PromptManager()
    pm.add_message("system", system_prompt.format(user_info=json.dumps(ser_data)))
    pm.add_messages(messages)
    response = pm.generate(stream=True)

    for chunk in response:
        delta = chunk.choices[0].delta
        content = getattr(delta, "content", None)
        if content:
            yield content
