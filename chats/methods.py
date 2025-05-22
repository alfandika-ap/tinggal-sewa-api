import os

from dotenv import load_dotenv
from openai import OpenAI

# from chats.tools import get_weather
from core.ai.prompt_manager import PromptManager
from core.ai.tokenizer import count_token
from chats.openai_functions import function_get_weather_schema, function_search_properties_schema

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
Kamu adalah asisten AI 'Tinggal Sewa', platform chat untuk membantu pengguna menemukan kos-kosan dan rumah sewa di seluruh Indonesia.
Kamu juga mempunyai tool untuk mengetahui cuaca di suatu kota.

Kamu akan melayani user dengan informasi dibawah ini:
{user_info}

JIKA ADA MARKDOWN JANGAN DI PUTUSIN, KARENA MARKDOWN ITU BISA DI BACA OLEH USER

"""

def handle_function_call(function_call):
    name = function_call["name"]
    arguments = json.loads(function_call["arguments"])
    
    if name == "get_weather":
        city = arguments.get("city", "")
        return city
    return "Function tidak dikenali"


def chat(message, user_id):
    ChatMessages.objects.create(
        user_id=user_id,
        content=message,
        role="user",
        function_name=None
    )

    chats = ChatMessages.objects.filter(user_id=user_id).order_by('created_at')[:20]
    user_info = User.objects.get(id=user_id)

    messages = []

    for chat in chats:
        content = chat.content
        name = getattr(chat, "function_name", None)

        try:
            content_obj = json.loads(content)
            if isinstance(content_obj, dict) and "data" in content_obj:
                content = content_obj["data"]
                if "name" in content_obj:
                    name = content_obj["name"]
        except (json.JSONDecodeError, TypeError):
            pass

        msg = {
            "role": chat.role,
            "content": content
        }

        if chat.role == "function":
            msg["name"] = name or "unknown_function"

        messages.append(msg)

    collected = {
        "text": "",
        "function_result": None
    }

    for chunk in stream_response(messages, user_info):
        yield f"data: {chunk}\n\n"

        try:
            parsed = json.loads(chunk)

            if parsed["type"] == "text":
                collected["text"] += parsed["data"]

            elif parsed["type"] == "function_result":
                collected["function_result"] = {
                    "name": parsed['data']['name'],
                    "data": parsed['data']['result']
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
            function_name=None
        )

    if collected["function_result"]:
        ChatMessages.objects.create(
            user_id=user_id,
            content=json.dumps({
                "type": "function_result",
                "name": collected["function_result"]["name"],
                "data": collected["function_result"]["data"],
            }),
            role="function",
            function_name=collected["function_result"]["name"],
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
    }

    pm = PromptManager()
    pm.add_message("system", system_prompt.format(user_info=json.dumps(ser_data)))
    pm.add_messages(messages)
    response = pm.generate(stream=True, functions=[function_get_weather_schema, function_search_properties_schema])

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

    # Jalankan dan kirim hasil function_call jika ada
    if function_response:
        result = handle_function_call({
            "name": function_name,
            "arguments": function_response,
        })

        yield json.dumps({
            "type": "function_result",
            "data": {
                "name": function_name,
                "result": result
            }
        })
        has_output = True

    if not has_output:
        yield json.dumps({"type": "text", "data": "(no response)"})

    yield json.dumps({"type": "done"})


def search_properties(query, where_condition):
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
            name="kost",
            embedding_function=ONNXMiniLM_L6_V2()
        )
        
        results = collection.query(query_texts=[query], n_results=10, where=where_condition)
        
        # Process results
        processed_results = []
        if results and 'documents' in results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                # Parse the document string into a dictionary
                try:
                    # The document is stored as a string representation of a dict
                    kost_data = ast.literal_eval(doc)
                    
                    # Add metadata if available
                    if 'metadatas' in results and results['metadatas'][0]:
                        kost_data.update(results['metadatas'][0][i])
                        
                    processed_results.append(kost_data)
                except (SyntaxError, ValueError) as e:
                    print(f"Error parsing result: {e}")
                    
        return {
            "success": True,
            "count": len(processed_results),
            "results": processed_results
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

