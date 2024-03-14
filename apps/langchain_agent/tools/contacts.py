from typing import List
from langchain.agents import tool

CONTACTS = [
    # {"name": "Clínica Girassol", "phone": "+5511973567307"},
    {"name": "Clínica Holosi Estética e Saúde", "phone": "+551141132266"},
    {"name": "espaço ( mira )", "phone": "+5511997997287"},
    {"name": "Dra Thais Ragazzo", "phone": "+5511978383990"},
    ]


@tool("get_all_contacts")
def get_all_contacts(placeholder: str) -> List[dict]:
    """Get contacts."""
    return CONTACTS
