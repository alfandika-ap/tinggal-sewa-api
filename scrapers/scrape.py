import asyncio
from crawl4ai import AsyncWebCrawler
from core.ai.scraper import client
from scrapers.models import KostList, Kost
import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

async def main():
    chroma = await chromadb.AsyncHttpClient("localhost", 8010)
    await chroma.delete_collection(name="kost")
    collection = await chroma.create_collection(
        name="kost",
        embedding_function=ONNXMiniLM_L6_V2(),
    )

    async with AsyncWebCrawler() as crawler:
        
        result = await crawler.arun(url="https://mamikos.com/kost/kost-jakarta-murah")

        res = client.beta.chat.completions.parse(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a web scraper. Extract a list of all available kosts from the following page. Return them in the given schema."},
                {"role": "user", "content": result.markdown},
            ],
            response_format=KostList,
        )

        response = res.choices[0].message.parsed
        

        for kost in response.kosts:
            
            detail_result = await crawler.arun(kost.url)

            detail_res = client.beta.chat.completions.parse(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "Extract kost detail from the following text. Return in the given schema."},
                    {"role": "user", "content": detail_result.markdown},
                ],
                response_format=Kost,
            )

            kost_data = detail_res.choices[0].message.parsed

            if not kost_data.url or not kost_data.url.strip():
                print("❌ Skipping kost with empty URL")
                continue


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
                        "facilities": kost.facilities,
                        "rules": kost.rules,
                        "contact": kost.contact,
                        "url": kost.url
                    }
                ],
            )

if __name__ == "__main__":
    asyncio.run(main())
