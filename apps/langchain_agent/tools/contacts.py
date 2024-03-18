from typing import List
from langchain.agents import tool

CONTACTS = [
    # {"name": "Clínica Girassol", "phone": "+5511973567307"},
    {"name": "Dermatologista", "phone": "+551130788848"},
    ]


@tool("get_all_contacts")
def get_all_contacts(placeholder: str) -> List[dict]:
    """Get contacts."""
    return CONTACTS
