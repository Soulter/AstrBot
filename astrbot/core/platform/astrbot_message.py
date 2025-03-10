import time
from typing import List, Dict, Any
from dataclasses import dataclass
from astrbot.core.message.components import BaseMessageComponent
from .message_type import MessageType


@dataclass
class MessageMember:
    user_id: str  # 发送者id
    nickname: str = None

    # 群id
    group_id: str = None


@dataclass
class Group:
    group_id: str
    group_name: str = None

    # 群头像
    group_avatar: str = None

    # 群主id
    group_owner: str = None

    # 群管理员id
    group_admin: str = None

    # 群成员
    members: List[MessageMember] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Group":
        # 提取members信息并转换为MessageMember对象
        members = [
            MessageMember(user_id=member["wxid"], nickname=member["nickName"])
            for member in data.get("memberList", [])
        ]

        return cls(
            group_id=data["chatroomId"],
            group_name=data.get("nickName"),
            group_avatar=data.get("smallHeadImgUrl"),
            group_owner=data.get("chatRoomOwner"),
            members=members,
        )


class AstrBotMessage:
    """
    AstrBot 的消息对象
    """

    type: MessageType  # 消息类型
    self_id: str  # 机器人的识别id
    session_id: str  # 会话id。取决于 unique_session 的设置。
    message_id: str  # 消息id
    group_id: str = ""  # 群组id，如果为私聊，则为空
    sender: MessageMember  # 发送者
    message: List[BaseMessageComponent]  # 消息链使用 Nakuru 的消息链格式
    message_str: str  # 最直观的纯文本消息字符串
    raw_message: object
    timestamp: int  # 消息时间戳

    def __init__(self) -> None:
        self.timestamp = int(time.time())

    def __str__(self) -> str:
        return str(self.__dict__)
