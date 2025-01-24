import os
import json
import asyncio
import aiohttp
import time
import traceback
from .miservice import MiAccount, MiNAService, MiIOService, miio_command, miio_command_help
from astrbot.core import logger
from astrbot.api.platform import AstrBotMessage, MessageMember, MessageType
from astrbot.api.message_components import Plain, Image, At

class SimpleMiSpeakerClient():
    '''
    @author: Soulter
    @references: https://github.com/yihong0618/xiaogpt/blob/main/xiaogpt/xiaogpt.py
    '''
    def __init__(self, config: dict):
        self.username = config['username']
        self.password = config['password']
        self.did = config['did']
        self.store = os.path.join("data", '.mi.token')
        self.interval = float(config.get('interval', 1))
        
        self.conv_query_cookies = {
            'userId': '',
            'deviceId': '',
            'serviceToken': ''
        }
        
        self.MI_CONVERSATION_URL = "https://userprofile.mina.mi.com/device_profile/v2/conversation?source=dialogu&hardware={hardware}&timestamp={timestamp}&limit=1"
        
        self.session = aiohttp.ClientSession()
    
        self.activate_word = config.get('activate_word', '测试')
        self.deactivate_word = config.get('deactivate_word', '停止')
        
        self.entered = False
        
    async def initialize(self):
        account = MiAccount(self.session, self.username, self.password, self.store)
        self.miio_service = MiIOService(account) # 小米设备服务
        self.mina_service = MiNAService(account) # 小爱音箱服务
        
        device = await self.get_mina_device()
        
        self.deviceID = device['deviceID']
        self.hardware = device['hardware']
        
        with open(self.store, 'r') as f:
            data = json.load(f)
            self.userId = data['userId']
            self.serviceToken = data['micoapi'][1]
        self.conv_query_cookies['userId'] = self.userId
        self.conv_query_cookies['deviceId'] = self.deviceID
        self.conv_query_cookies['serviceToken'] = self.serviceToken
        
        logger.info(f"MiSpeakerClient initialized. Conv cookies: {self.conv_query_cookies}. Hardware: {self.hardware}")

    async def get_mina_device(self) -> dict:
        devices = await self.mina_service.device_list()
        for device in devices:
            if device['miotDID'] == self.did:
                logger.info(f"找到设备 {device['alias']}({device['name']}) 了！")
                return device
            
    async def get_conv(self) -> str:
        # 时区请确保为北京时间
        async with aiohttp.ClientSession() as session:
            session.cookie_jar.update_cookies(self.conv_query_cookies)
            query_ts = int(time.time())*1000
            logger.debug(f"Querying conversation at {query_ts}")
            async with session.get(self.MI_CONVERSATION_URL.format(hardware=self.hardware, timestamp=str(query_ts))) as resp:
                json_blob = await resp.json()
                if json_blob['code'] == 0:
                    data = json.loads(json_blob['data'])
                    records = data.get('records', None)
                    for record in records:
                        if record['time'] >= query_ts - self.interval*1000:
                            return record['query']
                else:
                    logger.error(f"Failed to get conversation: {json_blob}")
        
        return None
                        
    async def start_pooling(self):
        while True:
            await asyncio.sleep(self.interval)
            try:
                query = await self.get_conv()
                if not query:
                    continue
                
                # is wake
                if query == self.activate_word:
                    self.entered = True
                    await self.stop_playing()
                    await self.send("我来啦！")
                    continue
                elif query == self.deactivate_word:
                    self.entered = False
                    await self.stop_playing()
                    await self.send("再见，欢迎给个 Star。")
                    continue
                if not self.entered:
                    continue
                
                await self.send("")
                abm = await self._convert(query)
                
                if abm:
                    coro = getattr(self, "on_event_received")
                    if coro:
                        await coro(abm)
                
            except BaseException as e:
                traceback.print_exc()
                logger.error(e)
                
    async def _convert(self, query: str):
        abm = AstrBotMessage()
        abm.message = [Plain(query)]
        abm.message_id = str(int(time.time()))
        abm.message_str = query
        abm.raw_message = query
        abm.session_id = f"{self.hardware}_{self.did}_{self.username}"
        abm.sender = MessageMember(self.username, "主人")
        abm.self_id = f"{self.hardware}_{self.did}"
        abm.type = MessageType.FRIEND_MESSAGE
        return abm
    
    async def send(self, message: str):
        text = f'5 {message}'
        await miio_command(self.miio_service, self.did, text, 'astrbot')
        
    async def stop_playing(self):
        text = f'3-2'
        await miio_command(self.miio_service, self.did, text, 'astrbot')
