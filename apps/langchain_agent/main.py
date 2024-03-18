import os
import sys
import typing
from dotenv import load_dotenv

from tools.contacts import get_all_contacts
from tools.client_information import get_client_information
from tools.vocode import call_phone_number
from tools.word_of_the_day import word_of_the_day
from langchain.memory import ConversationBufferMemory


from stdout_filterer import RedactPhoneNumbers

load_dotenv()

from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from langchain.agents import AgentType

if __name__ == "__main__":
    # Redirect stdout to our custom class
    sys.stdout = typing.cast(typing.TextIO, RedactPhoneNumbers(sys.stdout))

    OBJECTIVE = "Ligue para as clínicas em meus contatos e pergunte qual o próximo horário disponível para consulta."
    llm = ChatOpenAI(
        temperature=0, 
        model_name="gpt-4-turbo-preview")
    system_message = """
        Você é o assistente pessoal do Sr.Mauricio.
        Seu trabalho é ajudar o Sr.Mauricio a agendar uma consulta com dermatologista.
        Você falará agora com uma clínica por telefone.
        Você precisa confirmar se a clínica aceita o plano de saúde da Bradesco.
        Você também precisa confirmar qual o próximo horário disponível para consulta.
        Seja cordial e direta. Fale em português do Brasil.
        Prefira frases curtas e peça uma informação por vez.
        Não responda a nenhuma pergunta que fuja de seu contexto.
        Não agende nenhuma consulta, apenas pergunte sobre a disponibilidade.
        Não invente dados e informações.
        Espere a clínica atender e responder a ligação antes de começar a falar.
        Caso seja interrompida, o assistente espera a clínica terminar de falar e continue de onde parou.
        Durante a conversa, podem haver mal-entendidos como a clínica testando a conexão ao dizer "alô", nesses casos o assistente apenas ignora e continua de onde parou.
        Sua primeira fala deve se apresentar antes de tudo e perguntar se pode tirar uma dúvida com a pessoa que atender.
        """
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    # Logging of LLMChains
    verbose = True
    agent = initialize_agent(
        tools=[get_all_contacts, call_phone_number, get_client_information],
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=verbose,
        memory=memory,
        system_message=system_message,
        agent_kwargs={"system_message": system_message}
    )
    agent.run(OBJECTIVE)
