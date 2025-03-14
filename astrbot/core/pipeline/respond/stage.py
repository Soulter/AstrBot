import random
import asyncio
import math
import traceback
from typing import Union, AsyncGenerator
from ..stage import register_stage, Stage
from ..context import PipelineContext
from astrbot.core.platform.astr_message_event import AstrMessageEvent
from astrbot.core.message.message_event_result import MessageChain, ResultContentType
from astrbot.core import logger
from astrbot.core.message.message_event_result import BaseMessageComponent
from astrbot.core.star.star_handler import star_handlers_registry, EventType
from astrbot.core.star.star import star_map
from astrbot.core.message.components import Plain, Reply, At


@register_stage
class RespondStage(Stage):
    async def initialize(self, ctx: PipelineContext):
        self.ctx = ctx

        self.reply_with_mention = ctx.astrbot_config["platform_settings"][
            "reply_with_mention"
        ]
        self.reply_with_quote = ctx.astrbot_config["platform_settings"][
            "reply_with_quote"
        ]

        # 分段回复
        self.enable_seg: bool = ctx.astrbot_config["platform_settings"][
            "segmented_reply"
        ]["enable"]
        self.only_llm_result = ctx.astrbot_config["platform_settings"][
            "segmented_reply"
        ]["only_llm_result"]

        self.interval_method = ctx.astrbot_config["platform_settings"][
            "segmented_reply"
        ]["interval_method"]
        self.log_base = float(
            ctx.astrbot_config["platform_settings"]["segmented_reply"]["log_base"]
        )
        interval_str: str = ctx.astrbot_config["platform_settings"]["segmented_reply"][
            "interval"
        ]
        interval_str_ls = interval_str.replace(" ", "").split(",")
        try:
            self.interval = [float(t) for t in interval_str_ls]
        except BaseException as e:
            logger.error(f"解析分段回复的间隔时间失败。{e}")
            self.interval = [1.5, 3.5]
        logger.info(f"分段回复间隔时间：{self.interval}")

    async def _word_cnt(self, text: str) -> int:
        """分段回复 统计字数"""
        if all(ord(c) < 128 for c in text):
            word_count = len(text.split())
        else:
            word_count = len([c for c in text if c.isalnum()])
        return word_count

    async def _calc_comp_interval(self, comp: BaseMessageComponent) -> float:
        """分段回复 计算间隔时间"""
        if self.interval_method == "log":
            if isinstance(comp, Plain):
                wc = await self._word_cnt(comp.text)
                i = math.log(wc + 1, self.log_base)
                return random.uniform(i, i + 0.5)
            else:
                return random.uniform(1, 1.75)
        else:
            # random
            return random.uniform(self.interval[0], self.interval[1])

    async def process(
        self, event: AstrMessageEvent
    ) -> Union[None, AsyncGenerator[None, None]]:
        result = event.get_result()
        if result is None:
            return

        if result.result_content_type == ResultContentType.STREAMING_RESULT:
            # 流式结果直接交付平台适配器处理
            logger.info(f"应用流式输出({event.get_platform_name()})")
            await event._pre_send()
            await event.send_streaming(result.async_stream)
            await event._post_send()
            return

        elif len(result.chain) > 0:
            await event._pre_send()

            if self.enable_seg and (
                (self.only_llm_result and result.is_llm_result())
                or not self.only_llm_result
            ):
                decorated_comps = []
                if self.reply_with_mention:
                    for comp in result.chain:
                        if isinstance(comp, At):
                            decorated_comps.append(comp)
                            result.chain.remove(comp)
                            break
                if self.reply_with_quote:
                    for comp in result.chain:
                        if isinstance(comp, Reply):
                            decorated_comps.append(comp)
                            result.chain.remove(comp)
                            break
                # 分段回复
                for comp in result.chain:
                    i = await self._calc_comp_interval(comp)
                    await asyncio.sleep(i)
                    await event.send(MessageChain([*decorated_comps, comp]))
            else:
                await event.send(result)
            await event._post_send()
            logger.info(
                f"AstrBot -> {event.get_sender_name()}/{event.get_sender_id()}: {event._outline_chain(result.chain)}"
            )

        handlers = star_handlers_registry.get_handlers_by_event_type(
            EventType.OnAfterMessageSentEvent
        )
        for handler in handlers:
            try:
                logger.debug(
                    f"hook(on_after_message_sent) -> {star_map[handler.handler_module_path].name} - {handler.handler_name}"
                )
                await handler.handler(event)
            except BaseException:
                logger.error(traceback.format_exc())

            if event.is_stopped():
                logger.info(
                    f"{star_map[handler.handler_module_path].name} - {handler.handler_name} 终止了事件传播。"
                )
                return

        event.clear_result()
