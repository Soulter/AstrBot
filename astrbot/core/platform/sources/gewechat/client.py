import threading
import asyncio
import aiohttp
import quart
import base64
import datetime
import re
from astrbot.api.platform import AstrBotMessage, MessageMember, MessageType
from astrbot.api.message_components import Plain, Image, At, Record
from astrbot.api import logger, sp
from astrbot.core.utils.io import download_image_by_url

from .api.contact_api import ContactApi
from .api.download_api import DownloadApi
from .api.favor_api import FavorApi
from .api.group_api import GroupApi
from .api.label_api import LabelApi
from .api.login_api import LoginApi
from .api.message_api import MessageApi
from .api.personal_api import PersonalApi


class GewechatClient():
    '''对接 Gewechat 的接口。
    
    @author: Soulter
    @modified: diudiu62
    @date: 2025-02-18 14:56:30
    @website: https://github.com/Soulter
    '''
    def __init__(self, base_url: str, nickname: str, host: str, port: int, event_queue: asyncio.Queue):
        self.base_url = base_url
        if self.base_url.endswith('/'):
            self.base_url = self.base_url[:-1]
            
        self.download_base_url = self.base_url.split(':')[:-1] # 去掉端口
        self.download_base_url = ':'.join(self.download_base_url) + ":2532/download/"
        
        self.base_url += "/v2/api"
        
        logger.info(f"Gewechat API: {self.base_url}")
        logger.info(f"Gewechat 下载 API: {self.download_base_url}")
        
        if isinstance(port, str):
            port = int(port)
            
        self.token = None
        self.headers = {}
        self.nickname = nickname
        self.appid = sp.get(f"gewechat-appid-{nickname}", "")

        self.server = quart.Quart(__name__)
        self.server.add_url_rule('/astrbot-gewechat/callback', view_func=self.callback, methods=['POST'])
        self.server.add_url_rule('/astrbot-gewechat/file/<file_id>', view_func=self.handle_file, methods=['GET'])
        
        self.host = host
        self.port = port 
        self.callback_url = f"http://{self.host}:{self.port}/astrbot-gewechat/callback"
        self.file_server_url = f"http://{self.host}:{self.port}/astrbot-gewechat/file"
        
        self.event_queue = event_queue
        
        self.multimedia_downloader = None
        
        self._contact_api = None
        self._download_api = None
        self._favor_api = None
        self._group_api = None
        self._label_api = None
        self._login_api = None  
        self._message_api = None
        self._personal_api = None



    async def get_token_id(self):
        """获取tokenId"""
        self._login_api = LoginApi(self.base_url, self.token)

        json_blob = await self._login_api.get_token()
        self.token = json_blob['data']
        logger.info(f"获取到 Gewechat Token: {self.token}")
        self.headers = {
                    "X-GEWE-TOKEN": self.token
                }
        
        self._contact_api = ContactApi(self.base_url, self.token)
        self._download_api = DownloadApi(self.base_url, self.token)
        self._favor_api = FavorApi(self.base_url, self.token)
        self._group_api = GroupApi(self.base_url, self.token)
        self._label_api = LabelApi(self.base_url, self.token)
        self._login_api = LoginApi(self.base_url, self.token)
        self._message_api = MessageApi(self.base_url, self.token)
        self._personal_api = PersonalApi(self.base_url, self.token)
        return 
                
    async def _convert(self, data: dict) -> AstrBotMessage:
        type_name = data['TypeName']
        if type_name == "Offline":
            logger.critical("收到 gewechat 下线通知。")
            return
        
        if type_name == "ModContacts":
            logger.info("更新通讯录成功。")
            return
        
        if 'Data' in data and 'CreateTime' in data['Data']:
            # 得到系统 UTF+8 的 ts
            tz_offset = datetime.timedelta(hours=8)
            tz = datetime.timezone(tz_offset)
            ts = datetime.datetime.now(tz).timestamp()
            create_time = data['Data']['CreateTime']
            if create_time < ts - 30:
                logger.warning(f"消息时间戳过旧: {create_time}，当前时间戳: {ts}")
                return

        
        abm = AstrBotMessage()
        d = data['Data']
    
        from_user_name = d['FromUserName']['string'] # 消息来源
        d['to_wxid'] = from_user_name # 用于发信息
        
        abm.message_id = str(d.get('MsgId'))
        abm.session_id = from_user_name
        abm.self_id = data['Wxid'] # 机器人的 wxid
        
        user_id = "" # 发送人 wxid
        content = d['Content']['string'] # 消息内容
        
        at_me = False
        if "@chatroom" in from_user_name:
            abm.type = MessageType.GROUP_MESSAGE
            _t = content.split(':\n')
            user_id = _t[0]
            content = _t[1]
            if '\u2005' in content: 
                # at
                # content = content.split('\u2005')[1]
                content = re.sub(r'@[^\u2005]*\u2005', '', content)
            abm.group_id = from_user_name
            # at
            msg_source = d['MsgSource']
            if f'<atuserlist><![CDATA[,{abm.self_id}]]>' in msg_source \
                or f'<atuserlist><![CDATA[{abm.self_id}]]>' in msg_source:
                at_me = True
            if '在群聊中@了你' in d.get('PushContent', ''):
                at_me = True
        else:
            abm.type = MessageType.FRIEND_MESSAGE
            user_id = from_user_name
            
        abm.message = []
        if at_me:
            abm.message.insert(0, At(qq=abm.self_id))
        
        user_real_name = d.get('PushContent', 'unknown : ').split(' : ')[0] \
            .replace('在群聊中@了你', '') \
            .replace('在群聊中发了一段语音', '') \
            .replace('在群聊中发了一张图片', '') # 真实昵称
        abm.sender = MessageMember(user_id, user_real_name)
        abm.raw_message = d
        abm.message_str = ""
        # 不同消息类型
        match d['MsgType']:
            case 1:
                # 文本消息
                abm.message.append(Plain(content))
                abm.message_str = content
            case 3:
                # 图片消息
                file_url = await self.multimedia_downloader.download_image(
                    self.appid, 
                    content
                )
                logger.debug(f"下载图片: {file_url}")
                file_path = await download_image_by_url(file_url)
                abm.message.append(Image(file=file_path, url=file_path))
                
            case 34:
                # 语音消息
                # data = await self.multimedia_downloader.download_voice(
                #     self.appid, 
                #     content, 
                #     abm.message_id
                # )
                # print(data)
                if 'ImgBuf' in d and 'buffer' in d['ImgBuf']:
                    voice_data = base64.b64decode(d['ImgBuf']['buffer'])
                    file_path = f"data/temp/gewe_voice_{abm.message_id}.silk"
                    with open(file_path, "wb") as f:
                        f.write(voice_data)
                    abm.message.append(Record(file=file_path, url=file_path))
            case _:
                logger.info(f"未实现的消息类型: {d['MsgType']}")
                abm.raw_message = d
        
        logger.debug(f"abm: {abm}")
        return abm

    async def callback(self):
        data = await quart.request.json
        logger.debug(f"收到 gewechat 回调: {data}")
        
        if data.get('testMsg', None):
            return quart.jsonify({"r": "AstrBot ACK"})
        
        abm = None
        try:
            abm = await self._convert(data)
        except BaseException as e:
            logger.warning(f"尝试解析 GeweChat 下发的消息时遇到问题: {e}。下发消息内容: {data}。")
            
        if abm:
            coro = getattr(self, "on_event_received")
            if coro:
                await coro(abm)
        
        return quart.jsonify({"r": "AstrBot ACK"})
    
    async def handle_file(self, file_id):
        file_path = f"data/temp/{file_id}"
        return await quart.send_file(file_path)
    

    async def start_polling(self):
        threading.Thread(target=asyncio.run, args=(self._set_callback_url(),)).start()
        await self.server.run_task(
            host='0.0.0.0', 
            port=self.port, 
            shutdown_trigger=self.shutdown_trigger_placeholder
        )
    
    async def shutdown_trigger_placeholder(self):
        while not self.event_queue.closed:
            await asyncio.sleep(1)
        logger.info("gewechat 适配器已关闭。")
            
    






    
    # 定义gewechat接口

    async def fetch_contacts_list(self):
        """获取通讯录列表"""
        return await self._contact_api.fetch_contacts_list(self.appid)

    async def get_brief_info(self, wxids):
        """获取群/好友简要信息"""
        return await self._contact_api.get_brief_info(self.appid, wxids)

    async def get_detail_info(self, wxids):
        """获取群/好友详细信息"""
        return await self._contact_api.get_detail_info(self.appid, wxids)

    async def search_contacts(self, contacts_info):
        """搜索好友"""
        return await self._contact_api.search(self.appid, contacts_info)

    async def add_contacts(self, scene, option, v3, v4, content):
        """添加联系人/同意添加好友"""
        return await self._contact_api.add_contacts(self.appid, scene, option, v3, v4, content)

    async def delete_friend(self, wxid):
        """删除好友"""
        return await self._contact_api.delete_friend(self.appid, wxid)

    async def set_friend_permissions(self, wxid, only_chat):
        """设置好友仅聊天"""
        return await self._contact_api.set_friend_permissions(self.appid, wxid, only_chat)

    async def set_friend_remark(self, wxid, remark):
        """设置好友备注"""
        return await self._contact_api.set_friend_remark(self.appid, wxid, remark)

    async def get_phone_address_list(self, phones):
        """获取手机通讯录"""
        return await self._contact_api.get_phone_address_list(self.appid, phones)

    async def upload_phone_address_list(self, phones, op_type):
        """上传手机通讯录"""
        return await self._contact_api.upload_phone_address_list(self.appid, phones, op_type)

    async def sync_favor(self, sync_key):
        """同步收藏夹"""
        return await self._favor_api.sync(self.appid, sync_key)
    
    async def get_favor_content(self, fav_id):
        """获取收藏夹"""
        return await self._favor_api.get_content(self.appid, fav_id)

    async def delete_favor(self, fav_id):
        """删除收藏夹"""
        return await self._favor_api.delete(self.appid, fav_id)

    async def download_image(self, xml, type):
        """下载图片"""
        return await self._download_api.download_image(self.appid, xml, type)

    async def download_voice(self, xml, msg_id):
        """下载语音"""
        return await self._download_api.download_voice(self.appid, xml, msg_id)

    async def download_video(self, xml):
        """下载视频"""
        return await self._download_api.download_video(self.appid, xml)

    async def download_emoji_md5(self, emoji_md5):
        """下载emoji"""
        return await self._download_api.download_emoji_md5(self.appid, emoji_md5)

    async def download_cdn(self, aes_key, file_id, type, total_size, suffix):
        """cdn下载"""
        return await self._download_api.download_cdn(self.appid, aes_key, file_id, type, total_size, suffix)

    # Group API methods
    async def create_chatroom(self, wxids):
        """创建微信群"""
        return await self._group_api.create_chatroom(self.appid, wxids)

    async def modify_chatroom_name(self, chatroom_name, chatroom_id):
        """修改群名称"""
        return await self._group_api.modify_chatroom_name(self.appid, chatroom_name, chatroom_id)

    async def modify_chatroom_remark(self, chatroom_remark, chatroom_id):
        """修改群备注"""
        return await self._group_api.modify_chatroom_remark(self.appid, chatroom_remark, chatroom_id)

    async def modify_chatroom_nickname_for_self(self, nick_name, chatroom_id):
        """修改我在群内的昵称"""
        return await self._group_api.modify_chatroom_nickname_for_self(self.appid, nick_name, chatroom_id)

    async def invite_member(self, wxids, chatroom_id, reason):
        """邀请/添加 进群"""
        return await self._group_api.invite_member(self.appid, wxids, chatroom_id, reason)

    async def remove_member(self, wxids, chatroom_id):
        """删除群成员"""
        return await self._group_api.remove_member(self.appid, wxids, chatroom_id)

    async def quit_chatroom(self, chatroom_id):
        """退出群聊"""
        return await self._group_api.quit_chatroom(self.appid, chatroom_id)

    async def disband_chatroom(self, chatroom_id):
        """解散群聊"""
        return await self._group_api.disband_chatroom(self.appid, chatroom_id)

    async def get_chatroom_info(self, chatroom_id):
        """获取群信息"""
        return await self._group_api.get_chatroom_info(self.appid, chatroom_id)

    async def get_chatroom_member_list(self, chatroom_id):
        """获取群成员列表"""
        return await self._group_api.get_chatroom_member_list(self.appid, chatroom_id)

    async def get_chatroom_member_detail(self, chatroom_id, member_wxids):
        """获取群成员详情"""
        return await self._group_api.get_chatroom_member_detail(self.appid, chatroom_id, member_wxids)

    async def get_chatroom_announcement(self, chatroom_id):
        """获取群公告"""
        return await self._group_api.get_chatroom_announcement(self.appid, chatroom_id)

    async def set_chatroom_announcement(self, chatroom_id, content):
        """设置群公告"""
        return await self._group_api.set_chatroom_announcement(self.appid, chatroom_id, content)

    async def agree_join_room(self, url):
        """同意进群"""
        return await self._group_api.agree_join_room(self.appid, url)

    async def add_group_member_as_friend(self, member_wxid, chatroom_id, content):
        """添加群成员为好友"""
        return await self._group_api.add_group_member_as_friend(self.appid, member_wxid, chatroom_id, content)

    async def get_chatroom_qr_code(self, chatroom_id):
        """获取群二维码"""
        return await self._group_api.get_chatroom_qr_code(self.appid, chatroom_id)

    async def save_contract_list(self, oper_type, chatroom_id):
        """群保存到通讯录或从通讯录移除"""
        return await self._group_api.save_contract_list(self.appid, oper_type, chatroom_id)

    async def admin_operate(self, chatroom_id, wxids, oper_type):
        """管理员操作"""
        return await self._group_api.admin_operate(self.appid, chatroom_id, wxids, oper_type)

    async def pin_chat(self, top, chatroom_id):
        """聊天置顶"""
        return await self._group_api.pin_chat(self.appid, top, chatroom_id)

    async def set_msg_silence(self, silence, chatroom_id):
        """设置消息免打扰"""
        return await self._group_api.set_msg_silence(self.appid, silence, chatroom_id)

    async def join_room_using_qr_code(self, qr_url):
        """扫码进群"""
        return await self._group_api.join_room_using_qr_code(self.appid, qr_url)

    async def room_access_apply_check_approve(self, new_msg_id, chatroom_id, msg_content):
        """确认进群申请"""
        return await self._group_api.room_access_apply_check_approve(self.appid, new_msg_id, chatroom_id, msg_content)

    # Label API methods
    async def add_label(self, label_name):
        """添加标签"""
        return await self._label_api.add(self.appid, label_name)

    async def delete_label(self, label_ids):
        """删除标签"""
        return await self._label_api.delete(self.appid, label_ids)

    async def list_labels(self):
        """获取标签列表"""
        return await self._label_api.list(self.appid)

    async def modify_label_member_list(self, label_ids, wx_ids):
        """修改标签成员列表"""
        return await self._label_api.modify_member_list(self.appid, label_ids, wx_ids)

    # Personal API methods
    async def get_profile(self):
        """获取个人资料"""
        return await self._personal_api.get_profile(self.appid)

    async def get_qr_code(self):
        """获取自己的二维码"""
        return await self._personal_api.get_qr_code(self.appid)

    async def get_safety_info(self):
        """获取设备记录"""
        return await self._personal_api.get_safety_info(self.appid)

    async def privacy_settings(self, option, open):
        """隐私设置"""
        return await self._personal_api.privacy_settings(self.appid, option, open)

    async def update_profile(self, city, country, nick_name, province, sex, signature):
        """修改个人信息"""
        return await self._personal_api.update_profile(self.appid, city, country, nick_name, province, sex, signature)

    async def update_head_img(self, head_img_url):
        """修改头像"""
        return await self._personal_api.update_head_img(self.appid, head_img_url)

    # Login API methods
    async def login(self):
        """登录"""
        if self.token is None:
            await self.get_token_id()
        appid = await self._login_api.login(self.appid)
        if appid:
            sp.put(f"gewechat-appid-{self.nickname}", appid)
            self.appid = appid
            logger.info(f"已保存 APPID: {appid}")
        return

    async def get_token(self):
        """获取tokenId"""
        return await self._login_api.get_token()

    async def _set_callback_url(self):
        """设置微信消息的回调地址"""
        return await self._login_api.set_callback(self.token, self.callback_url)

    async def get_qr(self):
        """获取登录二维码"""
        return await self._login_api.get_qr(self.appid)

    async def check_qr(self, uuid, captch_code):
        """确认登陆"""
        return await self._login_api.check_qr(self.appid, uuid, captch_code)

    async def log_out(self):
        """退出微信"""
        return await self._login_api.log_out(self.appid)

    async def dialog_login(self):
        """弹框登录"""
        return await self._login_api.dialog_login(self.appid)

    async def check_online(self):
        """检查是否在线"""
        return await self._login_api.check_online(self.appid)

    async def logout(self):
        """退出"""
        return await self._login_api.logout(self.appid)

    # Message API methods
    async def post_text(self, to_wxid, content, ats: str = ""):
        """发送文字消息"""
        return await self._message_api.post_text(self.appid, to_wxid, content, ats)

    async def post_file(self, to_wxid, file_url, file_name):
        """发送文件消息"""
        return await self._message_api.post_file(self.appid, to_wxid, file_url, file_name)

    async def post_image(self, to_wxid, img_url):
        """发送图片消息"""
        return await self._message_api.post_image(self.appid, to_wxid, img_url)

    async def post_voice(self, to_wxid, voice_url, voice_duration):
        """发送语音消息"""
        return await self._message_api.post_voice(self.appid, to_wxid, voice_url, voice_duration)

    async def post_video(self, to_wxid, video_url, thumb_url, video_duration):
        """发送视频消息"""
        return await self._message_api.post_video(self.appid, to_wxid, video_url, thumb_url, video_duration)

    async def post_link(self, to_wxid, title, desc, link_url, thumb_url):
        """发送链接消息"""
        return await self._message_api.post_link(self.appid, to_wxid, title, desc, link_url, thumb_url)

    async def post_name_card(self, to_wxid, nick_name, name_card_wxid):
        """发送名片消息"""
        return await self._message_api.post_name_card(self.appid, to_wxid, nick_name, name_card_wxid)

    async def post_emoji(self, to_wxid, emoji_md5, emoji_size):
        """发送emoji消息"""
        return await self._message_api.post_emoji(self.appid, to_wxid, emoji_md5, emoji_size)

    async def post_app_msg(self, to_wxid, appmsg):
        """发送appmsg消息"""
        return await self._message_api.post_app_msg(self.appid, to_wxid, appmsg)

    async def post_mini_app(self, to_wxid, mini_app_id, display_name, page_path, cover_img_url, title, user_name):
        """发送小程序消息"""
        return await self._message_api.post_mini_app(self.appid, to_wxid, mini_app_id, display_name, page_path, cover_img_url, title, user_name)

    async def forward_file(self, to_wxid, xml):
        """转发文件"""
        return await self._message_api.forward_file(self.appid, to_wxid, xml)

    async def forward_image(self, to_wxid, xml):
        """转发图片"""
        return await self._message_api.forward_image(self.appid, to_wxid, xml)

    async def forward_video(self, to_wxid, xml):
        """转发视频"""
        return await self._message_api.forward_video(self.appid, to_wxid, xml)

    async def forward_url(self, to_wxid, xml):
        """转发链接"""
        return await self._message_api.forward_url(self.appid, to_wxid, xml)

    async def forward_mini_app(self, to_wxid, xml, cover_img_url):
        """转发小程序"""
        return await self._message_api.forward_mini_app(self.appid, to_wxid, xml, cover_img_url)

    async def revoke_msg(self, to_wxid, msg_id, new_msg_id, create_time):
        """撤回消息"""
        return await self._message_api.revoke_msg(self.appid, to_wxid, msg_id, new_msg_id, create_time)