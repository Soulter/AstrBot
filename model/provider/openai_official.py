import os
import asyncio
import json
import time
import tiktoken
import threading
import traceback
import base64

from openai import AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion
from openai._exceptions import *
from util.io import download_image_by_url

from astrbot.db import BaseDatabase
from model.provider.provider import Provider
from util.cmd_config import LLMConfig
from util.log import LogManager
from logging import Logger
from typing import List, Dict

from dataclasses import asdict

logger: Logger = LogManager.GetLogger(log_name='astrbot')

MODELS = {
    "gpt-4o": 128000,
    "gpt-4o-2024-05-13": 128000,
    "gpt-4-turbo": 128000,
    "gpt-4-turbo-2024-04-09": 128000,
    "gpt-4-turbo-preview": 128000,
    "gpt-4-0125-preview": 128000,
    "gpt-4-1106-preview": 128000,
    "gpt-4-vision-preview": 128000,
    "gpt-4-1106-vision-preview": 128000,
    "gpt-4": 8192,
    "gpt-4-0613": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-32k-0613": 32768,
    "gpt-3.5-turbo-0125": 16385,
    "gpt-3.5-turbo": 16385,
    "gpt-3.5-turbo-1106": 16385,
    "gpt-3.5-turbo-instruct": 4096,
    "gpt-3.5-turbo-16k": 16385,
    "gpt-3.5-turbo-0613": 16385,
    "gpt-3.5-turbo-16k-0613": 16385, 
}

class ProviderOpenAIOfficial(Provider):
    def __init__(self, llm_config: LLMConfig, db_helper: BaseDatabase) -> None:
        super().__init__()

        self.api_keys = []
        self.chosen_api_key = None
        self.base_url = None
        self.llm_config = llm_config
        self.keys_data = {} # 记录超额
        if llm_config.key: self.api_keys = llm_config.key
        if llm_config.api_base: self.base_url = llm_config.api_base
        if not self.api_keys:
            logger.warn("看起来你没有添加 OpenAI 的 API 密钥，OpenAI LLM 能力将不会启用。")
        else:
            self.chosen_api_key = self.api_keys[0]

        for key in self.api_keys:
            self.keys_data[key] = True

        self.client = AsyncOpenAI(
            api_key=self.chosen_api_key,
            base_url=self.base_url
        )
        super().set_curr_model(llm_config.model_config.model)
        if llm_config.image_generation_model_config:
            self.image_generator_model_configs: Dict = asdict(llm_config.image_generation_model_config)
        self.session_memory: Dict[str, List]  = {} # 会话记忆
        self.session_memory_lock = threading.Lock()
        self.max_tokens = self.llm_config.model_config.max_tokens # 上下文窗口大小
        
        logger.info("正在载入分词器 cl100k_base...")
        self.tokenizer = tiktoken.get_encoding("cl100k_base") # todo: 根据 model 切换分词器
        logger.info("分词器载入完成。")
        
        self.DEFAULT_PERSONALITY = {
            "prompt": self.llm_config.default_personality,
            "name": "default"
        }
        self.curr_personality = self.DEFAULT_PERSONALITY
        self.session_personality = {} # 记录了某个session是否已设置人格。
        # 读取历史记录
        self.db_helper = db_helper
        try:
            for history in db_helper.get_llm_history():
                self.session_memory_lock.acquire()
                self.session_memory[history.session_id] = json.loads(history.content)
                self.session_memory_lock.release()
        except BaseException as e:
            logger.warning(f"读取 OpenAI LLM 对话历史记录 失败：{e}。仍可正常使用。")
        
        # 定时保存历史记录
        threading.Thread(target=self.dump_history, daemon=True).start()

    def dump_history(self):
        '''转储历史记录'''
        time.sleep(30)
        while True:
            try:
                for session_id, content in self.session_memory.items():
                    self.db_helper.update_llm_history(session_id, json.dumps(content))
            except BaseException as e:
                logger.error("保存 LLM 历史记录失败: " + str(e))
            finally:
                time.sleep(10*60)
    
    def personality_set(self, default_personality: dict, session_id: str):
        if not default_personality: return
        if session_id not in self.session_memory:
            self.session_memory[session_id] = []
        self.curr_personality = default_personality
        self.session_personality = {} # 重置
        encoded_prompt = self.tokenizer.encode(default_personality['prompt'])
        tokens_num = len(encoded_prompt)
        model = self.get_curr_model()
        if model in MODELS and tokens_num > MODELS[model] - 500:
            default_personality['prompt'] = self.tokenizer.decode(encoded_prompt[:MODELS[model] - 500])

        new_record = {
            "user": {
                "role": "system",
                "content": default_personality['prompt'],
            },
            'usage_tokens': 0, # 到该条目的总 token 数
            'single-tokens': 0 # 该条目的 token 数
        }

        self.session_memory[session_id].append(new_record)

    async def encode_image_bs64(self, image_url: str) -> str:
        '''
        将图片转换为 base64
        '''
        if image_url.startswith("http"):
            image_url = await download_image_by_url(image_url)
        
        with open(image_url, "rb") as f:
            image_bs64 = base64.b64encode(f.read()).decode()
            return "data:image/jpeg;base64," + image_bs64

    async def retrieve_context(self, session_id: str):
        '''
        根据 session_id 获取保存的 OpenAI 格式的上下文
        '''
        if session_id not in self.session_memory:
            raise Exception("会话 ID 不存在")
        
        # 转换为 openai 要求的格式
        context = []
        is_lvm = await self.is_lvm()
        for record in self.session_memory[session_id]:
            if "user" in record and record['user']:
                if not is_lvm and "content" in record['user'] and isinstance(record['user']['content'], list):
                    logger.warn(f"由于当前模型 {self.get_curr_model()} 不支持视觉，将忽略上下文中的图片输入。如果一直弹出此警告，可以尝试 reset 指令。")
                    continue
                context.append(record['user'])
            if "AI" in record and record['AI']:
                context.append(record['AI'])

        return context

    async def is_lvm(self):
        '''
        是否是 LVM
        '''
        return self.get_curr_model().startswith("gpt-4")
    
    async def get_models(self):
        try:
            models = await self.client.models.list()
        except NotFoundError as e:
            bu = str(self.client.base_url)
            self.client.base_url = bu + "/v1"
            models = await self.client.models.list()
        finally:
            return filter(lambda x: x.id.startswith("gpt"), models.data)
    
    async def assemble_context(self, session_id: str, prompt: str, image_url: str = None):
        '''
        组装上下文，并且根据当前上下文窗口大小截断
        '''
        if session_id not in self.session_memory:
            raise Exception("会话 ID 不存在")
        
        tokens_num = len(self.tokenizer.encode(prompt))
        previous_total_tokens_num = 0 if not self.session_memory[session_id] else self.session_memory[session_id][-1]['usage_tokens']

        message = {
            "usage_tokens": previous_total_tokens_num + tokens_num,
            "single_tokens": tokens_num,
            "AI": None
        }
        if image_url:
            user_content = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": await self.encode_image_bs64(image_url)
                        }
                    }
                ]
            }
        else:
            user_content = {
                "role": "user",
                "content": prompt
            }

        message["user"] = user_content
        self.session_memory[session_id].append(message)

        # 根据 模型的上下文窗口 淘汰掉多余的记录
        curr_model = self.get_curr_model()
        if curr_model in MODELS:
            maxium_tokens_num = MODELS[curr_model] - 300 # 至少预留 300 给 completion
            # if message['usage_tokens'] > maxium_tokens_num:
                # 淘汰多余的记录，使得最终的 usage_tokens 不超过 maxium_tokens_num - 300
                # contexts = self.session_memory[session_id]
                # need_to_remove_idx = 0
                # freed_tokens_num = contexts[0]['single-tokens']
                # while freed_tokens_num < message['usage_tokens'] - maxium_tokens_num:
                #     need_to_remove_idx += 1
                #     freed_tokens_num += contexts[need_to_remove_idx]['single-tokens']
                # # 更新之后的所有记录的 usage_tokens
                # for i in range(len(contexts)):
                #     if i > need_to_remove_idx:
                #         contexts[i]['usage_tokens'] -= freed_tokens_num
                # logger.debug(f"淘汰上下文记录 {need_to_remove_idx+1} 条，释放 {freed_tokens_num} 个 token。当前上下文总 token 为 {contexts[-1]['usage_tokens']}。")
                # self.session_memory[session_id] = contexts[need_to_remove_idx+1:]
            while len(self.session_memory[session_id]) and self.session_memory[session_id][-1]['usage_tokens'] > maxium_tokens_num:
                self.pop_record(session_id)


    async def pop_record(self, session_id: str, pop_system_prompt: bool = False):
        '''
        弹出第一条记录
        '''
        if session_id not in self.session_memory:
            raise Exception("会话 ID 不存在")
        
        if len(self.session_memory[session_id]) == 0:
            return None
        
        for i in range(len(self.session_memory[session_id])):
            # 检查是否是 system prompt
            if not pop_system_prompt and self.session_memory[session_id][i]['user']['role'] == "system":
                # 如果只有一个 system prompt，才不删掉
                f = False
                for j in range(i+1, len(self.session_memory[session_id])):
                    if self.session_memory[session_id][j]['user']['role'] == "system":
                        f = True
                        break
                if not f:
                    continue
            record = self.session_memory[session_id].pop(i)
            break

        # 更新之后所有记录的 usage_tokens
        for i in range(len(self.session_memory[session_id])):
            self.session_memory[session_id][i]['usage_tokens'] -= record['single-tokens']
        logger.debug(f"淘汰上下文记录 1 条，释放 {record['single-tokens']} 个 token。当前上下文总 token 为 {self.session_memory[session_id][-1]['usage_tokens']}。")
        return record

    async def text_chat(self, 
                        prompt: str, 
                        session_id: str, 
                        image_url: None=None, 
                        tools: None=None, 
                        extra_conf: Dict = None,
                        **kwargs
                    ) -> str:
        if os.environ.get("TEST_LLM", "off") != "on" and os.environ.get("TEST_MODE", "off") == "on":
            return "这是一个测试消息。"
        
        super().accu_model_stat()
        if not session_id:
            session_id = "unknown"
            if "unknown" in self.session_memory:
                del self.session_memory["unknown"]

        if session_id not in self.session_memory:
            self.session_memory[session_id] = []

        if session_id not in self.session_personality or not self.session_personality[session_id]:
            self.personality_set(self.curr_personality, session_id)
            self.session_personality[session_id] = True
        
        # 如果 prompt 超过了最大窗口，截断。
        # 1. 可以保证之后 pop 的时候不会出现问题
        # 2. 可以保证不会超过最大 token 数
        _encoded_prompt = self.tokenizer.encode(prompt)
        curr_model = self.get_curr_model()
        if curr_model in MODELS and len(_encoded_prompt) > MODELS[curr_model] - 300:
            _encoded_prompt = _encoded_prompt[:MODELS[curr_model] - 300]
            prompt = self.tokenizer.decode(_encoded_prompt)
        
        # 组装上下文，并且根据当前上下文窗口大小截断
        await self.assemble_context(session_id, prompt, image_url)

        # 获取上下文，openai 格式
        contexts = await self.retrieve_context(session_id)

        conf = asdict(self.llm_config.model_config)
        if extra_conf: conf.update(extra_conf)

        # start request
        retry = 0
        rate_limit_retry = 0
        while retry < 3 or rate_limit_retry < 5:
            logger.debug(conf)
            logger.debug(contexts)
            if tools:
                completion_coro = self.client.chat.completions.create(
                    messages=contexts,
                    stream=False,
                    tools=tools,
                    **conf
                )
            else:
                completion_coro = self.client.chat.completions.create(
                    messages=contexts,
                    stream=False,
                    **conf
                )
            try:
                completion = await completion_coro
                break
            except AuthenticationError as e:
                api_key = self.chosen_api_key[10:] + "..."
                logger.error(f"OpenAI API Key {api_key} 验证错误。详细原因：{e}。正在切换到下一个可用的 Key（如果有的话）")
                self.keys_data[self.chosen_api_key] = False
                ok = await self.switch_to_next_key()
                if ok: continue
                else: raise Exception("所有 OpenAI API Key 目前都不可用。")
            except BadRequestError as e:
                retry += 1
                logger.warn(f"OpenAI 请求异常：{e}。")
                if "image_url is only supported by certain models." in str(e):
                    raise Exception(f"当前模型 { self.get_curr_model() } 不支持图片输入，请更换模型。")
            except RateLimitError as e:
                if "You exceeded your current quota" in str(e):
                    self.keys_data[self.chosen_api_key] = False
                    ok = await self.switch_to_next_key()
                    if ok: continue
                    else: raise Exception("所有 OpenAI API Key 目前都不可用。")
                logger.error(f"OpenAI API Key {self.chosen_api_key} 达到请求速率限制或者官方服务器当前超载。详细原因：{e}")
                await self.switch_to_next_key()
                rate_limit_retry += 1
                await asyncio.sleep(1)
            except NotFoundError as e:
                raise e
            except Exception as e:
                retry += 1
                if retry >= 3:
                    logger.error(traceback.format_exc())
                    raise Exception(f"OpenAI 请求失败：{e}。重试次数已达到上限。")
                if "maximum context length" in str(e):
                    logger.warn(f"OpenAI 请求失败：{e}。上下文长度超过限制。尝试弹出最早的记录然后重试。")
                    self.pop_record(session_id)
                
                logger.warning(traceback.format_exc())
                logger.warning(f"OpenAI 请求失败：{e}。重试第 {retry} 次。")
                await asyncio.sleep(1)

        assert isinstance(completion, ChatCompletion)
        logger.debug(f"openai completion: {completion.usage}")
        
        if len(completion.choices) == 0:
            raise Exception("OpenAI API 返回的 completion 为空。")
        choice = completion.choices[0]

        usage_tokens = completion.usage.total_tokens
        completion_tokens = completion.usage.completion_tokens
        self.session_memory[session_id][-1]['usage_tokens'] = usage_tokens
        self.session_memory[session_id][-1]['single_tokens'] += completion_tokens

        if choice.message.content:
            # 返回文本
            completion_text = str(choice.message.content).strip()
        elif choice.message.tool_calls and choice.message.tool_calls:
            # tools call (function calling)
            return choice.message.tool_calls[0].function
        
        self.session_memory[session_id][-1]['AI'] = {
            "role": "assistant",
            "content": completion_text
        }

        return completion_text
    
    async def switch_to_next_key(self):
        '''
        切换到下一个 API Key
        '''
        if not self.api_keys:
            logger.error("OpenAI API Key 不存在。")
            return False

        for key in self.keys_data:
            if self.keys_data[key]:
                # 没超额
                self.chosen_api_key = key
                self.client.api_key = key
                logger.info(f"OpenAI 切换到 API Key {key[:10]}... 成功。")
                return True

        return False
    
    async def image_generate(self, prompt: str, session_id: str = None, **kwargs) -> str:
        '''
        生成图片
        '''
        retry = 0
        conf = self.image_generator_model_configs
        if not conf:
            logger.error("OpenAI 图片生成模型配置不存在。")
            raise Exception("OpenAI 图片生成模型配置不存在。")
        super().accu_model_stat(model=conf['model'])
        while retry < 3:
            try:
                images_response = await self.client.images.generate(
                    prompt=prompt,
                    **conf
                )
                image_url = images_response.data[0].url
                return image_url
            except Exception as e:
                retry += 1
                if retry >= 3:
                    logger.error(traceback.format_exc())
                    raise Exception(f"OpenAI 图片生成请求失败：{e}。重试次数已达到上限。")
                logger.warning(f"OpenAI 图片生成请求失败：{e}。重试第 {retry} 次。")
                await asyncio.sleep(1)

    async def forget(self, session_id=None, keep_system_prompt: bool=False) -> bool:
        if session_id is None: return False
        self.session_memory[session_id] = []
        if keep_system_prompt:
            self.personality_set(self.curr_personality, session_id)
        else:
            self.curr_personality = self.DEFAULT_PERSONALITY
        return True
    
    def dump_contexts_page(self, session_id: str, size=5, page=1,):
        '''
        获取缓存的会话
        '''
        # contexts_str = ""
        # for i, key in enumerate(self.session_memory):
        #     if i < (page-1)*size or i >= page*size:
        #         continue
        #     contexts_str += f"Session ID: {key}\n"
        #     for record in self.session_memory[key]:
        #         if "user" in record:
        #             contexts_str += f"User: {record['user']['content']}\n"
        #         if "AI" in record:
        #             contexts_str += f"AI: {record['AI']['content']}\n"
        #     contexts_str += "---\n"
        contexts_str = ""
        if session_id in self.session_memory:
            for record in self.session_memory[session_id]:
                if "user" in record and record['user']:
                    text = record['user']['content'][:100] + "..." if len(record['user']['content']) > 100 else record['user']['content']
                    contexts_str += f"User: {text}\n"
                if "AI" in record and record['AI']:
                    text = record['AI']['content'][:100] + "..." if len(record['AI']['content']) > 100 else record['AI']['content']
                    contexts_str += f"Assistant: {text}\n"
        else:
            contexts_str = "会话 ID 不存在。"

        return contexts_str, len(self.session_memory[session_id])

    def set_model(self, model: str):
        # TODO: 更新配置文件
        super().set_curr_model(model)
    
    def get_configs(self):
        return asdict(self.llm_config)

    def get_keys_data(self):
        return self.keys_data

    def get_curr_key(self):
        return self.chosen_api_key

    def set_key(self, key):
        self.client.api_key = key