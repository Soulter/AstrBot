import botpy
from botpy.message import Message
import yaml
import re
from util.errors.errors import PromptExceededError
from botpy.message import DirectMessage
import json
import threading
import asyncio
import time
from cores.database.conn import dbConn
import requests
import util.unfit_words as uw
import os
import sys
from cores.qqbot.personality import personalities


history_dump_interval = 10
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

# 人格信息
now_personality = {}

# 机器人私聊模式
direct_message_mode = True

# 适配pyinstaller
abs_path = os.path.dirname(os.path.realpath(sys.argv[0])) + '/'

# 版本
version = '2.4 RealChatGPT Ver.'

# gpt配置信息
gpt_config = {}

def new_sub_thread(func, args=()):
    thread = threading.Thread(target=func, args=args, daemon=True)
    thread.start() 

class botClient(botpy.Client):
    # 收到At消息
    async def on_at_message_create(self, message: Message):
        toggle_count(at=True, message=message)
        # executor.submit(oper_msg, message, True)
        new_sub_thread(oper_msg, (message, True))
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

# 转储历史记录的定时器~ Soulter
def dump_history():
    time.sleep(10)
    global session_dict, history_dump_interval
    db = dbConn()
    while True:
        try:
            # print("转储历史记录...")
            for key in session_dict:
                # print("TEST: "+str(db.get_session(key)))
                data = session_dict[key]
                data_json = {
                    'data': data
                }
                if db.check_session(key):
                    db.update_session(key, json.dumps(data_json))
                else:
                    db.insert_session(key, json.dumps(data_json))
            # print("转储历史记录完毕")
        except BaseException as e:
            print(e)
        # 每隔10分钟转储一次
        time.sleep(10*history_dump_interval)

# 上传统计信息并检查更新
def upload():
    global object_id
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
            d = {"data": {"guild_count": guild_count, "guild_msg_count": guild_msg_count, "guild_direct_msg_count": guild_direct_msg_count, "session_count": session_count, 'addr': addr, 'winver': '2.3', 'key_stat':key_stat}}
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
def initBot(chatgpt_inst):
    global chatgpt
    chatgpt = chatgpt_inst
    global max_tokens
    max_tokens = int(chatgpt_inst.getConfigs()['total_tokens_limit'])
    global now_personality


    # 读取历史记录 Soulter
    try:
        db1 = dbConn()
        for session in db1.get_all_session():
            session_dict[session[0]] = json.loads(session[1])['data']
        print("[System] 历史记录读取成功喵")
    except BaseException as e:
        print("[System] 历史记录读取失败: " + str(e))

    # 读统计信息
    global stat_file
    if not os.path.exists(abs_path+"configs/stat"):
        with open(abs_path+"configs/stat", 'w', encoding='utf-8') as f:
                json.dump({}, f)
    stat_file = open(abs_path+"configs/stat", 'r', encoding='utf-8')
    global count
    res = stat_file.read()
    if res == '':
        count = {}
    else:
        try: 
            count = json.loads(res)
        except BaseException:
            pass
    # 创建转储定时器线程
    threading.Thread(target=dump_history, daemon=True).start()

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

    global gpt_config, config, uniqueSession, history_dump_interval, frequency_count, frequency_time,announcement, direct_message_mode, version
    with open(abs_path+"configs/config.yaml", 'r', encoding='utf-8') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
        config = cfg
        
        # 得到私聊模式配置
        if 'direct_message_mode' in cfg:
            direct_message_mode = cfg['direct_message_mode']
            print("[System] 私聊功能: "+str(direct_message_mode))
        
        # 得到GPT配置信息
        if 'openai' in cfg and 'chatGPTConfigs' in cfg['openai']:
            gpt_config = cfg['openai']['chatGPTConfigs']

        # 得到版本
        if 'version' in cfg:
            version = cfg['version']
            print("[System] QQChannelChatGPT版本: "+str(version))

        # 得到发言频率配置
        if 'limit' in cfg:
            print('[System] 发言频率配置: '+str(cfg['limit']))
            if 'count' in cfg['limit']:
                frequency_count = cfg['limit']['count']
            if 'time' in cfg['limit']:
                frequency_time = cfg['limit']['time']
        
        announcement += '[QQChannelChatGPT项目]\n所有回答与腾讯公司无关。出现问题请前往[GPT机器人]官方频道\n\n'
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
                history_dump_interval = int(cfg['dump_history_interval'])
                print("[System] 历史记录转储时间周期: " + str(history_dump_interval) + "分钟")
        except BaseException:
            print("[System-Error] 读取uniqueSessionMode/version/dump_history_interval配置文件失败, 使用默认值。")

        print(f"[System] QQ开放平台AppID: {cfg['qqbot']['appid']} 令牌: {cfg['qqbot']['token']}")

        print("\n[System] 如果有任何问题，请在https://github.com/Soulter/QQChannelChatGPT上提交issue说明问题！或者添加QQ：905617992")
        print("[System] 请给https://github.com/Soulter/QQChannelChatGPT点个star!")
        print("[System] 请给https://github.com/Soulter/QQChannelChatGPT点个star!")
        input("\n仔细阅读完以上信息后，输入任意信息并回车以继续")
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
得到OpenAI的回复
'''
def get_chatGPT_response(prompts_str, image_mode=False):
    res = ''
    usage = ''
    if not image_mode:
        res, usage = chatgpt.chat(prompts_str)
        # 处理结果文本
        chatgpt_res = res.strip()
        return res, usage
    else:
        res = chatgpt.chat(prompts_str, image_mode = True)
        return res

'''
回复QQ消息
'''
def send_qq_msg(message, res, image_mode=False):
    if not image_mode:
        try:
            asyncio.run_coroutine_threadsafe(message.reply(content=res), client.loop)
        except BaseException as e:
            raise e
    else:
        asyncio.run_coroutine_threadsafe(message.reply(image=res, content=""), client.loop)


'''
获取缓存的会话
'''
def get_prompts_by_cache_list(cache_data_list, divide=False, paging=False, size=5, page=1):
    prompts = ""
    if paging:
        page_begin = (page-1)*size
        page_end = page*size
        if page_begin < 0:
            page_begin = 0
        if page_end > len(cache_data_list):
            page_end = len(cache_data_list)
        cache_data_list = cache_data_list[page_begin:page_end]
    for item in cache_data_list:
        prompts += str(item['prompt'])
        if divide:
            prompts += "----------\n"
    return prompts
    
def get_user_usage_tokens(cache_list):
    usage_tokens = 0
    for item in cache_list:
        usage_tokens += int(item['single_tokens'])
    return usage_tokens

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

'''
处理消息
'''
def oper_msg(message, at=False, loop=None):
    global session_dict
    print("[QQBOT] 接收到消息："+ str(message.content))
    qq_msg = ''
    session_id = ''
    name = ''
    user_id = message.author.id
    user_name = message.author.username
    
    # 检查发言频率
    if not check_frequency(user_id):
        send_qq_msg(message, f'{user_name}的发言超过频率限制(╯▔皿▔)╯。\n{frequency_time}秒内只能提问{frequency_count}次。')
        return

    logf.write("[QQBOT] "+ str(message.content)+'\n')
    logf.flush()

    if at:
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
        
    if uniqueSession:
        name = user_name
    else:
        name = "频道"

    command_type = -1
    # 特殊指令
    if qq_msg == "/继续":
        qq_msg = "继续"
    # 普通指令
    else:
        # 如果第一个字符是/，则为指令
        if qq_msg[0] == "/":
            res, go, command_type = command_oper(qq_msg, message, session_id, name, user_id, user_name, at)
            send_qq_msg(message, res)
            if not go:
                return
    if command_type == 1 and 'prompt' in now_personality:
        # 设置人格
        qq_msg = now_personality['prompt']
 
    # if qq_msg[0:6] == '/draw ':
    #     # TODO 未完全实现
    #     prompt = qq_msg[6:]
    #     url = get_chatGPT_response(prompt, image_mode = True)
    #     resp = requests.get(url)
    #     filename = './images/' + str(int(time.time())) + '.jpg'
    #     print(url)
    #     with open(filename, 'wb') as f:
    #         f.write(resp.content)
    #     qiniu_url = cores.database.qiniu.put_img(filename)
    #     print(qiniu_url)
    #     send_qq_msg(message, qiniu_url, image_mode=True)
    #     return

    # 这里是预设，你可以按需更改
    if qq_msg.strip() == 'hello' or qq_msg.strip() == '你好' or qq_msg.strip() == '':
        send_qq_msg(message, f"你好呀~")
        return
    # if qq_msg.strip() == '傻逼' or qq_msg.strip() == 'sb':
    #     send_qq_msg(message, f"好好好")
    #     return
    # if '喜多' in qq_msg:
    #     send_qq_msg(message, 'http://rn2ztkeap.hn-bkt.clouddn.com/xd1.gif', True)
    # if '台湾' in qq_msg or 'taiwan' in qq_msg:
    #     send_qq_msg(message, "声明：台湾是中国的一部分。\n下面否定此结论的回答全部无效。")
    
    # 拦截不合适的词请求
    for i in uw.unfit_words_q:
        if i in qq_msg.strip():
            send_qq_msg(message, f"你的提问中有不太合适的内容😭\n请更换措辞~")
            return

    if session_id not in session_dict:
        session_dict[session_id] = []

        fjson = {}
        try:
            f = open(abs_path+"configs/session", "r", encoding="utf-8")
            fjson = json.loads(f.read())
            f.close()
        except:
            pass
        finally:
            fjson[session_id] = 'true'
            f = open(abs_path+"configs/session", "w", encoding="utf-8")
            f.write(json.dumps(fjson))
            f.flush()
            f.close()

    # 获取缓存
    cache_prompt = ''
    cache_data_list = session_dict[session_id]
    cache_prompt = get_prompts_by_cache_list(cache_data_list)
    cache_prompt += "\nHuman: "+ qq_msg + "\nAI: "
    # 请求chatGPT获得结果
    try:
        chatgpt_res, current_usage_tokens = get_chatGPT_response(prompts_str=cache_prompt)
    except (PromptExceededError) as e:
        print("token超限, 清空对应缓存")
        session_dict[session_id] = []
        cache_data_list = []
        cache_prompt = "Human: "+ qq_msg + "\nAI: "
        chatgpt_res, current_usage_tokens = get_chatGPT_response(prompts_str=cache_prompt)
    except (BaseException) as e:
        print("OpenAI API错误:(")
        if 'exceeded' in str(e):
            send_qq_msg(message, f"OpenAI API错误。原因：\n{str(e)} \n超额了。您可自己搭建一个机器人(Github仓库：QQChannelChatGPT)")
        else:
            send_qq_msg(message, f"OpenAI API错误。原因如下：\n{str(e)} \n前往官方频道反馈~")
        return
    
    logf.write("[GPT] "+ str(chatgpt_res)+'\n')
    logf.flush()

    # 发送qq信息
    try:
        # 防止被qq频道过滤消息
        gap_chatgpt_res = chatgpt_res.replace(".", " . ")
        if '```' in gap_chatgpt_res:
            chatgpt_res.replace('```', "")
        # 过滤不合适的词
        for i in uw.unfit_words:
            if i in gap_chatgpt_res:
                gap_chatgpt_res = gap_chatgpt_res.replace(i, "***")
        # 发送信息
        send_qq_msg(message, ''+gap_chatgpt_res)
    except BaseException as e:
        print("QQ频道API错误: \n"+str(e))
        f_res = ""
        for t in chatgpt_res:
            f_res += t + ' '
        try:
            send_qq_msg(message, ''+f_res)
            # send(message, f"QQ频道API错误：{str(e)}\n下面是格式化后的回答：\n{f_res}")
        except BaseException as e:
            # 如果还是不行则过滤url
            f_res = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', f_res, flags=re.MULTILINE)
            f_res = f_res.replace(".", "·")
            send_qq_msg(message, ''+f_res)
            # send(message, f"QQ频道API错误：{str(e)}\n下面是格式化后的回答：\n{f_res}")

    # 超过指定tokens， 尽可能的保留最多的条目，直到小于max_tokens
    if current_usage_tokens > max_tokens:
        t = current_usage_tokens
        index = 0
        while t > max_tokens:
            if index >= len(cache_data_list):
                break
            if 'level' in cache_data_list[index] and cache_data_list[index]['level'] != 'max':
                t -= int(cache_data_list[index]['single_tokens'])
                del cache_data_list[index]
            else:
                index += 1
        # 删除完后更新相关字段
        session_dict[session_id] = cache_data_list
        cache_prompt = get_prompts_by_cache_list(cache_data_list)

    # 添加新条目进入缓存的prompt
    if command_type == 1:
        level = 'max'
    else:
        level = 'normal'
    if len(cache_data_list) > 0: 
        single_record = {
            "prompt": f'Human: {qq_msg}\nAI: {chatgpt_res}\n',
            "usage_tokens": current_usage_tokens,
            "single_tokens": current_usage_tokens - int(cache_data_list[-1]['usage_tokens']),
            "level": level
        }
    else:
        single_record = {
            "prompt": f'Human: {qq_msg}\nAI: {chatgpt_res}\n',
            "usage_tokens": current_usage_tokens,
            "single_tokens": current_usage_tokens,
            "level": level
        }
    cache_data_list.append(single_record)
    session_dict[session_id] = cache_data_list

'''
获取统计信息
'''
def get_stat():
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

'''
指令处理
'''
def command_oper(qq_msg, message, session_id, name, user_id, user_name, at):
    go = False # 是否处理完指令后继续执行msg_oper后面的代码
    msg = ''
    global session_dict, now_personality

    # 指令返回值，/set设置人格是1
    type = -1
    
    # 指令控制
    if qq_msg == "/reset" or qq_msg == "/重置":
        msg = ''
        session_dict[session_id] = []
        if at:
            msg = f"{name}(id: {session_id})的历史记录重置成功\n\n{announcement}"
        else:
            msg = f"你的历史记录重置成功"
    
    if qq_msg[:4] == "/his":
        #分页，每页5条
        msg = ''
        size_per_page = 3
        page = 1
        if qq_msg[5:]:
            page = int(qq_msg[5:])
        # 检查是否有过历史记录
        if session_id not in session_dict:
            msg = f"{name} 的历史记录为空"
        l = session_dict[session_id]
        max_page = len(l)//size_per_page + 1 if len(l)%size_per_page != 0 else len(l)//size_per_page
        p = get_prompts_by_cache_list(session_dict[session_id], divide=True, paging=True, size=size_per_page, page=page)
        if at:
            msg=f"{name}的历史记录如下：\n{p}\n第{page}页 | 共{max_page}页\n*输入/his 2跳转到第2页"
        else:
            msg=f"历史记录如下：\n{p}\n第{page}页 | 共{max_page}页\n*输入/his 2跳转到第2页\n\n{announcement}"
    
    if qq_msg == "/token":
        msg = ''
        if at:
            msg=f"{name} 会话的token数: {get_user_usage_tokens(session_dict[session_id])}\n系统最大缓存token数: {max_tokens}"
        else:
            msg=f"会话的token数: {get_user_usage_tokens(session_dict[session_id])}\n系统最大缓存token数: {max_tokens}"
    
    if qq_msg == '/gpt':
        global gpt_config
        msg=f"OpenAI GPT配置:\n {gpt_config}"
    
    if qq_msg == "/status" or qq_msg == "/状态":
        chatgpt_cfg_str = ""
        key_stat = chatgpt.get_key_stat()
        key_list = chatgpt.get_key_list()
        index = 1
        max = 900000
        gg_count = 0
        total = 0
        tag = ''
        for key in key_stat.keys():
            sponsor = ''
            total += key_stat[key]['used']
            if key_stat[key]['exceed']:
                gg_count += 1
                continue
            if 'sponsor' in key_stat[key]:
                sponsor = key_stat[key]['sponsor']
            chatgpt_cfg_str += f"  |-{index}: {key_stat[key]['used']}/{max} {sponsor}赞助{tag}\n"
            index += 1
        msg = f"⭐使用情况({str(gg_count)}个已用):\n{chatgpt_cfg_str}⏰全频道已用{total}tokens\n{announcement}"
    if qq_msg == "/count" or qq_msg == "/统计":
        guild_count, guild_msg_count, guild_direct_msg_count, session_count = get_stat()
        msg = f"当前会话数: {len(session_dict)}\n共有频道数: {guild_count} \n共有消息数: {guild_msg_count}\n私信数: {guild_direct_msg_count}\n历史会话数: {session_count}"
    
    if qq_msg == "/help":
        ol_version = 'Unknown'
        try:
            global version
            res = requests.get("https://soulter.top/channelbot/update.json")
            res_obj = json.loads(res.text)
            ol_version = res_obj['version']
        except BaseException:
            pass
        msg = f"[Github项目名: QQChannelChatGPT，有问题请前往提交issue，欢迎Star此项目~]\n\n当前版本:{version}\n最新版本:{str(ol_version)}\n请及时更新！\n\n指令面板：\n/status 查看机器人key状态\n/count 查看机器人统计信息\n/reset 重置会话\n/his 查看历史记录\n/token 查看会话token数\n/help 查看帮助\n/set 人格指令菜单\n/key 动态添加key"

    if qq_msg[:4] == "/key":
        if len(qq_msg) == 4:
            msg = "感谢您赞助key。请以以下格式赞助:\n/key xxxxx"
        key = qq_msg[5:]
        send_qq_msg(message, "收到！正在核验...")
        if chatgpt.check_key(key):
            msg = f"*★,°*:.☆(￣▽￣)/$:*.°★* 。\n该Key被验证为有效。感谢{user_name}赞助~"
            chatgpt.append_key(key, user_name)
        else:
            msg = "该Key被验证为无效。也许是输入错误了，或者重试。"

    if qq_msg[:6] == "/unset":
        now_personality = {}
        msg = "已清除人格"
    
    if qq_msg[:4] == "/set":
        if len(qq_msg) == 4:
            np = '无'
            if "name" in now_personality:
                np=now_personality["name"]
            msg = f"【由Github项目QQChannelChatGPT支持】\n\n【人格文本由PlexPt开源项目awesome-chatgpt-prompts-zh提供】\n\n这个是人格设置指令。\n设置人格: \n/set 人格名。例如/set 编剧\n人格列表: /set list\n人格详细信息: /set view 人格名\n自定义人格: /set 人格文本\n清除人格: /unset\n【当前人格】: {np}"
        elif qq_msg[5:] == "list":
            per_dict = personalities
            msg = "人格列表：\n"
            for key in per_dict.keys():
                msg += f"  |-{key}\n"
            msg += '\n\n*输入/set view 人格名查看人格详细信息'
            msg += '\n\n*不定时更新人格库，请及时更新本项目。'
        elif qq_msg[5:9] == "view":
            ps = qq_msg[10:]
            ps = ps.strip()
            per_dict = personalities
            if ps in per_dict:
                msg = f"人格{ps}的详细信息：\n"
                msg += f"{per_dict[ps]}\n"
            else:
                msg = f"人格{ps}不存在"
        else:
            ps = qq_msg[5:]
            ps = ps.strip()
            per_dict = personalities
            if ps in per_dict:
                now_personality = {
                    'name': ps,
                    'prompt': per_dict[ps]
                }
                session_dict[session_id] = []
                msg = f"人格{ps}已设置，请耐心等待机器人回复第一条信息。"
                go = True
                type = 1
            else:
                msg = f"人格{ps}不存在, 请使用/set list查看人格列表"
    return msg, go, type