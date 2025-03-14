import asyncio
import functools
from typing import List
from .. import Provider, Personality
from ..entites import LLMResponse
from ..func_tool_manager import FuncCall
from astrbot.core.db import BaseDatabase
from ..register import register_provider_adapter
from .openai_source import ProviderOpenAIOfficial
from astrbot.core import logger, sp
from dashscope import Application


@register_provider_adapter("dashscope", "Dashscope APP 适配器。")
class ProviderDashscope(ProviderOpenAIOfficial):
    def __init__(
        self,
        provider_config: dict,
        provider_settings: dict,
        db_helper: BaseDatabase,
        persistant_history=False,
        default_persona: Personality = None,
    ) -> None:
        Provider.__init__(
            self,
            provider_config,
            provider_settings,
            persistant_history,
            db_helper,
            default_persona,
        )
        self.api_key = provider_config.get("dashscope_api_key", "")
        if not self.api_key:
            raise Exception("阿里云百炼 API Key 不能为空。")
        self.app_id = provider_config.get("dashscope_app_id", "")
        if not self.app_id:
            raise Exception("阿里云百炼 APP ID 不能为空。")
        self.dashscope_app_type = provider_config.get("dashscope_app_type", "")
        if not self.dashscope_app_type:
            raise Exception("阿里云百炼 APP 类型不能为空。")
        self.model_name = "dashscope"
        self.variables: dict = provider_config.get("variables", {})

        self.timeout = provider_config.get("timeout", 120)
        if isinstance(self.timeout, str):
            self.timeout = int(self.timeout)

    async def text_chat(
        self,
        prompt: str,
        session_id: str = None,
        image_urls: List[str] = [],
        func_tool: FuncCall = None,
        contexts: List = None,
        system_prompt: str = None,
        stream=False,
        **kwargs,
    ) -> LLMResponse:
        # 获得会话变量
        payload_vars = self.variables.copy()
        # 动态变量
        session_vars = sp.get("session_variables", {})
        session_var = session_vars.get(session_id, {})
        payload_vars.update(session_var)

        if self.dashscope_app_type in ["agent", "dialog-workflow"]:
            # 支持多轮对话的
            new_record = {"role": "user", "content": prompt}
            if image_urls:
                logger.warning("阿里云百炼暂不支持图片输入，将自动忽略图片内容。")
            contexts_no_img = await self._remove_image_from_context(contexts)
            context_query = [*contexts_no_img, new_record]
            if system_prompt:
                context_query.insert(0, {"role": "system", "content": system_prompt})
            for part in context_query:
                if "_no_save" in part:
                    del part["_no_save"]
            # 调用阿里云百炼 API
            partial = functools.partial(
                Application.call,
                app_id=self.app_id,
                api_key=self.api_key,
                messages=context_query,
                biz_params=payload_vars or None,
            )
            response = await asyncio.get_event_loop().run_in_executor(None, partial)
        else:
            # 不支持多轮对话的
            # 调用阿里云百炼 API
            partial = functools.partial(
                Application.call,
                app_id=self.app_id,
                promtp=prompt,
                api_key=self.api_key,
                biz_params=payload_vars or None,
            )
            response = await asyncio.get_event_loop().run_in_executor(None, partial)

        logger.debug(f"dashscope resp: {response}")

        if response.status_code != 200:
            logger.error(
                f"阿里云百炼请求失败: request_id={response.request_id}, code={response.status_code}, message={response.message}, 请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code"
            )
            return LLMResponse(
                role="err",
                completion_text=f"阿里云百炼请求失败: message={response.message} code={response.status_code}",
            )

        output_text = response.output.get("text", "")
        return LLMResponse(role="assistant", completion_text=output_text)

    async def forget(self, session_id):
        return True

    async def get_current_key(self):
        return self.api_key

    async def set_key(self, key):
        raise Exception("阿里云百炼 适配器不支持设置 API Key。")

    async def get_models(self):
        return [self.get_model()]

    async def get_human_readable_context(self, session_id, page, page_size):
        raise Exception("暂不支持获得 阿里云百炼 的历史消息记录。")

    async def terminate(self):
        pass
