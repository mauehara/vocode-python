from typing import List
from langchain.agents import tool

CONTACTS = [{"name": "Mauricio", 
             "phone": "+5511973567307",
             "full_address": "Rua das Flores, 123, São Paulo, SP",
             "email": "mauricio@gmail.com",}]


@tool("get_client_information")
def get_client_information(placeholder: str) -> List[dict]:
    """Get client information."""
    return CONTACTS
