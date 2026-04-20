import os
from dotenv import load_dotenv
from typing import Dict
from notion_client import Client

load_dotenv('backend/.env')

notion_token = os.getenv("NOTION_API_KEY")
notion = Client(auth=notion_token)

results = notion.search(filter={"property": "object", "value": "page"}).get("results", [])
parent = results[0]
parent_id = parent["id"]
parent_type = parent["object"]

new_page = {
    "parent": {"type": f"{parent_type}_id", f"{parent_type}_id": parent_id},
    "properties": {
        "title": {"title": [{"text": {"content": "Test Note"}}]}
    },
    "children": [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": "This is a test note."}}]}
        }
    ]
}

try:
    created = notion.pages.create(**new_page)
    print("Success:", created.get("url"))
except Exception as e:
    print("Error:", e)
