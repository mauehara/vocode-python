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
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.models.synthesizer import GoogleSynthesizerConfig
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
        # voice_name="pt-BR-FranciscaNeural",
        voice_name="pt-BR-AntonioNeural",
        language_code="pt-BR",
    )
    elevenlabs_synthesizer_config = ElevenLabsSynthesizerConfig(
        sampling_rate=DEFAULT_SAMPLING_RATE,
        audio_encoding=DEFAULT_AUDIO_ENCODING,
        api_key="b19ec31664be9f7e15f2a83e2c4d7c8f",
        voice_id="CZD4BJ803C6T0alQxsR7",
    )
    google_synthesizer_config = ElevenLabsSynthesizerConfig(
        sampling_rate=DEFAULT_SAMPLING_RATE,
        audio_encoding=DEFAULT_AUDIO_ENCODING,
        api_key="AIzaSyDaMFTgcp8MLaQ_tjnDhfLD9hpGf-zwABY",
        language_code="pt-BR",
        voice_name="pt-BR-Neural2-B",
        pitch=0,
        speaking_rate=1.2,
    )
    transcriber_config = AzureTranscriberConfig(
        sampling_rate=DEFAULT_SAMPLING_RATE,
        audio_encoding=DEFAULT_AUDIO_ENCODING,
        chunk_size=DEFAULT_CHUNK_SIZE,
        endpointing_config=PunctuationEndpointingConfig(),
        language="pt-BR",
    )
    agent_config = ChatGPTAgentConfig(
        initial_message=BaseMessage(text="Boa tarde! Vocês aceitam plano da Sul América?"),
        prompt_preamble="Você é um assistente pessoal que faz agendamentos de consultas médicas. \
            Seu trabalho é ajudar seu cliente a encontrar uma clínica médica \
            e que aceite o plano de saúde: Executivo 100 da Sul América. \
            você falará agora com uma clínica por telefone. \
            Seu objetivo é confirmar se a clínica aceita o plano de saúde do cliente e perguntar qual o próximo horário disponível para consulta. \
            Não marque nenhuma consulta, apenas pergunte sobre a disponibilidade. \
            Diga que você precisa confirmar com o seu cliente primeiro e que retornará a ligação. \
            Seja cordial e educada. Dirija-se a pessoa que te atender pelo nome. \
            Se limite a cumprir o objetivo e não faça perguntas adicionais e nem responda a perguntas fora desse contexto.",
        generate_responses=True,
        model_name="gpt-4",
    )

    outbound_call = OutboundCall(
        base_url=BASE_URL,
        to_phone="+5511996309356",
        # to_phone="+5511973567307",
        from_phone=os.environ["OUTBOUND_CALLER_NUMBER"],
        config_manager=config_manager,
        agent_config=agent_config,
        synthesizer_config=synthesizer_config,
        transcriber_config=transcriber_config,
        twilio_config=twilio_config,
        mobile_only=False,
    )

    input("Press enter to start call...")
    await outbound_call.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
