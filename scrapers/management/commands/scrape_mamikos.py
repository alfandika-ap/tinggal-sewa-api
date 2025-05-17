import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, ProxyConfig

from django.core.management.base import BaseCommand
from scrapers.models import Property

import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

from core.ai.proxy import config
from core.ai.scraper import client

proxy = ProxyConfig(**config)

config = BrowserConfig(
    proxy=proxy
)

class Command(BaseCommand):
    help = "Scrape properties from mamikos.com"

    def handle(self, *args, **kwargs):
        self.stdout.write('Running Mamikos scraper...')
        asyncio.run(main())


async def main():
    chroma = await chromadb.AsyncHttpClient("localhost", 8010)
    collection = await chroma.create_collection(
        name="property_data",
        embedding_function=ONNXMiniLM_L6_V2(),
    )
    async with AsyncWebCrawler(config=config) as crawler:
        result = await crawler.arun("https://mamikos.com/cari?rent=2&sort=price,-&price=10000-20000000&singgahsini=0")

        res = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Extract all properties from this text: {result}"},
                {"role": "user", "content": result if isinstance(result, str) else result.markdown},
            ],
            response_format="json",
        )

        properties = res.choices[0].message.parsed

        for prop in properties:
            result = await crawler.arun(prop["url"])

            res = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"Extract all properties from this text: {result}"},
                    {"role": "user", "content": result if isinstance(result, str) else result.markdown},
                ],
                response_format="json",
            )

            property_data = res.choices[0].message.parsed

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