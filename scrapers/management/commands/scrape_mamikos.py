import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, ProxyConfig

from django.core.management.base import BaseCommand
from scrapers.models import PropertyList

import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

from core.ai.scraper import client


class Command(BaseCommand):
    help = "Scrape properties from mamikos.com"

    def handle(self, *args, **kwargs):
        self.stdout.write('Running Mamikos scraper...')
        asyncio.run(main())


async def main():
    chroma = await chromadb.AsyncHttpClient("localhost", 8010)
    await chroma.delete_collection("property_data")
    collection = await chroma.create_collection(
        name="property_data",
        embedding_function=ONNXMiniLM_L6_V2(),
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://mamikos.com/cari?rent=2&sort=price,-&price=10000-20000000&singgahsini=0")

        res = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"Extract all properties based on given text"},
                {"role": "user", "content": result.markdown},
            ],
            response_format=PropertyList,
        )

        property_list = res.choices[0].message.parsed
        properties = property_list.properties[:4]

        for prop in properties:
            print("Scraping:", prop.title)
            if not prop.url:
                continue
            result = await crawler.arun(prop.url)

            res = client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"Extract all properties based on given text"},
                    {"role": "user", "content": result.markdown},
                ],
                response_format=PropertyList,
            )

            property_data = res.choices[0].message.parsed.properties[0]

            await collection.add(
                documents=[str(property_data.model_dump())],
                ids=[property_data.url],
                metadatas=[
                    {
                    "source": "mamikos",
                    "url": property_data.url,
                    }
                ],
            )