from typing import List
from langchain.agents import tool

CONTACTS = [{"name": "Mike's Pizza", "phone": "+5511973567307"}]


@tool("get_all_contacts")
def get_all_contacts(placeholder: str) -> List[dict]:
    """Get contacts."""
    return CONTACTS
