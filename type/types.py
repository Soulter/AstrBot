import asyncio
from asyncio import Task
from type.register import *
from typing import List, Awaitable
from logging import Logger
from util.cmd_config import CmdConfig
from util.t2i.renderer import TextToImageRenderer
from util.updator.astrbot_updator import AstrBotUpdator
from util.image_uploader import ImageUploader
from util.updator.plugin_updator import PluginUpdator
from type.command import CommandResult
from type.astrbot_message import MessageType
from model.plugin.command import PluginCommandBridge
from model.provider.provider import Provider


class Context:
    '''
    存放一些公用的数据，用于在不同模块(如core与command)之间传递
    '''

    def __init__(self):
        self.logger: Logger = None
        self.base_config: dict = None  # 配置（期望启动机器人后是不变的）
        self.config_helper: CmdConfig = None
        self.cached_plugins: List[RegisteredPlugin] = []  # 缓存的插件
        self.platforms: List[RegisteredPlatform] = []
        self.llms: List[RegisteredLLM] = []
        self.default_personality: dict = None
        
        self.unique_session = False # 独立会话
        self.version: str = None  # 机器人版本
        self.nick: tuple = None  # gocq 的唤醒词
        self.t2i_mode = False
        self.web_search = False  # 是否开启了网页搜索
        
        self.metrics_uploader = None
        self.updator: AstrBotUpdator = None
        self.plugin_updator: PluginUpdator = None
        self.plugin_command_bridge = PluginCommandBridge(self.cached_plugins)
        self.image_renderer = TextToImageRenderer()
        self.image_uploader = ImageUploader()
        self.message_handler = None # see astrbot/message/handler.py
        self.ext_tasks: List[Task] = []
        
        self.command_manager = None

        # useless
        self.reply_prefix = ""

    def register_commands(self, 
                          plugin_name: str, 
                          command_name: str, 
                          description: str, 
                          priority: int, 
                          handler: callable,
                          use_regex: bool = False,
                          ignore_prefix: bool = False):
        '''
        注册插件指令。
        
        @param plugin_name: 插件名，注意需要和你的 metadata 中的一致。
        @param command_name: 指令名，如 "help"。不需要带前缀。
        @param description: 指令描述。
        @param priority: 优先级越高，越先被处理。合理的优先级应该在 1-10 之间。
        @param handler: 指令处理函数。函数参数：message: AstrMessageEvent, context: Context
        @param use_regex: 是否使用正则表达式匹配指令名。
        @param ignore_prefix: 是否忽略前缀。默认为 False。设置为 True 后，将不会检查用户设置的前缀。
        
        .. Example::
        
        ignore_prefix = False 时，用户输入 "/help" 时，会被识别为 "help" 指令。如果 ignore_prefix = True，则用户输入 "help" 也会被识别为 "help" 指令。
        '''
        self.plugin_command_bridge.register_command(plugin_name, 
                                                    command_name, 
                                                    description, 
                                                    priority, 
                                                    handler, 
                                                    use_regex,
                                                    ignore_prefix)
        
    def register_task(self, coro: Awaitable, task_name: str):
        '''
        注册任务。适用于需要长时间运行的插件。
        
        `coro`: 协程对象
        `task_name`: 任务名，用于标识任务。自定义即可。
        '''
        task = asyncio.create_task(coro, name=task_name)
        self.ext_tasks.append(task)
        
    def register_provider(self, llm_name: str, provider: Provider, origin: str = ''):
        '''
        注册一个提供 LLM 资源的 Provider。
        
        `provider`: Provider 对象。即你的实现需要继承 Provider 类。至少应该实现 text_chat() 方法。
        '''
        self.llms.append(RegisteredLLM(llm_name, provider, origin))
    
    def find_platform(self, platform_name: str) -> RegisteredPlatform:
        for platform in self.platforms:
            if platform_name == platform.platform_name:
                return platform
            
        raise ValueError("couldn't find the platform you specified")

    async def send_message(self, unified_msg_origin: str, message: CommandResult):
        '''
        发送消息。
        
        `unified_msg_origin`: 统一消息来源
        `message`: 消息内容
        '''
        l = unified_msg_origin.split(":")
        if len(l) != 3:
            raise ValueError("Invalid unified_msg_origin")
        platform_name, message_type, id = l
        platform = self.find_platform(platform_name)
        await platform.platform_instance.send_msg_new(MessageType(message_type), id, message)
        