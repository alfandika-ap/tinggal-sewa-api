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
    "description": "Search for properties (kosan, apartemen, rumah, dll) based on the given criteria, criteria can be city, province, price, facilities, etc related to the property.",
    "parameters": {
        "type": "object",
        "properties": {
            "criteria": {
                "type": "string",
                "description": "criteria can be city, province, price range, facilities, etc related to the property"
            }
        },
        "required": ["criteria"]
    }
}