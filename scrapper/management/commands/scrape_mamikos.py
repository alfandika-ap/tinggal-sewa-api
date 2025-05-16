import asyncio
from crawl4ai import AsyncCrawler, BrowserConfig, ProxyConfig
from models import Property

from core.ai.proxy import config
from core.ai.scrapper import client

proxy = ProxyConfig(**config)

browser_config = BrowserConfig(
    proxy=proxy
)

async def main():
    async with AsyncCrawler(browser_config=browser_config) as crawler:
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

            with open("property.json", "a") as f:
                f.write(str(property_data) + "\n")


            await Property.objects.create(
                property_id=property_data["property_id"],
                title=property_data["title"],
                price=property_data["price"],
                location=property_data["location"],
                rules=property_data["rules"],
                room_specs=property_data["room_specs"],
                url=property_data["url"],
            )


if __name__ == "__main__":
    asyncio.run(main())
