function_get_weather_schema = {
    "name": "get_weather",
    "description": "Get the weather for a given city",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Name of the city"
            }
        },
        "required": ["city"]
    }
}

function_search_properties_schema = {
    "name": "search_properties",
    "description": "Search for properties like kos-kosan, apartments, or houses based on structured criteria.",
    "parameters": {
        "type": "object",
        "properties": {
            "query_texts": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Array of natural language descriptions of the search."
            },
            "where": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "province": {"type": "string"},
                    "price_min": {"type": "number"},
                    "price_max": {"type": "number"},
                    "gender": {"type": "string", "enum": ["pria", "wanita", "campuran"]},
                    "facilities": {
                        "type": "object",
                        "properties": {
                            "wifi": {"type": "boolean"},
                            "ac": {"type": "boolean"},
                            "kitchen": {"type": "boolean"},
                            "parking": {"type": "boolean"},
                            # tambahkan fasilitas lain sesuai kebutuhan
                        }
                    }
                }
            }
        },
        "required": ["query_texts", "where"]
    }
}


function_search_properties_schema = {
    "name": "search_properties",
    "description": "WAJIB digunakan untuk mencari properti ketika user memberikan lokasi dan budget. Search for kos, apartments, or houses.",
    "parameters": {
        "type": "object",
        "properties": {
            "query_texts": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Natural language description of search request"
            },
            "where": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "province": {"type": "string"},
                    "price_min": {"type": "number"},
                    "price_max": {"type": "number"},
                    "gender": {"type": "string", "enum": ["pria", "wanita", "campuran"]},
                    "facilities": {
                        "type": "object",
                        "additionalProperties": {"type": "boolean"}
                    }
                },
                "required": ["city", "province"]
            }
        },
        "required": ["query_texts", "where"]
    }
}