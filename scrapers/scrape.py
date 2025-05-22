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
    existing_collections = await chroma.list_collections()
    if "kost" in existing_collections:
      await chroma.delete_collection(name="kost")
    collection = await chroma.create_collection(
        name="kost",
        embedding_function=ONNXMiniLM_L6_V2(),
    )

    processed_urls = set()

    async with AsyncWebCrawler() as crawler:
        
        result = await crawler.arun(url="https://mamikos.com/kos/singgahsini/")

        res = client.beta.chat.completions.parse(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a web scraper specialized in extracting kost (boarding house) listings from Mamikos. Extract ONLY unique listings from the provided page content. Ensure there are NO duplicate listings in your response. Each listing should have a unique URL."},
                {"role": "user", "content": f"Extract all unique kost listings from the following HTML content. For each listing, you MUST extract a unique URL. Also include: name, monthly price, location, facilities, gender policy, and available units. Format the data as specified in the KostList schema.\n\nPage content:\n{result.markdown}"}
            ],
            response_format=KostList,
        )

        response = res.choices[0].message.parsed
        
        print(f"Found {len(response.kosts)} kost listings")

        for kost in response.kosts:
            if not kost.url or not kost.url.strip():
                print("❌ Skipping kost with empty URL")
                continue
                
            # Skip duplicates
            if kost.url in processed_urls:
                print(f"⚠️ Skipping duplicate URL: {kost.url}")
                continue
                
            processed_urls.add(kost.url)
            
            print(f"Processing: {kost.title} - {kost.url}")
            
            detail_result = await crawler.arun(kost.url)

            detail_res = client.beta.chat.completions.parse(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "Extract detailed information about a kost (boarding house) from the provided HTML content. Return only factual information present on the page."},
                    {"role": "user", "content": f"Extract the complete details for this kost listing. Return in the Kost schema format.\n\nDetail page content:\n{detail_result.markdown}"}
                ],
                response_format=Kost,
            )

            kost_data = detail_res.choices[0].message.parsed

            if not kost_data.url or not kost_data.url.strip():
                kost_data.url = kost.url


            await collection.add(
                documents=[str(kost_data.model_dump())],
                ids=[kost_data.url],
                metadatas=[
                    {
                        "source": "mamikos",
                        "title": kost.title,
                        "address": kost.address,
                        "city": kost.city,
                        "province": kost.province,
                        "description": kost.description,
                        "price": kost.price,
                        "facilities": ", ".join(kost.facilities) if kost.facilities else "",
                        "rules": ", ".join(kost.rules) if kost.rules else "",
                        "contact": kost.contact,
                        "url": kost.url
                    }
                ],
            )

            with open("kost.log", "a", encoding="utf-8") as f:
                f.write(f"{kost_data.model_dump()}\n")

if __name__ == "__main__":
    asyncio.run(main())
