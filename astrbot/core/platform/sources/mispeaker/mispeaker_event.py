import random
import asyncio
from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, MessageChain
from astrbot.api.platform import AstrBotMessage, PlatformMetadata
from astrbot.api.message_components import Plain, Image
from .client import SimpleMiSpeakerClient

class MiSpeakerPlatformEvent(AstrMessageEvent):
    def __init__(
            self, 
            message_str: str, 
            message_obj: AstrBotMessage, 
            platform_meta: PlatformMetadata, 
            session_id: str,
            client: SimpleMiSpeakerClient
        ):
        super().__init__(message_str, message_obj, platform_meta, session_id)
        self.client = client
        
    @staticmethod
    async def send_with_client(message: MessageChain, user_name: str):
        pass
        
    async def send(self, message: MessageChain):
        for comp in message.chain:
            if isinstance(comp, Plain):
                await self.client.send(comp.text)
        
        await super().send(message)