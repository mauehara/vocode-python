from typing import List
from langchain.agents import tool

CONTACTS = [
    # {"name": "Clínica Girassol", "phone": "+5511973567307"},
    {"name": "Dra. Monica Adoni Heller", "phone": "+551120991545"},
    ]


@tool("get_all_contacts")
def get_all_contacts(placeholder: str) -> List[dict]:
    """Get contacts."""
    return CONTACTS
