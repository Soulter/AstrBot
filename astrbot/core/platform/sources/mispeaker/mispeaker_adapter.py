import logging
import time
import asyncio
import os

from astrbot.api.platform import Platform, AstrBotMessage, MessageMember, MessageType, PlatformMetadata
from astrbot.api.event import MessageChain
from typing import Union, List
from astrbot.api.message_components import Image, Plain, At
from astrbot.core.platform.astr_message_event import MessageSesion
from ...register import register_platform_adapter
from astrbot.core.message.components import BaseMessageComponent
from .client import SimpleMiSpeakerClient
from .mispeaker_event import MiSpeakerPlatformEvent
from astrbot.core import logger


@register_platform_adapter("mispeaker", "小爱音箱")
class MiSpeakerPlatformAdapter(Platform):

    def __init__(self, platform_config: dict, platform_settings: dict, event_queue: asyncio.Queue) -> None:
        super().__init__(event_queue)
                
        self.config = platform_config

        
    async def send_by_session(self, session: MessageSesion, message_chain: MessageChain):
        pass
        
    def meta(self) -> PlatformMetadata:
        return PlatformMetadata(
            "mispeaker",
            "小爱音箱",
        )
        
    async def handle_msg(self, message: AstrBotMessage):
        message_event = MiSpeakerPlatformEvent(
            message_str=message.message_str,
            message_obj=message,
            platform_meta=self.meta(),
            session_id=message.session_id,
            client=self.client
        )
        
        self.commit_event(message_event)

    def run(self):
        self.client = SimpleMiSpeakerClient(
            self.config
        )
        
        async def on_event_received(abm: AstrBotMessage):
            logger.info(f"on_event_received: {abm}")
            
            await self.handle_msg(abm)
            
        self.client.on_event_received = on_event_received
        
        return self._run()
    
    async def _run(self):
        await self.client.initialize()
        await self.client.start_pooling()