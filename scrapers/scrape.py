import os
import sys
import django

# Setup environment Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

import asyncio
from crawl4ai import AsyncWebCrawler, ProxyConfig, BrowserConfig
from core.ai.scraper import client
from core.ai.proxy import get_proxy_config
from scrapers.models import KostList, Kost
import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

proxy_data = get_proxy_config()

proxy_config = ProxyConfig(
    server=proxy_data["server"],
    username=proxy_data["username"],
    password=proxy_data["password"]
)

config = BrowserConfig(proxy_config=proxy_config)

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

    async with AsyncWebCrawler(config=config) as crawler:
        # 1. Scrape halaman list untuk dapatkan list kost dan URL detail-nya
        list_page_url = "https://www.cari-kos.com/search/kos/jawa-timur/kota-malang?price-from=0&price-to=10000000"
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
                        "content": (
                            "You are an expert web scraper specializing in Indonesian kost (boarding house) data extraction. "
                            "Your task is to extract comprehensive kost details from the provided HTML/markdown content.\n\n"
                            
                            "EXTRACTION REQUIREMENTS:\n"
                            "1. TITLE: Extract the main kost name/title, clean and concise\n"
                            "2. PRICE: Extract monthly rent price as integer (remove 'Rp', '.', ',', '/bulan', etc.)\n"
                            "3. ADDRESS: Extract full street address in lowercase, include street name and number\n"
                            "4. CITY: Extract city name only in lowercase (e.g., 'malang', 'surabaya')\n"
                            "5. PROVINCE: Extract province name only in lowercase (e.g., 'jawa timur', 'jawa barat')\n"
                            "6. GENDER: Use only 'pria', 'wanita', or 'campur' (mixed) in lowercase\n"
                            "7. DESCRIPTION: Extract main description, max 500 characters, clean formatting\n"
                            "8. FACILITIES: Extract as array of facility names (e.g., ['wifi', 'ac', 'kamar mandi dalam'])\n"
                            "9. RULES: Extract house rules as array (e.g., ['tidak merokok', 'jam malam 22:00'])\n"
                            "10. CONTACT: Extract phone number or WhatsApp number, clean format\n"
                            "11. IMAGE_URL: Extract the main/first property image URL (full URL, not relative)\n"
                            "12. URL: Use the current page URL being scraped\n\n"
                            
                            "DATA CLEANING RULES:\n"
                            "- Remove all HTML tags and excess whitespace\n"
                            "- Convert prices to pure integers (1500000 not '1.500.000')\n"
                            "- Standardize facility names (use common Indonesian terms)\n"
                            "- Ensure addresses are complete but concise\n"
                            "- Handle missing data gracefully (return empty string/array, not null)\n"
                            "- Validate image URLs are complete and accessible\n\n"
                            
                            "COMMON FACILITY TRANSLATIONS:\n"
                            "- Air conditioning → 'ac'\n"
                            "- WiFi/Internet → 'wifi'\n"
                            "- Private bathroom → 'kamar mandi dalam'\n"
                            "- Shared bathroom → 'kamar mandi luar'\n"
                            "- Kitchen → 'dapur'\n"
                            "- Parking → 'parkir'\n"
                            "- Security → 'keamanan 24 jam'\n"
                            "- Laundry → 'laundry'\n"
                            "- Furnished → 'furnished'\n"
                            "- TV → 'tv'\n"
                            "- Refrigerator → 'kulkas'\n"
                            "- Water heater → 'water heater'\n"
                            "- Wardrobe → 'lemari'\n"
                            "- Bed → 'kasur'\n"
                            "- Study desk → 'meja belajar'\n"
                            "- Balcony → 'balkon'\n\n"
                            
                            "PRICE EXTRACTION RULES:\n"
                            "- Look for patterns like 'Rp 1.500.000', 'Rp1,500,000', '1.5 juta'\n"
                            "- Convert text numbers: 'juta' = 1,000,000, 'ribu' = 1,000\n"
                            "- Extract only monthly prices, ignore daily/weekly rates\n"
                            "- If multiple prices exist, take the base/starting price\n\n"
                            
                            "GENDER DETECTION RULES:\n"
                            "- Look for keywords: 'pria', 'laki-laki', 'cowok', 'putra' → 'pria'\n"
                            "- Look for keywords: 'wanita', 'perempuan', 'cewek', 'putri' → 'wanita'\n"
                            "- Look for keywords: 'campur', 'mixed', 'pria/wanita' → 'campur'\n"
                            "- Default to 'campur' if unclear\n\n"
                            
                            "ADDRESS STANDARDIZATION:\n"
                            "- Use full street address including RT/RW if available\n"
                            "- Format: 'jl. veteran no. 123, malang'\n"
                            "- Remove unnecessary words like 'alamat:', 'lokasi:'\n"
                            "- Keep important landmarks if mentioned\n\n"
                            
                            "If any required field cannot be found, return appropriate empty values but do not skip the field entirely."
                        ),
                    },
                    {"role": "user", "content": f"Current page URL: {kost_summary.url}\n\nPage content to extract from:\n{detail_result.markdown}"},
                ],
                response_format=Kost,
            )

            kost_data = detail_res.choices[0].message.parsed

            if not kost_data.url or not kost_data.url.strip():
                print("❌ Skipping kost with empty URL in detail")
                continue

            # Helper functions for safe data conversion
            def safe_string(value):
                return "" if value is None else str(value)

            def safe_int(value):
                """Convert value to int, return 0 if None or invalid"""
                if value is None:
                    return 0
                try:
                    # Handle string numbers
                    if isinstance(value, str):
                        # Remove non-numeric characters except digits
                        cleaned = ''.join(filter(str.isdigit, value))
                        return int(cleaned) if cleaned else 0
                    return int(value)
                except (ValueError, TypeError):
                    return 0

            def safe_list_to_string(value):
                """Convert list to comma-separated string"""
                if value is None:
                    return ""
                if isinstance(value, list):
                    return ", ".join(str(item) for item in value if item)
                return str(value)

            # Convert price to integer for proper numeric operations
            price_int = safe_int(kost_data.price)

            # Simpan ke ChromaDB dengan proper data types
            await collection.add(
                documents=[str(kost_data.model_dump())],
                ids=[kost_data.url],
                metadatas=[
                    {
                        "source": "papikost",
                        "title": safe_string(kost_data.title),
                        "address": safe_string(kost_data.address),
                        "city": safe_string(kost_data.city),
                        "province": safe_string(kost_data.province),
                        "description": safe_string(kost_data.description),
                        "price": price_int,  # Store as integer, not string
                        "price_str": safe_string(kost_data.price),  # Keep original as string if needed
                        "facilities": safe_list_to_string(kost_data.facilities),
                        "rules": safe_list_to_string(kost_data.rules),
                        "contact": safe_string(kost_data.contact),
                        "url": safe_string(kost_data.url),
                        "image_url": safe_string(kost_data.image_url),
                        "gender": safe_string(kost_data.gender),
                    }
                ],
            )

            print(f"✅ Successfully added kost: {kost_data.title} (Price: {price_int})")

            # Log data ke file
            with open("kost.log", "a", encoding="utf-8") as f:
                f.write(f"{kost_data.model_dump()}\n")

if __name__ == "__main__":
    asyncio.run(main())