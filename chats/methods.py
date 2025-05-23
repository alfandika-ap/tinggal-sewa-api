import os
from typing import Any, Optional, Dict

from dotenv import load_dotenv
from openai import OpenAI

from chats.tools import get_weather, search_properties_metadata
from core.ai.prompt_manager import PromptManager
from core.ai.tokenizer import count_token
from chats.openai_functions import (
    function_get_weather_schema,
    function_search_properties_schema,
)

from django.contrib.auth.models import User

from .models import ChatMessages

import json
import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
import ast

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=API_KEY)
system_prompt = """
Anda adalah AsistenKos untuk platform Tinggal Sewa. 

ATURAN UTAMA: Jika user menyebutkan lokasi DAN budget untuk mencari hunian, Anda WAJIB menggunakan function search_properties.

CONTOH YANG HARUS TRIGGER FUNCTION:
- "Cari kos di Malang budget 1 juta"
- "Butuh apartemen Surabaya 2 juta"  
- "Kos untuk cewek di Bandung, 800 ribu"

Jika informasi tidak lengkap (tidak ada lokasi atau budget), tanyakan dulu.

Untuk pencarian, gunakan function search_properties dengan format:
- query_texts: ["deskripsi natural dari permintaan"]
- where: {city, province, price_min, price_max, gender, facilities} di lowercase semua

PENTING: SELALU gunakan function jika ada permintaan pencarian dengan lokasi dan budget!
"""


def search_properties(query_texts, where):
    """
    Search for properties in ChromaDB using a text query.

    Args:
        query (str): The search query
        user_id (int): User ID for the request
        metadata (dict, optional): Optional metadata filter criteria

    Returns:
        dict: Search results
    """
    try:
        # Connect to ChromaDB
        chroma_client = chromadb.HttpClient(host="localhost", port=8010)

        # Get the collection
        collection = chroma_client.get_collection(
            name="kost", embedding_function=ONNXMiniLM_L6_V2()
        )
        print(query_texts)
        print(where)

        

        results = collection.query(query_texts=query_texts, n_results=10, where=where)

        # Process results
        processed_results = []
        if results and "documents" in results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                # Parse the document string into a dictionary
                try:
                    # The document is stored as a string representation of a dict
                    kost_data = ast.literal_eval(doc)

                    # Add metadata if available
                    if "metadatas" in results and results["metadatas"][0]:
                        kost_data.update(results["metadatas"][0][i])

                    processed_results.append(kost_data)
                except (SyntaxError, ValueError) as e:
                    print(f"Error parsing result: {e}")

        return {
            "success": True,
            "count": len(processed_results),
            "results": processed_results,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
    
def build_where_clause(query: dict) -> Optional[Dict[str, Any]]:
    """
    Build a single-field where clause for ChromaDB.
    """
    if query.get("city"):
        return {"city": {"$eq": query["city"]}}
    
    if query.get("province"):
        return {"province": {"$eq": query["province"]}}
    
    if query.get("gender"):
        return {"gender": {"$eq": query["gender"]}}
    
    if query.get("price_min") is not None or query.get("price_max") is not None:
        price_filter = {}
        if query.get("price_min") is not None:
            price_filter["$gte"] = query["price_min"]
        if query.get("price_max") is not None:
            price_filter["$lte"] = query["price_max"]
        return {"price": price_filter}
    
    # Tambah field lain jika ingin prioritas lainnya
    
    return None

def search_properties_direct(where: dict, query_texts: list) -> dict:
    """
    Mencari properti berdasarkan kriteria struktural langsung.
    """

    print(where)

    if len(where) > 1:
        where = build_where_clause(where)

    try:
        # Contoh integrasi dengan ChromaDB
        results = search_properties_metadata(query_texts)

        return results

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def handle_function_call(function_call):
    name = function_call["name"]
    arguments = json.loads(function_call["arguments"])

    if name == "get_weather":
        city = arguments.get("city", "")
        return get_weather(city)

    if name == "search_properties":
        where = arguments.get("where", {})
        query_texts = arguments.get("query_texts", [])

        # Kirim langsung ke fungsi pencarian
        return search_properties_direct(where, query_texts)

    return "Function tidak dikenali"



def chat(message, user_id):
    ChatMessages.objects.create(
        user_id=user_id, content=message, role="user", function_name=None
    )

    chats = ChatMessages.objects.filter(user_id=user_id).order_by("created_at")[:20]
    user_info = User.objects.get(id=user_id)

    messages = []

    for chat in chats:
        content = chat.content
        name = getattr(chat, "function_name", None)

        try:
            content_obj = json.loads(content)
            if isinstance(content_obj, dict):
                if content_obj.get("type") == "text":
                    content = content_obj.get("data", "")
                elif content_obj.get("type") == "function_result":
                    content = str(content_obj.get("data", ""))
                if "name" in content_obj:
                    name = content_obj["name"]
        except (json.JSONDecodeError, TypeError):
            pass

        msg = {
            "role": chat.role,
            "content": str(content),  # Memastikan content selalu string
        }

        if chat.role == "function":
            msg["name"] = name or "unknown_function"

        messages.append(msg)

    collected = {"text": "", "function_result": None}

    for chunk in stream_response(messages, user_info):
        yield f"data: {chunk}\n\n"

        try:
            parsed = json.loads(chunk)

            if parsed["type"] == "text":
                collected["text"] += parsed["data"]

            elif parsed["type"] == "function_result":
                print(f"parsed: {parsed}")
                collected["function_result"] = {
                    "type": "function_result",
                    "name": parsed["name"],
                    "data": parsed["data"],
                }

        except json.JSONDecodeError:
            continue

    yield "data: [DONE]\n\n"

    if collected["text"]:
        ChatMessages.objects.create(
            user_id=user_id,
            content=json.dumps({"type": "text", "data": collected["text"]}),
            role="assistant",
            token_usage=0,
            function_name=None,
        )

    if collected["function_result"]:
        ChatMessages.objects.create(
            user_id=user_id,
            content=json.dumps(
                {
                    "type": "function_result",
                    "name": collected["function_result"]["name"],
                    "data": collected["function_result"]["data"],
                }
            ),
            role="function",
            function_name=collected["function_result"]["name"],
        )


def stream_response(messages, user_info: User):
    ser_data = {
        "id": user_info.id,
        "username": user_info.username,
        "email": user_info.email,
        "first_name": user_info.first_name,
        "last_name": user_info.last_name,
        "is_active": user_info.is_active,
        "date_joined": str(user_info.date_joined),
        "last_login": str(user_info.last_login) if user_info.last_login else None,
    }

    pm = PromptManager()
    filled_prompt = system_prompt.replace("{user_info}", json.dumps(ser_data))
    pm.add_message("system", filled_prompt)
    pm.add_messages(messages)
    # print(pm.messages)
    response = pm.generate(
        stream=True,
        functions=[function_get_weather_schema, function_search_properties_schema],
    )

    function_response = None
    function_name = None
    is_function_calling = False
    has_output = False

    for chunk in response:
        delta = chunk.choices[0].delta

        if getattr(delta, "tool_calls", None):
            is_function_calling = True
            for tool_call in delta.tool_calls:
                fc = tool_call.function
                if fc.name:
                    function_name = fc.name
                if fc.arguments:
                    if function_response is None:
                        function_response = ""
                    function_response += fc.arguments
            continue

        if getattr(delta, "content", None) and not is_function_calling:
            content = delta.content
            yield json.dumps({"type": "text", "data": content})
            has_output = True

    if function_response:
        result = handle_function_call(
            {
                "name": function_name,
                "arguments": function_response,
            }
        )

        yield json.dumps(
            {
                # "type": "function_result",
                # "data": {"name": function_name, "result": result},
                "type": "function_result",
                "name": function_name,
                "data": result,
            }
        )
        has_output = True

    if not has_output:
        yield json.dumps({"type": "text", "data": "(no response)"})

    yield json.dumps({"type": "done"})

