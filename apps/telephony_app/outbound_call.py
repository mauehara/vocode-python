import os
import vocode
from dotenv import load_dotenv

load_dotenv()

from vocode.streaming.telephony.conversation.outbound_call import OutboundCall
from vocode.streaming.telephony.config_manager.redis_config_manager import (
    RedisConfigManager,
)

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
from vocode.streaming.models.telephony import (
    TwilioConfig,
)


BASE_URL = os.environ["BASE_URL"]



async def main():
    config_manager = RedisConfigManager()

    twilio_config = TwilioConfig(
        account_sid=os.environ["TWILIO_ACCOUNT_SID"],
        auth_token=os.environ["TWILIO_AUTH_TOKEN"],
        record=True,
    )
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
    agent_config = ChatGPTAgentConfig(
        initial_message=BaseMessage(text="Oi Lia, você vai ao show de qual artista hoje?"),
        prompt_preamble="Descubra o gênero musical do cantor que a Lia irá assistir hoje.",
        generate_responses=True,
        model_name="gpt-4",
    )

    outbound_call = OutboundCall(
        base_url=BASE_URL,
        to_phone="+5511946275451",
        from_phone=os.environ["OUTBOUND_CALLER_NUMBER"],
        config_manager=config_manager,
        agent_config=agent_config,
        synthesizer_config=synthesizer_config,
        transcriber_config=transcriber_config,
        twilio_config=twilio_config,
    )

    input("Press enter to start call...")
    await outbound_call.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
