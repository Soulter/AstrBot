import io

import botpy
from PIL import Image
from botpy.message import Message
from botpy.types.message import Reference
import yaml
import re
from util.errors.errors import PromptExceededError
from botpy.message import DirectMessage
import json
import threading
import asyncio
import time
import requests
import util.unfit_words as uw
import os
import sys
from cores.qqbot.personality import personalities
from addons.baidu_aip_judge import BaiduJudge


# QQBotClient实例
client = ''
# ChatGPT实例
global chatgpt
# 缓存的会话
session_dict = {}
# 最大缓存token（在配置里改 configs/config.yaml）
max_tokens = 2000
# 配置信息
config = {}
# 统计信息
count = {}
# 统计信息
stat_file = ''
# 是否独立会话默认值
uniqueSession = False

# 日志记录
logf = open('log.log', 'a+', encoding='utf-8')
# 是否上传日志,仅上传频道数量等数量的统计信息
is_upload_log = True

# 用户发言频率
user_frequency = {}
# 时间默认值
frequency_time = 60
# 计数默认值
frequency_count = 2

# 公告（可自定义）：
announcement = ""

# 机器人私聊模式
direct_message_mode = True

# 适配pyinstaller
abs_path = os.path.dirname(os.path.realpath(sys.argv[0])) + '/'

# 版本
version = '2.9'

# 语言模型
REV_CHATGPT = 'rev_chatgpt'
OPENAI_OFFICIAL = 'openai_official'
REV_ERNIE = 'rev_ernie'
REV_EDGEGPT = 'rev_edgegpt'
provider = None
chosen_provider = None

# 逆向库对象
rev_chatgpt = None
# gpt配置信息
gpt_config = {}
# 百度内容审核实例
baidu_judge = None
# 回复前缀
reply_prefix = {}


def new_sub_thread(func, args=()):
    thread = threading.Thread(target=func, args=args, daemon=True)
    thread.start() 

class botClient(botpy.Client):
    # 收到At消息
    async def on_at_message_create(self, message: Message):
        toggle_count(at=True, message=message)
        message_reference = Reference(message_id=message.id, ignore_get_message_error=False)
        # executor.submit(oper_msg, message, True)
        new_sub_thread(oper_msg, (message, True, message_reference))
        # await oper_msg(message=message, at=True)

    # 收到私聊消息
    async def on_direct_message_create(self, message: DirectMessage):
        if direct_message_mode:
            toggle_count(at=False, message=message)
            # executor.submit(oper_msg, message, True)
            # await oper_msg(message=message, at=False)
            new_sub_thread(oper_msg, (message, False))

# 写入统计信息
def toggle_count(at: bool, message):
    global stat_file
    try: 
        if str(message.guild_id) not in count:
            count[str(message.guild_id)] = {
                'count': 1,
                'direct_count': 1,
            }
        else:
            count[str(message.guild_id)]['count'] += 1
            if not at:
                count[str(message.guild_id)]['direct_count'] += 1
        stat_file = open(abs_path+"configs/stat", 'w', encoding='utf-8')
        stat_file.write(json.dumps(count))
        stat_file.flush()
        stat_file.close()
    except BaseException:
        pass

# 上传统计信息并检查更新
def upload():
    global object_id
    global version
    while True:
        addr = ''
        try:
            # 用户唯一性标识
            addr = requests.get('http://myip.ipip.net', timeout=5).text
        except BaseException:
            pass
        try:
            ts = str(time.time())
            guild_count, guild_msg_count, guild_direct_msg_count, session_count = get_stat()
            headers = {
                'X-LC-Id': 'UqfXTWW15nB7iMT0OHvYrDFb-gzGzoHsz',
                'X-LC-Key': 'QAZ1rQLY1ZufHrZlpuUiNff7',
                'Content-Type': 'application/json'
            }
            key_stat = chatgpt.get_key_stat()
            d = {"data": {'version': version, "guild_count": guild_count, "guild_msg_count": guild_msg_count, "guild_direct_msg_count": guild_direct_msg_count, "session_count": session_count, 'addr': addr, 'key_stat':key_stat}}
            d = json.dumps(d).encode("utf-8")
            res = requests.put(f'https://uqfxtww1.lc-cn-n1-shared.com/1.1/classes/bot_record/{object_id}', headers = headers, data = d)
            if json.loads(res.text)['code'] == 1:
                print("[System] New User.")
                res = requests.post(f'https://uqfxtww1.lc-cn-n1-shared.com/1.1/classes/bot_record', headers = headers, data = d)
                object_id = json.loads(res.text)['objectId']
                object_id_file = open(abs_path+"configs/object_id", 'w+', encoding='utf-8')
                object_id_file.write(str(object_id))
                object_id_file.flush()
                object_id_file.close()
        except BaseException as e:
            pass
        # 每隔2小时上传一次
        time.sleep(60*60*2)

'''
初始化机器人
'''
def initBot(cfg, prov):
    global chatgpt, provider, rev_chatgpt, baidu_judge, rev_edgegpt, chosen_provider
    global reply_prefix, gpt_config, config, uniqueSession, frequency_count, frequency_time,announcement, direct_message_mode, version
    global command_openai_official, command_rev_chatgpt, command_rev_edgegpt,reply_prefix
    provider = prov
    config = cfg
    if 'reply_prefix' in cfg:
        reply_prefix = cfg['reply_prefix']

    # 语言模型提供商
    if REV_CHATGPT in prov:
        if 'account' in cfg['rev_ChatGPT']:
            from model.provider.provider_rev_chatgpt import ProviderRevChatGPT
            from model.command.command_rev_chatgpt import CommandRevChatGPT
            rev_chatgpt = ProviderRevChatGPT(cfg['rev_ChatGPT'])
            command_rev_chatgpt = CommandRevChatGPT(cfg['rev_ChatGPT'])
            chosen_provider = REV_CHATGPT
        else:
            input("[System-err] 请退出本程序, 然后在配置文件中填写rev_ChatGPT相关配置")
        
    if REV_EDGEGPT in prov:
        from model.provider.provider_rev_edgegpt import ProviderRevEdgeGPT
        from model.command.command_rev_edgegpt import CommandRevEdgeGPT
        rev_edgegpt = ProviderRevEdgeGPT()
        command_rev_edgegpt = CommandRevEdgeGPT(rev_edgegpt)
        chosen_provider = REV_EDGEGPT
    if OPENAI_OFFICIAL in prov:
        from model.provider.provider_openai_official import ProviderOpenAIOfficial
        from model.command.command_openai_official import CommandOpenAIOfficial
        chatgpt = ProviderOpenAIOfficial(cfg['openai'])
        command_openai_official = CommandOpenAIOfficial(chatgpt)
        chosen_provider = OPENAI_OFFICIAL

    # 检查provider设置偏好
    if os.path.exists("provider_preference.txt"):
        with open("provider_preference.txt", 'r', encoding='utf-8') as f:
            res = f.read()
            if res in prov:
                chosen_provider = res
        

    # 百度内容审核
    if 'baidu_aip' in cfg and 'enable' in cfg['baidu_aip'] and cfg['baidu_aip']['enable']:
        try: 
            baidu_judge = BaiduJudge(cfg['baidu_aip'])
            print("[System] 百度内容审核初始化成功")
        except BaseException as e:
            input("[System] 百度内容审核初始化失败: " + str(e))
            exit()
        
    # 统计上传
    if is_upload_log:
        # 读取object_id
        global object_id
        if not os.path.exists(abs_path+"configs/object_id"):
            with open(abs_path+"configs/object_id", 'w', encoding='utf-8') as f:
                f.write("")
        object_id_file = open(abs_path+"configs/object_id", 'r', encoding='utf-8')
        object_id = object_id_file.read()
        object_id_file.close()
        # 创建上传定时器线程
        threading.Thread(target=upload, daemon=True).start()
    
    # 得到私聊模式配置
    if 'direct_message_mode' in cfg:
        direct_message_mode = cfg['direct_message_mode']
        print("[System] 私聊功能: "+str(direct_message_mode))

    # 得到版本
    if 'version' in cfg:
        try:
            f = open(abs_path+"version.txt", 'r', encoding='utf-8')
            version = f.read()
        except:
            print('[System-Err] 读取更新记录文件失败')

    # 得到发言频率配置
    if 'limit' in cfg:
        print('[System] 发言频率配置: '+str(cfg['limit']))
        if 'count' in cfg['limit']:
            frequency_count = cfg['limit']['count']
        if 'time' in cfg['limit']:
            frequency_time = cfg['limit']['time']
    
    announcement += '[QQChannelChatGPT项目，觉得好用的话欢迎前往Github给Star]\n所有回答与腾讯公司无关。出现问题请前往[GPT机器人]官方频道\n\n'
    # 得到公告配置
    if 'notice' in cfg:
        print('[System] 公告配置: '+cfg['notice'])
        announcement += cfg['notice']
    try:
        if 'uniqueSessionMode' in cfg and cfg['uniqueSessionMode']:
            uniqueSession = True
        else:
            uniqueSession = False
        print("[System] 独立会话: " + str(uniqueSession))
        if 'dump_history_interval' in cfg:
            print("[System] 历史记录转储时间周期: " + cfg['dump_history_interval'] + "分钟")
    except BaseException:
        print("[System-Error] 读取uniqueSessionMode/version/dump_history_interval配置文件失败, 使用默认值。")

    print(f"[System] QQ开放平台AppID: {cfg['qqbot']['appid']} 令牌: {cfg['qqbot']['token']}")

    print("\n[System] 如果有任何问题，请在https://github.com/Soulter/QQChannelChatGPT上提交issue说明问题！或者添加QQ：905617992")
    print("[System] 请给https://github.com/Soulter/QQChannelChatGPT点个star!")
    print("[System] 请给https://github.com/Soulter/QQChannelChatGPT点个star!")
    # input("\n仔细阅读完以上信息后，输入任意信息并回车以继续")
    try:
        run_bot(cfg['qqbot']['appid'], cfg['qqbot']['token'])
    except BaseException as e:
        input(f"\n[System-Error] 启动QQ机器人时出现错误，原因如下：{e}\n可能是没有填写QQBOT appid和token？请在config中完善你的appid和token\n配置教程：https://soulter.top/posts/qpdg.html\n")

        
'''
启动机器人
'''
def run_bot(appid, token):
    intents = botpy.Intents(public_guild_messages=True, direct_message=True) 
    global client
    client = botClient(intents=intents)
    client.run(appid=appid, token=token)


'''
回复QQ消息
'''
def send_qq_msg(message, res, image_mode=False, msg_ref = None):
    if not image_mode:
        try:
            if msg_ref is not None:
                reply_res = asyncio.run_coroutine_threadsafe(message.reply(content=res, message_reference = msg_ref), client.loop)
            else:
                reply_res = asyncio.run_coroutine_threadsafe(message.reply(content=res), client.loop)
            reply_res.result()
        except BaseException as e:
            if "msg over length" in str(e):
                split_res = []
                split_res.append(res[:len(res)//2])      
                split_res.append(res[len(res)//2:])
                for i in split_res:
                    if msg_ref is not None:
                        reply_res = asyncio.run_coroutine_threadsafe(message.reply(content=i, message_reference = msg_ref), client.loop)
                    else:
                        reply_res = asyncio.run_coroutine_threadsafe(message.reply(content=i), client.loop)
                    reply_res.result()
            else:
                print("[System-Error] 回复QQ消息失败")
                raise e
    else:
        pic_res = requests.get(str(res), stream=True)
        if pic_res.status_code == 200:
            # 将二进制数据转换成图片对象
            image = Image.open(io.BytesIO(pic_res.content))
            # 保存图片到本地
            image.save('tmp_image.jpg')
        asyncio.run_coroutine_threadsafe(message.reply(file_image='tmp_image.jpg', content=""), client.loop)


'''
检查发言频率
'''
def check_frequency(id) -> bool:
    ts = int(time.time())
    if id in user_frequency:
        if ts-user_frequency[id]['time'] > frequency_time:
            user_frequency[id]['time'] = ts
            user_frequency[id]['count'] = 1
            return True
        else:
            if user_frequency[id]['count'] >= frequency_count:
                return False
            else:
                user_frequency[id]['count']+=1
                return True
    else:
        t = {'time':ts,'count':1}
        user_frequency[id] = t
        return True


def save_provider_preference(chosen_provider):
    with open('provider_preference.txt', 'w') as f:
        f.write(chosen_provider)
'''
处理消息
'''
def oper_msg(message, at=False, msg_ref = None):
    global session_dict, provider
    print("[QQBOT] 接收到消息："+ str(message.content))
    qq_msg = ''
    session_id = ''
    user_id = message.author.id
    user_name = message.author.username
    global chosen_provider, reply_prefix
    print(chosen_provider)
    
    # 检查发言频率
    if not check_frequency(user_id):
        send_qq_msg(message, f'{user_name}的发言超过频率限制(╯▔皿▔)╯。\n{frequency_time}秒内只能提问{frequency_count}次。')
        return

    logf.write("[QQBOT] "+ str(message.content)+'\n')
    logf.flush()

    if at:
        # 过滤@
        qq_msg = message.content
        lines = qq_msg.splitlines()
        for i in range(len(lines)):
            lines[i] = re.sub(r"<@!\d+>", "", lines[i])
        qq_msg = "\n".join(lines).lstrip().strip()

        if uniqueSession:
            session_id = user_id
        else:
            session_id = message.channel_id
    else:
        qq_msg = message.content
        session_id = user_id

    # 这里是预设
    if qq_msg.strip() == 'hello' or qq_msg.strip() == '你好' or qq_msg.strip() == '':
        send_qq_msg(message, f"你好呀🥰，输入/help查看指令噢", msg_ref=msg_ref)
        return
    
    # 关键词拦截器
    for i in uw.unfit_words_q:
        matches = re.match(i, qq_msg.strip(), re.I | re.M)
        if matches:
            send_qq_msg(message, f"你的提问得到的回复未通过【自有关键词拦截】服务，不予回复。", msg_ref=msg_ref)
            return
    if baidu_judge != None:
        check, msg = baidu_judge.judge(qq_msg)
        if not check:
            send_qq_msg(message, f"你的提问得到的回复未通过【百度AI内容审核】服务，不予回复。\n\n{msg}", msg_ref=msg_ref)
            return
    
    # 检查是否是更换语言模型的请求
    if qq_msg.startswith('/bing'):
        chosen_provider = REV_EDGEGPT
        save_provider_preference(chosen_provider)
        send_qq_msg(message, f"已切换至【{chosen_provider}】", msg_ref=msg_ref)
        return
    elif qq_msg.startswith('/gpt'):
        chosen_provider = OPENAI_OFFICIAL
        save_provider_preference(chosen_provider)
        send_qq_msg(message, f"已切换至【{chosen_provider}】", msg_ref=msg_ref)
        return
    elif qq_msg.startswith('/revgpt'):
        chosen_provider = REV_CHATGPT
        save_provider_preference(chosen_provider)
        send_qq_msg(message, f"已切换至【{chosen_provider}】", msg_ref=msg_ref)
        return

    chatgpt_res = ""

    if chosen_provider == OPENAI_OFFICIAL:
        # 检查指令
        hit, command_result = command_openai_official.check_command(qq_msg, session_id, user_name)
        print(f"{hit} {command_result}")
        # hit: 是否触发指令
        if hit:
            if command_result != None and command_result[0]:
                # 是否是画图模式
                if len(command_result) == 3 and command_result[2] == 'image':
                    for i in command_result[1]:
                        send_qq_msg(message, i, image_mode=True, msg_ref=command_result[2])
                else: 
                    try:
                        send_qq_msg(message, command_result[1], msg_ref=msg_ref)
                    except BaseException as e:
                        t = command_result[1].replace(".", " . ")
                        send_qq_msg(message, t, msg_ref=msg_ref)
            else:
                send_qq_msg(message, f"指令调用错误: \n{command_result[1]}", msg_ref=msg_ref)
            return
        # 请求chatGPT获得结果
        try:

            chatgpt_res = chatgpt.text_chat(qq_msg, session_id)
            if OPENAI_OFFICIAL in reply_prefix:
                chatgpt_res = reply_prefix[OPENAI_OFFICIAL] + chatgpt_res
        except (BaseException) as e:
            print("[System-Err] OpenAI API错误。原因如下:\n"+str(e))
            if 'exceeded' in str(e):
                send_qq_msg(message, f"OpenAI API错误。原因：\n{str(e)} \n超额了。可自己搭建一个机器人(Github仓库：QQChannelChatGPT)")
                return
            else:
                f_res = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '[被隐藏的链接]', str(e), flags=re.MULTILINE)
                f_res = f_res.replace(".", "·")
                send_qq_msg(message, f"OpenAI API错误。原因如下：\n{f_res} \n前往官方频道反馈~")
                return
        
    elif chosen_provider == REV_CHATGPT:
        hit, command_result = command_rev_chatgpt.check_command(qq_msg)
        if hit:
            if command_result != None and command_result[0]:
                try:
                    send_qq_msg(message, command_result[1], msg_ref=msg_ref)
                except BaseException as e:
                    t = command_result[1].replace(".", " . ")
                    send_qq_msg(message, t, msg_ref=msg_ref)
            else:
                send_qq_msg(message, f"指令调用错误: \n{command_result[1]}", msg_ref=msg_ref)
            return
        try:
            chatgpt_res = str(rev_chatgpt.text_chat(qq_msg))
            if REV_CHATGPT in reply_prefix:
                chatgpt_res = reply_prefix[REV_CHATGPT] + chatgpt_res
        except BaseException as e:
            print("[System-Err] Rev ChatGPT API错误。原因如下:\n"+str(e))
            send_qq_msg(message, f"Rev ChatGPT API错误。原因如下: \n{str(e)} \n前往官方频道反馈~")
            return
    elif chosen_provider == REV_EDGEGPT:
        hit, command_result = command_rev_edgegpt.check_command(qq_msg, client.loop)
        if hit:
            if command_result != None and command_result[0]:
                try:
                    send_qq_msg(message, command_result[1], msg_ref=msg_ref)
                except BaseException as e:
                    t = command_result[1].replace(".", " . ")
                    send_qq_msg(message, t, msg_ref=msg_ref)
            else:
                send_qq_msg(message, f"指令调用错误: \n{command_result[1]}", msg_ref=msg_ref)
            return
        try:
            if rev_edgegpt.is_busy():
                send_qq_msg(message, f"[RevBing] 正忙，请稍后再试",msg_ref=msg_ref)
                return
            else:
                res, res_code = asyncio.run_coroutine_threadsafe(rev_edgegpt.text_chat(qq_msg), client.loop).result()
                if res_code == 0: # bing不想继续话题，重置会话后重试。
                    send_qq_msg(message, f"Bing不想继续话题了, 正在自动重置会话并重试。", msg_ref=msg_ref)
                    asyncio.run_coroutine_threadsafe(rev_edgegpt.forget(), client.loop).result()
                    res, res_code = asyncio.run_coroutine_threadsafe(rev_edgegpt.text_chat(qq_msg), client.loop).result()
                    if res_code == 0: # bing还是不想继续话题，大概率说明提问有问题。
                        send_qq_msg(message, f"Bing仍然不想继续话题, 请检查您的提问。", msg_ref=msg_ref)
                        return
                chatgpt_res = str(res)
                if REV_EDGEGPT in reply_prefix:
                    chatgpt_res = reply_prefix[REV_EDGEGPT] + chatgpt_res
        except BaseException as e:
            print("[System-Err] Rev NewBing API错误。原因如下:\n"+str(e))
            send_qq_msg(message, f"Rev NewBing API错误。原因如下：\n{str(e)} \n前往官方频道反馈~")
            return
        
    # 记录日志
    logf.write(f"{reply_prefix} {str(chatgpt_res)}\n")
    logf.flush()

    # 敏感过滤
    # 过滤不合适的词
    judged_res = chatgpt_res
    for i in uw.unfit_words:
        judged_res = re.sub(i, "***", judged_res)
    # 百度内容审核服务二次审核
    if baidu_judge != None:
        check, msg = baidu_judge.judge(judged_res)
        if not check:
            send_qq_msg(message, f"你的提问得到的回复【百度内容审核】未通过，不予回复。\n\n{msg}", msg_ref=msg_ref)
            return
    # 发送qq信息
    try:
        # 防止被qq频道过滤消息
        gap_chatgpt_res = judged_res.replace(".", " . ")
        send_qq_msg(message, ''+gap_chatgpt_res, msg_ref=msg_ref)
        # 发送信息
    except BaseException as e:
        print("QQ频道API错误: \n"+str(e))
        f_res = ""
        for t in chatgpt_res:
            f_res += t + ' '
        try:
            send_qq_msg(message, ''+f_res, msg_ref=msg_ref)
            # send(message, f"QQ频道API错误：{str(e)}\n下面是格式化后的回答：\n{f_res}")
        except BaseException as e:
            # 如果还是不行则过滤url
            f_res = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '[被隐藏的链接]', str(e), flags=re.MULTILINE)
            f_res = f_res.replace(".", "·")
            send_qq_msg(message, ''+f_res, msg_ref=msg_ref)
            # send(message, f"QQ频道API错误：{str(e)}\n下面是格式化后的回答：\n{f_res}")

        
'''
获取统计信息
'''
def get_stat(self):
    try:
        f = open(abs_path+"configs/stat", "r", encoding="utf-8")
        fjson = json.loads(f.read())
        f.close()
        guild_count = 0
        guild_msg_count = 0
        guild_direct_msg_count = 0

        for k,v in fjson.items():
            guild_count += 1
            guild_msg_count += v['count']
            guild_direct_msg_count += v['direct_count']
        
        session_count = 0

        f = open(abs_path+"configs/session", "r", encoding="utf-8")
        fjson = json.loads(f.read())
        f.close()
        for k,v in fjson.items():
            session_count += 1
        return guild_count, guild_msg_count, guild_direct_msg_count, session_count
    except:
        return -1, -1, -1, -1