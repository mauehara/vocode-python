import logging
import asyncio
import os
from langchain.agents import tool
from dotenv import load_dotenv

from vocode.streaming.models.message import BaseMessage
from call_transcript_utils import delete_transcript, get_transcript

load_dotenv()

from vocode.streaming.telephony.conversation.outbound_call import OutboundCall
from vocode.streaming.telephony.config_manager.redis_config_manager import (
    RedisConfigManager,
)
from vocode.streaming.models.agent import ChatGPTAgentConfig
import time
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.synthesizer import AzureSynthesizerConfig
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.telephony.constants import (
    DEFAULT_AUDIO_ENCODING,
    DEFAULT_SAMPLING_RATE,
    DEFAULT_CHUNK_SIZE,
)
from vocode.streaming.models.transcriber import (
    AzureTranscriberConfig,
    PunctuationEndpointingConfig,
)
from vocode.streaming.models.telephony import (
    TwilioConfig,
)

LOOP = asyncio.new_event_loop()
asyncio.set_event_loop(LOOP)

@tool("call phone number")
def call_phone_number(input: str) -> str:
    """calls a phone number as a bot and returns a transcript of the conversation.
    the input to this tool is a pipe separated list of a phone number, a prompt, and the first thing the bot should say.
    The prompt should instruct the bot with what to do on the call and be in the 3rd person,
    like 'the assistant is performing this task' instead of 'perform this task'.

    should only use this tool once it has found an adequate phone number to call.

    for example, `+15555555555|the assistant is explaining the meaning of life|i'm going to tell you the meaning of life` will call +15555555555, say 'i'm going to tell you the meaning of life', and instruct the assistant to tell the human what the meaning of life is.
    """
    phone_number, prompt, initial_message = input.split("|", 2)

    prompt_preamble = """
        O assistente é o assistente pessoal de um cliente chamado Mauricio.
        O objetivo do assistente é ajudar o Mauricio a agendar consultas médicas.
        O assistente precisa confirmar se a consultório médico aceita o plano de saúde da Bradesco.
        O assistente também precisa confirmar qual o próximo horário disponível para consulta.
        O assistente é cordial e direto. 
        O assistente fala em português do Brasil.
        O assistente usa frases curtas e pede uma informação por vez.
        O assistente não responde a nenhuma pergunta que fuja de seu contexto.
        O assistente não agenda nenhuma consulta, apenas pergunta sobre a disponibilidade.
        O assistente não inventa dados e informações.
        O assistente interaje apenas com os consultório médicos.
        O assistente não se coloca à disposição ao final da ligação. Apenas deseja um ótimo dia e desliga.
        O assistente espera a consultório médico atender e responder a ligação antes de começar a falar.
        O assistente se refere à pessoa que atende pelo nome.
        O assistente não precisa dizer o seu próprio nome ao se apresentar.
        Caso o assistente precise de mais informações, ele diz que irá retornar a ligação.
        Após a fala inicial da pessoa que atender a ligação, o assistente pergunta sobre o plano de saúde.
        """ + prompt

    synthesizer_config = AzureSynthesizerConfig(
        sampling_rate=DEFAULT_SAMPLING_RATE,
        audio_encoding=DEFAULT_AUDIO_ENCODING,
        voice_name="pt-BR-FranciscaNeural",
        language_code="pt-BR",
    )
    elevenlabs_synthesizer_config = ElevenLabsSynthesizerConfig(
        api_key=os.environ["ELEVENLABS_API_KEY"],
        voice_id=os.environ["ELEVENLABS_VOICE_ID"],
        sampling_rate=DEFAULT_SAMPLING_RATE,
        audio_encoding=DEFAULT_AUDIO_ENCODING,
        # stability=0.74,
        # similarity_boost=0.40,
        model_id="eleven_multilingual_v2",
        optimize_streaming_latency=3,
    )

    transcriber_config = AzureTranscriberConfig(
        sampling_rate=DEFAULT_SAMPLING_RATE,
        audio_encoding=DEFAULT_AUDIO_ENCODING,
        chunk_size=DEFAULT_CHUNK_SIZE,
        endpointing_config=PunctuationEndpointingConfig(),
        language="pt-BR",
    )
    twilio_config = TwilioConfig(
        account_sid=os.environ["TWILIO_ACCOUNT_SID"],
        auth_token=os.environ["TWILIO_AUTH_TOKEN"],
        record=True,
    )

    call = OutboundCall(
        base_url=os.environ["TELEPHONY_SERVER_BASE_URL"],
        to_phone=phone_number,
        from_phone=os.environ["OUTBOUND_CALLER_NUMBER"],
        config_manager=RedisConfigManager(),
        agent_config=ChatGPTAgentConfig(
            prompt_preamble=prompt_preamble,
            # initial_message=BaseMessage(text=initial_message),
            temperature=0.1,
            allow_agent_to_be_cut_off=False,
        ),
        logger=logging.Logger("call_phone_number"),
        synthesizer_config=elevenlabs_synthesizer_config,
        transcriber_config=transcriber_config,
        twilio_config=twilio_config,
        mobile_only=False,
    )
    LOOP.run_until_complete(call.start())
    while True:
        maybe_transcript = get_transcript(call.conversation_id)
        if maybe_transcript:
            delete_transcript(call.conversation_id)
            return maybe_transcript
        else:
            time.sleep(1)
