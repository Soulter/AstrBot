from defusedxml import ElementTree as ET
from astrbot.api import logger
from astrbot.api.message_components import Emoji


class GeweDataPaser:
    def __init__(self, data, is_private_chat):
        self.data = data
        self.is_private_chat = is_private_chat

    def _format_to_xml(self):
        return ET.fromstring(self.data)

    def parse_emoji(self) -> Emoji | None:
        try:
            emoji_element = self._format_to_xml().find(".//emoji")
            # 提取 md5 和 len 属性
            if emoji_element is not None:
                md5_value = emoji_element.get("md5")
                emoji_size = emoji_element.get("len")
                cdnurl = emoji_element.get("cdnurl")

                return Emoji(md5=md5_value, md5_len=emoji_size, cdnurl=cdnurl)

        except Exception as e:
            logger.error(f"parse_emoji failed, {e}")
