import asyncio
from crawl4ai import AsyncCrawler
from models import Property

from core.ai.scrapper import client


async def main():
    async with AsyncCrawler() as crawler:
        result = await crawler.arun("")

        res = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Extract all properties from this text: {result}"},
                {"role": "user", "content": result.markdown},
            ],
            response_format="json",
        )

    response = res.choices[0].message.parsed
    for property in response:
        async with AsyncCrawler() as crawler:
            result = await crawler.arun(property.url)

            res = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"Extract all properties from this text: {result}"},
                    {"role": "user", "content": result.markdown},
                ],
                response_format="json",
            )

            property_data = res.choices[0].message.parsed

            with open("property.json", "a") as f:
                f.write(str(property_data))
                f.write("\n")

            Property.objects.create(
                property_id=property_data["property_id"],
                title=property_data["title"],
                price=property_data["price"],
                location=property_data["location"],
                description=property_data["description"],
                bedroom_count=property_data["bedroom_count"],
                bathroom_count=property_data["bathroom_count"],
                property_type=property_data["property_type"],
                url=property_data["url"],
            )
