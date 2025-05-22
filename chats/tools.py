from typing import Optional, Dict
from pydantic import BaseModel
from chats.methods import search_properties
from core.ai.prompt_manager import PromptManager
import logging

logger = logging.getLogger(__name__)


class ChromaQuery(BaseModel):
    query_text: str
    title: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    address: Optional[str] = None
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    gender: Optional[str] = None



def get_weather(city: str) -> str:
    return f"Cuaca di {city} sekarang cerah dengan suhu 25°C."


def build_where_clause(query: ChromaQuery) -> Optional[Dict]:
    filters = []
    if query.city:
        filters.append({"city": {"$eq": query.city}})
    if query.province:
        filters.append({"province": {"$eq": query.province}})
    if query.address:
        filters.append({"address": {"$eq": query.address}})
    if query.price_min is not None:
        filters.append({"price": {"$gte": query.price_min}})
    if query.price_max is not None:
        filters.append({"price": {"$lte": query.price_max}})
    if query.gender:
        filters.append({"gender": {"$eq": query.gender}})
    return {"$and": filters} if filters else None


def search_properties_metadata(query: str) -> dict:
    system_prompt = """
    Kamu adalah asisten yang membantu membuat query pencarian untuk vector database (seperti ChromaDB).
    Ambil informasi dari pertanyaan user dan hasilkan format JSON berikut:

    {
        "query_text": "Buat versi query yang lebih bermakna dan deskriptif secara semantik dari pertanyaan asli.",
        "title": "Kost di Jakarta Pusat khusus pria atau wanita peremuan dan secara detailnya",
        "city": "Jakarta Pusat",
        "province": "DKI Jakarta",
        "address": null,
        "price_min": 1000000,
        "price_max": 2000000,
        "gender": "pria" atau "wanita" lowercase
    }

    Semua nilai opsional boleh null jika tidak disebut. 
    "price_min" dan "price_max" harus berupa angka (jika ada). 
    "query_text" WAJIB lebih semantik daripada pertanyaan asli.
    """

    pm = PromptManager()
    pm.add_message("system", system_prompt)
    pm.add_message("user", f"Pertanyaan: {query}")

    try:
        extracted: ChromaQuery = pm.generate_structured_json_schema(ChromaQuery)
    except Exception as e:
        logger.error(f"Gagal mengurai query dari AI: {str(e)}")
        raise ValueError("Gagal mengurai query. Silakan coba lagi.")

    logger.debug(f"Query Extracted: {extracted.json()}")

    where_clause = build_where_clause(extracted)
    search = search_properties(extracted.query_text, where_clause)

    return {
        "data": search,
        "query_texts": [extracted.query_text],
        "where": where_clause
    }
