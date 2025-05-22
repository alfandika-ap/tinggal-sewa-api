import os
import sys
import django

# Setup environment Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

import asyncio
from crawl4ai import AsyncWebCrawler
from core.ai.scraper import client
from scrapers.models import KostList, Kost
import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

async def main():
    chroma = await chromadb.AsyncHttpClient("localhost", 8010)

    # Check and delete existing collection
    existing_collections = await chroma.list_collections()
    print("existing_collections =", existing_collections)

    if "kost" in existing_collections:
        print("🔁 Deleting existing 'kost' collection...")
        await chroma.delete_collection(name="kost")

    # Create new collection
    collection = await chroma.create_collection(
        name="kost",
        embedding_function=ONNXMiniLM_L6_V2(),
    )

    async with AsyncWebCrawler() as crawler:
        # 1. Scrape halaman list untuk dapatkan list kost dan URL detail-nya
        list_page_url = "https://papikost.com/search/?act=filter&keyword=malang"
        list_result = await crawler.arun(url=list_page_url)

        list_res = client.beta.chat.completions.parse(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a web scraper. Extract a list of all available kosts from the following page. "
                        "Return them in the given schema."
                    ),
                },
                {"role": "user", "content": list_result.markdown},
            ],
            response_format=KostList,
        )

        kost_list = list_res.choices[0].message.parsed

        # 2. Loop tiap kost, scrape detail halaman detail masing-masing kost
        for kost_summary in kost_list.kosts:
            if not kost_summary.url or not kost_summary.url.strip():
                print("❌ Skipping kost with empty URL in list")
                continue

            print(f"➡️ Scraping detail kost: {kost_summary.url}")
            detail_result = await crawler.arun(kost_summary.url)

            detail_res = client.beta.chat.completions.parse(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "system",
                        "content": "Extract kost detail from the following text, including image URL. Return in the given schema. for gender use lowercase  pria or wanita",
                    },
                    {"role": "user", "content": detail_result.markdown},
                ],
                response_format=Kost,
            )

            kost_data = detail_res.choices[0].message.parsed

            if not kost_data.url or not kost_data.url.strip():
                print("❌ Skipping kost with empty URL in detail")
                continue

            # Simpan ke ChromaDB
            await collection.add(
                documents=[str(kost_data.model_dump())],
                ids=[kost_data.url],
                metadatas=[
                    {
                        "source": "mamikos",
                        "title": kost_data.title,
                        "address": kost_data.address,
                        "city": kost_data.city,
                        "province": kost_data.province,
                        "description": kost_data.description,
                        "price": kost_data.price,
                        "facilities": kost_data.facilities,
                        "rules": kost_data.rules,
                        "contact": kost_data.contact,
                        "url": kost_data.url,
                        "image_url": kost_data.image_url,
                        "gender": kost_data.gender
                    }
                ],
            )

            # Log data ke file
            with open("kost.log", "a", encoding="utf-8") as f:
                f.write(f"{kost_data.model_dump()}\n")

if __name__ == "__main__":
    asyncio.run(main())
