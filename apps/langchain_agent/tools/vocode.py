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
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.telephony.constants import (
    DEFAULT_AUDIO_ENCODING,
    DEFAULT_SAMPLING_RATE,
    DEFAULT_CHUNK_SIZE,
)
from vocode.streaming.models.transcriber import (
    AzureTranscriberConfig,
    PunctuationEndpointingConfig,
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

    synthesizer_config = AzureSynthesizerConfig(
        sampling_rate=DEFAULT_SAMPLING_RATE,
        audio_encoding=DEFAULT_AUDIO_ENCODING,
        voice_name="pt-BR-FranciscaNeural",
        language_code="pt-BR",
    )
    transcriber_config = AzureTranscriberConfig(
        sampling_rate=DEFAULT_SAMPLING_RATE,
        audio_encoding=DEFAULT_AUDIO_ENCODING,
        chunk_size=DEFAULT_CHUNK_SIZE,
        endpointing_config=PunctuationEndpointingConfig(),
        language="pt-BR",
    )

    call = OutboundCall(
        base_url=os.environ["TELEPHONY_SERVER_BASE_URL"],
        to_phone=phone_number,
        from_phone=os.environ["OUTBOUND_CALLER_NUMBER"],
        config_manager=RedisConfigManager(),
        agent_config=ChatGPTAgentConfig(
            prompt_preamble=prompt,
            initial_message=BaseMessage(text=initial_message),
        ),
        logger=logging.Logger("call_phone_number"),
        synthesizer_config=synthesizer_config,
        transcriber_config=transcriber_config,
    )
    LOOP.run_until_complete(call.start())
    while True:
        maybe_transcript = get_transcript(call.conversation_id)
        if maybe_transcript:
            delete_transcript(call.conversation_id)
            return maybe_transcript
        else:
            time.sleep(1)
