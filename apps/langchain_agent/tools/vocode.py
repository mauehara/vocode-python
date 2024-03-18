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
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.telephony.constants import (
    DEFAULT_AUDIO_ENCODING,
    DEFAULT_SAMPLING_RATE,
    DEFAULT_CHUNK_SIZE,
)
from vocode.streaming.models.transcriber import (
    AzureTranscriberConfig,
    PunctuationEndpointingConfig,
    DeepgramTranscriberConfig,
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
       O assistente está ligando para um dermatologista com os objetivos:
        - Certificar-se de que o consultório aceita o plano de saúde da Bradesco: TNP4.
        - Perguntar pela próxima data e hora disponíveis para uma consulta.
        O assistente está sendo cordial, informal e sucinto.
        O assistente espera a consultório médico atender e responder a ligação antes de começar a falar.
        O assistente não cria ou cita nomes de médicos ou o seu próprio.
        O assistente não está agendando uma consulta, apenas perguntando sobre a disponibilidade.
        O assistente usa frases curtas com até 15 palavras e pede uma informação por vez.
    """

    # synthesizer_config = AzureSynthesizerConfig(
    #     sampling_rate=DEFAULT_SAMPLING_RATE,
    #     audio_encoding=DEFAULT_AUDIO_ENCODING,
    #     voice_name="pt-BR-FranciscaNeural",
    #     language_code="pt-BR",
    # )
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

    # transcriber_config = AzureTranscriberConfig(
    #     sampling_rate=DEFAULT_SAMPLING_RATE,
    #     audio_encoding=DEFAULT_AUDIO_ENCODING,
    #     chunk_size=DEFAULT_CHUNK_SIZE,
    #     endpointing_config=PunctuationEndpointingConfig(),
    #     language="pt-BR",
    # )
    transcriber_config = DeepgramTranscriberConfig.from_telephone_input_device(
        language="pt-BR",
        model="nova-2",
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
            initial_message=BaseMessage(text="Alô, boa tarde!"),
            temperature=0.5,
            # allow_agent_to_be_cut_off=False,
            model_name="gpt-4-0125-preview",
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
