"""
如需修改配置，请在 `data/cmd_config.json` 中修改或者在管理面板中可视化修改。
"""

VERSION = "3.4.39"
DB_PATH = "data/data_v3.db"

# 默认配置
DEFAULT_CONFIG = {
    "config_version": 2,
    "platform_settings": {
        "unique_session": False,
        "rate_limit": {
            "time": 60,
            "count": 30,
            "strategy": "stall",  # stall, discard
        },
        "reply_prefix": "",
        "forward_threshold": 1500,
        "enable_id_white_list": True,
        "id_whitelist": [],
        "id_whitelist_log": True,
        "wl_ignore_admin_on_group": True,
        "wl_ignore_admin_on_friend": True,
        "reply_with_mention": False,
        "reply_with_quote": False,
        "path_mapping": [],
        "segmented_reply": {
            "enable": False,
            "only_llm_result": True,
            "interval_method": "random",
            "interval": "1.5,3.5",
            "log_base": 2.6,
            "words_count_threshold": 150,
            "regex": ".*?[。？！~…]+|.+$",
            "content_cleanup_rule": "",
        },
        "no_permission_reply": True,
        "empty_mention_waiting": True,
        "friend_message_needs_wake_prefix": False,
    },
    "provider": [],
    "provider_settings": {
        "enable": True,
        "wake_prefix": "",
        "web_search": False,
        "web_search_link": False,
        "identifier": False,
        "datetime_system_prompt": True,
        "default_personality": "default",
        "prompt_prefix": "",
    },
    "provider_stt_settings": {
        "enable": False,
        "provider_id": "",
    },
    "provider_tts_settings": {
        "enable": False,
        "provider_id": "",
    },
    "provider_ltm_settings": {
        "group_icl_enable": False,
        "group_message_max_cnt": 300,
        "image_caption": False,
        "image_caption_provider_id": "",
        "image_caption_prompt": "Please describe the image using Chinese.",
        "active_reply": {
            "enable": False,
            "method": "possibility_reply",
            "possibility_reply": 0.1,
            "prompt": "",
            "whitelist": [],
        },
    },
    "content_safety": {
        "also_use_in_response": False,
        "internal_keywords": {"enable": True, "extra_keywords": []},
        "baidu_aip": {"enable": False, "app_id": "", "api_key": "", "secret_key": ""},
    },
    "admins_id": ["astrbot"],
    "t2i": False,
    "t2i_word_threshold": 150,
    "http_proxy": "",
    "dashboard": {
        "enable": True,
        "username": "astrbot",
        "password": "77b90590a8945a7d36c963981a307dc9",
        "host": "0.0.0.0",
        "port": 6185,
    },
    "platform": [],
    "wake_prefix": ["/"],
    "log_level": "INFO",
    "t2i_endpoint": "",
    "pip_install_arg": "",
    "plugin_repo_mirror": "",
    "knowledge_db": {},
    "persona": [],
}


# 配置项的中文描述、值类型
CONFIG_METADATA_2 = {
    "platform_group": {
        "name": "消息平台",
        "metadata": {
            "platform": {
                "description": "消息平台适配器",
                "type": "list",
                "config_template": {
                    "qq_official(QQ)": {
                        "id": "default",
                        "type": "qq_official",
                        "enable": False,
                        "appid": "",
                        "secret": "",
                        "enable_group_c2c": True,
                        "enable_guild_direct_message": True,
                    },
                    "qq_official_webhook(QQ)": {
                        "id": "default",
                        "type": "qq_official_webhook",
                        "enable": False,
                        "appid": "",
                        "secret": "",
                        "callback_server_host": "0.0.0.0",
                        "port": 6196,
                    },
                    "aiocqhttp(OneBotv11)": {
                        "id": "default",
                        "type": "aiocqhttp",
                        "enable": False,
                        "ws_reverse_host": "0.0.0.0",
                        "ws_reverse_port": 6199,
                    },
                    "gewechat(微信)": {
                        "id": "gwchat",
                        "type": "gewechat",
                        "enable": False,
                        "base_url": "http://localhost:2531",
                        "nickname": "soulter",
                        "host": "这里填写你的局域网IP或者公网服务器IP",
                        "port": 11451,
                    },
                    "wecom(企业微信)": {
                        "id": "wecom",
                        "type": "wecom",
                        "enable": False,
                        "corpid": "",
                        "secret": "",
                        "token": "",
                        "encoding_aes_key": "",
                        "api_base_url": "https://qyapi.weixin.qq.com/cgi-bin/",
                        "callback_server_host": "0.0.0.0",
                        "port": 6195,
                    },
                    "lark(飞书)": {
                        "id": "lark",
                        "type": "lark",
                        "enable": False,
                        "lark_bot_name": "",
                        "app_id": "",
                        "app_secret": "",
                        "domain": "https://open.feishu.cn",
                    },
                    "dingtalk(钉钉)": {
                        "id": "dingtalk",
                        "type": "dingtalk",
                        "enable": False,
                        "client_id": "",
                        "client_secret": "",
                    },
                    "telegram": {
                        "id": "telegram",
                        "type": "telegram",
                        "enable": False,
                        "telegram_token": "your_bot_token",
                        "start_message": "Hello, I'm AstrBot!",
                        "telegram_api_base_url": "https://api.telegram.org/bot",
                        "telegram_file_base_url": "https://api.telegram.org/file/bot",
                    },
                },
                "items": {
                    "telegram_token": {
                        "description": "Bot Token",
                        "type": "string",
                        "hint": "如果你的网络环境为中国大陆，请在 `其他配置` 处设置代理或更改 api_base。",
                    },
                    "id": {
                        "description": "ID",
                        "type": "string",
                        "obvious_hint": True,
                        "hint": "ID 不能和其它的平台适配器重复，否则将发生严重冲突。",
                    },
                    "type": {
                        "description": "适配器类型",
                        "type": "string",
                        "invisible": True,
                    },
                    "enable": {
                        "description": "启用",
                        "type": "bool",
                        "hint": "是否启用该适配器。未启用的适配器对应的消息平台将不会接收到消息。",
                    },
                    "appid": {
                        "description": "appid",
                        "type": "string",
                        "hint": "必填项。QQ 官方机器人平台的 appid。如何获取请参考文档。",
                    },
                    "secret": {
                        "description": "secret",
                        "type": "string",
                        "hint": "必填项。QQ 官方机器人平台的 secret。如何获取请参考文档。",
                    },
                    "enable_group_c2c": {
                        "description": "启用消息列表单聊",
                        "type": "bool",
                        "hint": "启用后，机器人可以接收到 QQ 消息列表中的私聊消息。你可能需要在 QQ 机器人平台上通过扫描二维码的方式添加机器人为你的好友。详见文档。",
                    },
                    "enable_guild_direct_message": {
                        "description": "启用频道私聊",
                        "type": "bool",
                        "hint": "启用后，机器人可以接收到频道的私聊消息。",
                    },
                    "ws_reverse_host": {
                        "description": "反向 Websocket 主机地址(AstrBot 为服务器端)",
                        "type": "string",
                        "hint": "aiocqhttp 适配器的反向 Websocket 服务器 IP 地址，不包含端口号。",
                    },
                    "ws_reverse_port": {
                        "description": "反向 Websocket 端口",
                        "type": "int",
                        "hint": "aiocqhttp 适配器的反向 Websocket 端口。",
                    },
                    "lark_bot_name": {
                        "description": "飞书机器人的名字",
                        "type": "string",
                        "hint": "请务必填对，否则 @ 机器人将无法唤醒，只能通过前缀唤醒。",
                        "obvious_hint": True,
                    },
                },
            },
            "platform_settings": {
                "description": "平台设置",
                "type": "object",
                "items": {
                    "unique_session": {
                        "description": "会话隔离",
                        "type": "bool",
                        "hint": "启用后，在群组或者频道中，每个人的消息上下文都是独立的。",
                    },
                    "rate_limit": {
                        "description": "速率限制",
                        "hint": "每个会话在 `time` 秒内最多只能发送 `count` 条消息。",
                        "type": "object",
                        "items": {
                            "time": {"description": "消息速率限制时间", "type": "int"},
                            "count": {"description": "消息速率限制计数", "type": "int"},
                            "strategy": {
                                "description": "速率限制策略",
                                "type": "string",
                                "options": ["stall", "discard"],
                                "hint": "当消息速率超过限制时的处理策略。stall 为等待，discard 为丢弃。",
                            },
                        },
                    },
                    "no_permission_reply": {
                        "description": "无权限回复",
                        "type": "bool",
                        "hint": "启用后，当用户没有权限执行某个操作时，机器人会回复一条消息。",
                    },
                    "empty_mention_waiting": {
                        "description": "只 @ 机器人是否触发等待回复",
                        "type": "bool",
                        "hint": "启用后，当消息内容只有 @ 机器人时，会触发等待回复，在 60 秒内的该用户的任意一条消息均会唤醒机器人。这在某些平台不支持 @ 和语音/图片等消息同时发送时特别有用。",
                    },
                    "friend_message_needs_wake_prefix": {
                        "description": "私聊消息是否需要唤醒前缀",
                        "type": "bool",
                        "hint": "启用后，私聊消息需要唤醒前缀才会被处理，同群聊一样。",
                    },
                    "segmented_reply": {
                        "description": "分段回复",
                        "type": "object",
                        "items": {
                            "enable": {
                                "description": "启用分段回复",
                                "type": "bool",
                            },
                            "only_llm_result": {
                                "description": "仅对 LLM 结果分段",
                                "type": "bool",
                            },
                            "interval_method": {
                                "description": "间隔时间计算方法",
                                "type": "string",
                                "options": ["random", "log"],
                                "hint": "分段回复的间隔时间计算方法。random 为随机时间，log 为根据消息长度计算，$y=log_<log_base>(x)$，x为字数，y的单位为秒。",
                            },
                            "interval": {
                                "description": "随机间隔时间(秒)",
                                "type": "string",
                                "hint": "`random` 方法用。每一段回复的间隔时间，格式为 `最小时间,最大时间`。如 `0.75,2.5`",
                            },
                            "log_base": {
                                "description": "对数函数底数",
                                "type": "float",
                                "hint": "`log` 方法用。对数函数的底数。默认为 2.6",
                            },
                            "words_count_threshold": {
                                "description": "字数阈值",
                                "type": "int",
                                "hint": "超过这个字数的消息不会被分段回复。默认为 150",
                            },
                            "regex": {
                                "description": "正则表达式",
                                "type": "string",
                                "obvious_hint": True,
                                "hint": "用于分隔一段消息。默认情况下会根据句号、问号等标点符号分隔。re.findall(r'<regex>', text)",
                            },
                            "content_cleanup_rule": {
                                "description": "过滤分段后的内容",
                                "type": "string",
                                "obvious_hint": True,
                                "hint": "移除分段后的内容中的指定的内容。支持正则表达式。如填写 `[。？！]` 将移除所有的句号、问号、感叹号。re.sub(r'<regex>', '', text)",
                            },
                        },
                    },
                    "reply_prefix": {
                        "description": "回复前缀",
                        "type": "string",
                        "hint": "机器人回复消息时带有的前缀。",
                    },
                    "forward_threshold": {
                        "description": "转发消息的字数阈值",
                        "type": "int",
                        "hint": "超过一定字数后，机器人会将消息折叠成 QQ 群聊的 “转发消息”，以防止刷屏。目前仅 QQ 平台适配器适用。",
                    },
                    "enable_id_white_list": {
                        "description": "启用 ID 白名单",
                        "type": "bool",
                    },
                    "id_whitelist": {
                        "description": "ID 白名单",
                        "type": "list",
                        "items": {"type": "string"},
                        "obvious_hint": True,
                        "hint": "只处理所填写的 ID 发来的消息事件。为空时不启用白名单过滤。可以使用 /sid 指令获取在某个平台上的会话 ID。会话 ID 类似 aiocqhttp:GroupMessage:547540978。管理员可使用 /wl 添加白名单",
                    },
                    "id_whitelist_log": {
                        "description": "打印白名单日志",
                        "type": "bool",
                        "hint": "启用后，当一条消息没通过白名单时，会输出 INFO 级别的日志。",
                    },
                    "wl_ignore_admin_on_group": {
                        "description": "管理员群组消息无视 ID 白名单",
                        "type": "bool",
                    },
                    "wl_ignore_admin_on_friend": {
                        "description": "管理员私聊消息无视 ID 白名单",
                        "type": "bool",
                    },
                    "reply_with_mention": {
                        "description": "回复时 @ 发送者",
                        "type": "bool",
                        "hint": "启用后，机器人回复消息时会 @ 发送者。实际效果以具体的平台适配器为准。",
                    },
                    "reply_with_quote": {
                        "description": "回复时引用消息",
                        "type": "bool",
                        "hint": "启用后，机器人回复消息时会引用原消息。实际效果以具体的平台适配器为准。",
                    },
                    "path_mapping": {
                        "description": "路径映射",
                        "type": "list",
                        "items": {"type": "string"},
                        "obvious_hint": True,
                        "hint": "此功能解决由于文件系统不一致导致路径不存在的问题。格式为 <原路径>:<映射路径>。如 `/app/.config/QQ:/var/lib/docker/volumes/xxxx/_data`。这样，当消息平台下发的事件中图片和语音路径以 `/app/.config/QQ` 开头时，开头被替换为 `/var/lib/docker/volumes/xxxx/_data`。这在 AstrBot 或者平台协议端使用 Docker 部署时特别有用。",
                    },
                },
            },
            "content_safety": {
                "description": "内容安全",
                "type": "object",
                "items": {
                    "also_use_in_response": {
                        "description": "对大模型响应安全审核",
                        "type": "bool",
                        "hint": "启用后，大模型的响应也会通过内容安全审核。",
                    },
                    "baidu_aip": {
                        "description": "百度内容审核配置",
                        "type": "object",
                        "items": {
                            "enable": {
                                "description": "启用百度内容审核",
                                "type": "bool",
                                "hint": "启用此功能前，您需要手动在设备中安装 baidu-aip 库。一般来说，安装指令如下: `pip3 install baidu-aip`",
                            },
                            "app_id": {"description": "APP ID", "type": "string"},
                            "api_key": {"description": "API Key", "type": "string"},
                            "secret_key": {
                                "description": "Secret Key",
                                "type": "string",
                            },
                        },
                    },
                    "internal_keywords": {
                        "description": "内部关键词过滤",
                        "type": "object",
                        "items": {
                            "enable": {
                                "description": "启用内部关键词过滤",
                                "type": "bool",
                            },
                            "extra_keywords": {
                                "description": "额外关键词",
                                "type": "list",
                                "items": {"type": "string"},
                                "hint": "额外的屏蔽关键词列表，支持正则表达式。",
                            },
                        },
                    },
                },
            },
        },
    },
    "provider_group": {
        "name": "服务提供商",
        "metadata": {
            "provider": {
                "description": "服务提供商配置",
                "type": "list",
                "config_template": {
                    "OpenAI": {
                        "id": "openai",
                        "type": "openai_chat_completion",
                        "enable": True,
                        "key": [],
                        "api_base": "https://api.openai.com/v1",
                        "timeout": 120,
                        "model_config": {
                            "model": "gpt-4o-mini",
                        },
                    },
                    "Azure_OpenAI": {
                        "id": "azure",
                        "type": "openai_chat_completion",
                        "enable": True,
                        "api_version": "2024-05-01-preview",
                        "key": [],
                        "api_base": "",
                        "timeout": 120,
                        "model_config": {
                            "model": "gpt-4o-mini",
                        },
                    },
                    "xAI(grok)": {
                        "id": "xai",
                        "type": "openai_chat_completion",
                        "enable": True,
                        "key": [],
                        "api_base": "https://api.x.ai/v1",
                        "timeout": 120,
                        "model_config": {
                            "model": "grok-2-latest",
                        },
                    },
                    "Anthropic(claude)": {
                        "id": "claude",
                        "type": "anthropic_chat_completion",
                        "enable": True,
                        "key": [],
                        "api_base": "https://api.anthropic.com/v1",
                        "timeout": 120,
                        "model_config": {
                            "model": "claude-3-5-sonnet-latest",
                            "max_tokens": 4096,
                        },
                    },
                    "Ollama": {
                        "id": "ollama_default",
                        "type": "openai_chat_completion",
                        "enable": True,
                        "key": ["ollama"],  # ollama 的 key 默认是 ollama
                        "api_base": "http://localhost:11434/v1",
                        "model_config": {
                            "model": "llama3.1-8b",
                        },
                    },
                    "LM_Studio": {
                        "id": "lm_studio",
                        "type": "openai_chat_completion",
                        "enable": True,
                        "key": ["lmstudio"],
                        "api_base": "http://localhost:1234/v1",
                        "model_config": {
                            "model": "llama-3.1-8b",
                        },
                    },
                    "Gemini(OpenAI兼容)": {
                        "id": "gemini_default",
                        "type": "openai_chat_completion",
                        "enable": True,
                        "key": [],
                        "api_base": "https://generativelanguage.googleapis.com/v1beta/openai/",
                        "timeout": 120,
                        "model_config": {
                            "model": "gemini-1.5-flash",
                        },
                    },
                    "Gemini(googlegenai原生)": {
                        "id": "gemini_default",
                        "type": "googlegenai_chat_completion",
                        "enable": True,
                        "key": [],
                        "api_base": "https://generativelanguage.googleapis.com/",
                        "timeout": 120,
                        "model_config": {
                            "model": "gemini-1.5-flash",
                        },
                    },
                    "DeepSeek": {
                        "id": "deepseek_default",
                        "type": "openai_chat_completion",
                        "enable": True,
                        "key": [],
                        "api_base": "https://api.deepseek.com/v1",
                        "timeout": 120,
                        "model_config": {
                            "model": "deepseek-chat",
                        },
                    },
                    "Zhipu(智谱)": {
                        "id": "zhipu_default",
                        "type": "zhipu_chat_completion",
                        "enable": True,
                        "key": [],
                        "timeout": 120,
                        "api_base": "https://open.bigmodel.cn/api/paas/v4/",
                        "model_config": {
                            "model": "glm-4-flash",
                        },
                    },
                    "SiliconFlow(硅基流动)": {
                        "id": "siliconflow",
                        "type": "openai_chat_completion",
                        "enable": True,
                        "key": [],
                        "timeout": 120,
                        "api_base": "https://api.siliconflow.cn/v1",
                        "model_config": {
                            "model": "deepseek-ai/DeepSeek-V3",
                        },
                    },
                    "MoonShot(Kimi)": {
                        "id": "moonshot",
                        "type": "openai_chat_completion",
                        "enable": True,
                        "key": [],
                        "timeout": 120,
                        "api_base": "https://api.moonshot.cn/v1",
                        "model_config": {
                            "model": "moonshot-v1-8k",
                        },
                    },
                    "LLMTuner": {
                        "id": "llmtuner_default",
                        "type": "llm_tuner",
                        "enable": True,
                        "base_model_path": "",
                        "adapter_model_path": "",
                        "llmtuner_template": "",
                        "finetuning_type": "lora",
                        "quantization_bit": 4,
                    },
                    "Dify": {
                        "id": "dify_app_default",
                        "type": "dify",
                        "enable": True,
                        "dify_api_type": "chat",
                        "dify_api_key": "",
                        "dify_api_base": "https://api.dify.ai/v1",
                        "dify_workflow_output_key": "astrbot_wf_output",
                        "dify_query_input_key": "astrbot_text_query",
                        "variables": {},
                        "timeout": 60,
                    },
                    "Dashscope(阿里云百炼应用)": {
                        "id": "dashscope",
                        "type": "dashscope",
                        "enable": True,
                        "dashscope_app_type": "agent",
                        "dashscope_api_key": "",
                        "dashscope_app_id": "",
                        "rag_options": {
                            "pipeline_ids": [],
                            "file_ids": [],
                            "output_reference": False,
                        },
                        "variables": {},
                        "timeout": 60,
                    },
                    "FastGPT": {
                        "id": "fastgpt",
                        "type": "openai_chat_completion",
                        "enable": True,
                        "key": [],
                        "api_base": "https://api.fastgpt.in/api/v1",
                        "timeout": 60,
                    },
                    "Whisper(API)": {
                        "id": "whisper",
                        "type": "openai_whisper_api",
                        "enable": False,
                        "api_key": "",
                        "api_base": "",
                        "model": "whisper-1",
                    },
                    "Whisper(本地加载)": {
                        "whisper_hint": "(不用修改我)",
                        "enable": False,
                        "id": "whisper",
                        "type": "openai_whisper_selfhost",
                        "model": "tiny",
                    },
                    "sensevoice(本地加载)": {
                        "sensevoice_hint": "(不用修改我)",
                        "enable": False,
                        "id": "sensevoice",
                        "type": "sensevoice_stt_selfhost",
                        "stt_model": "iic/SenseVoiceSmall",
                        "is_emotion": False,
                    },
                    "OpenAI_TTS(API)": {
                        "id": "openai_tts",
                        "type": "openai_tts_api",
                        "enable": False,
                        "api_key": "",
                        "api_base": "",
                        "model": "tts-1",
                        "openai-tts-voice": "alloy",
                        "timeout": "20",
                    },
                    "Edge_TTS": {
                        "edgetts_hint": "提示：使用这个服务前需要安装有 ffmpeg，并且可以直接在终端调用 ffmpeg 指令。",
                        "id": "edge_tts",
                        "type": "edge_tts",
                        "enable": False,
                        "edge-tts-voice": "zh-CN-XiaoxiaoNeural",
                        "timeout": 20,
                    },
                    "GSVI_TTS(API)": {
                        "id": "gsvi_tts",
                        "type": "gsvi_tts_api",
                        "api_base": "http://127.0.0.1:5000",
                        "character": "",
                        "emotion": "default",
                        "enable": False,
                        "timeout": 20,
                    },
                    "FishAudio_TTS(API)": {
                        "id": "fishaudio_tts",
                        "type": "fishaudio_tts_api",
                        "enable": False,
                        "api_key": "",
                        "api_base": "https://api.fish.audio/v1",
                        "fishaudio-tts-character": "可莉",
                        "timeout": "20",
                    },
                },
                "items": {
                    "rag_options": {
                        "description": "RAG 选项",
                        "type": "object",
                        "hint": "检索知识库设置, 非必填。仅 Agent 应用类型支持(智能体应用, 包括 RAG 应用)",
                        "items": {
                            "pipeline_ids": {
                                "description": "知识库 ID 列表",
                                "type": "list",
                                "items": {"type": "string"},
                                "hint": "对指定知识库内所有文档进行检索, 前往 https://bailian.console.aliyun.com/ 数据应用->知识索引创建和获取 ID。",
                            },
                            "file_ids": {
                                "description": "非结构化文档 ID, 传入该参数将对指定非结构化文档进行检索。",
                                "type": "list",
                                "items": {"type": "string"},
                                "hint": "对指定非结构化文档进行检索。前往 https://bailian.console.aliyun.com/ 数据管理创建和获取 ID。",
                            },
                            "output_reference": {
                                "description": "是否输出知识库/文档的引用",
                                "type": "bool",
                                "hint": "在每次回答尾部加上引用源。默认为 False。",
                            },
                        },
                    },
                    "sensevoice_hint": {
                        "description": "部署SenseVoice",
                        "type": "string",
                        "hint": "启用前请 pip 安装 funasr、funasr_onnx、torchaudio、torch、modelscope、jieba 库（默认使用CPU，大约下载 1 GB），并且安装 ffmpeg。否则将无法正常转文字。",
                        "obvious_hint": True,
                    },
                    "is_emotion": {
                        "description": "情绪识别",
                        "type": "bool",
                        "hint": "是否开启情绪识别。happy｜sad｜angry｜neutral｜fearful｜disgusted｜surprised｜unknown",
                    },
                    "stt_model": {
                        "description": "模型名称",
                        "type": "string",
                        "hint": "modelscope 上的模型名称。默认：iic/SenseVoiceSmall。",
                    },
                    "variables": {
                        "description": "工作流固定输入变量",
                        "type": "object",
                        "obvious_hint": True,
                        "items": {},
                        "hint": "可选。工作流固定输入变量，将会作为工作流的输入。也可以在对话时使用 /set 指令动态设置变量。如果变量名冲突，优先使用动态设置的变量。",
                        "invisible": True,
                    },
                    # "fastgpt_app_type": {
                    #     "description": "应用类型",
                    #     "type": "string",
                    #     "hint": "FastGPT 应用的应用类型。",
                    #     "options": ["agent", "workflow", "plugin"],
                    #     "obvious_hint": True,
                    # },
                    "dashscope_app_type": {
                        "description": "应用类型",
                        "type": "string",
                        "hint": "百炼应用的应用类型。",
                        "options": [
                            "agent",
                            "agent-arrange",
                            "dialog-workflow",
                            "task-workflow",
                        ],
                        "obvious_hint": True,
                    },
                    "timeout": {
                        "description": "超时时间",
                        "type": "int",
                        "hint": "超时时间，单位为秒。",
                    },
                    "openai-tts-voice": {
                        "description": "voice",
                        "type": "string",
                        "obvious_hint": True,
                        "hint": "OpenAI TTS 的声音。OpenAI 默认支持：'alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'",
                    },
                    "fishaudio-tts-character": {
                        "description": "character",
                        "type": "string",
                        "obvious_hint": True,
                        "hint": "fishaudio TTS 的角色。默认为可莉。更多角色请访问：https://fish.audio/zh-CN/discovery",
                    },
                    "whisper_hint": {
                        "description": "本地部署 Whisper 模型须知",
                        "type": "string",
                        "hint": "启用前请 pip 安装 openai-whisper 库（N卡用户大约下载 2GB，主要是 torch 和 cuda，CPU 用户大约下载 1 GB），并且安装 ffmpeg。否则将无法正常转文字。",
                        "obvious_hint": True,
                    },
                    "id": {
                        "description": "ID",
                        "type": "string",
                        "obvious_hint": True,
                        "hint": "ID 不能和其它的服务提供商重复，否则将发生严重冲突。",
                    },
                    "type": {
                        "description": "模型提供商类型",
                        "type": "string",
                        "invisible": True,
                    },
                    "enable": {
                        "description": "启用",
                        "type": "bool",
                        "hint": "是否启用该模型。未启用的模型将不会被使用。",
                    },
                    "key": {
                        "description": "API Key",
                        "type": "list",
                        "items": {"type": "string"},
                        "hint": "API Key 列表。填写好后输入回车即可添加 API Key。支持多个 API Key。",
                    },
                    "api_base": {
                        "description": "API Base URL",
                        "type": "string",
                        "hint": "API Base URL 请在在模型提供商处获得。如出现 404 报错，尝试在地址末尾加上 /v1",
                        "obvious_hint": True,
                    },
                    "base_model_path": {
                        "description": "基座模型路径",
                        "type": "string",
                        "hint": "基座模型路径。",
                    },
                    "adapter_model_path": {
                        "description": "Adapter 模型路径",
                        "type": "string",
                        "hint": "Adapter 模型路径。如 Lora",
                    },
                    "llmtuner_template": {
                        "description": "template",
                        "type": "string",
                        "hint": "基座模型的类型。如 llama3, qwen, 请参考 LlamaFactory 文档。",
                    },
                    "finetuning_type": {
                        "description": "微调类型",
                        "type": "string",
                        "hint": "微调类型。如 `lora`",
                    },
                    "quantization_bit": {
                        "description": "量化位数",
                        "type": "int",
                        "hint": "量化位数。如 4",
                    },
                    "model_config": {
                        "description": "文本生成模型",
                        "type": "object",
                        "items": {
                            "model": {
                                "description": "模型名称",
                                "type": "string",
                                "hint": "大语言模型的名称，一般是小写的英文。如 gpt-4o-mini, deepseek-chat 等。",
                            },
                            "max_tokens": {
                                "description": "模型最大输出长度（tokens）",
                                "type": "int",
                            },
                            "temperature": {"description": "温度", "type": "float"},
                            "top_p": {"description": "Top P值", "type": "float"},
                        },
                        "editable": True,
                    },
                    "dify_api_key": {
                        "description": "API Key",
                        "type": "string",
                        "hint": "Dify API Key。此项必填。",
                    },
                    "dify_api_base": {
                        "description": "API Base URL",
                        "type": "string",
                        "hint": "Dify API Base URL。默认为 https://api.dify.ai/v1",
                    },
                    "dify_api_type": {
                        "description": "Dify 应用类型",
                        "type": "string",
                        "hint": "Dify API 类型。根据 Dify 官网，目前支持 chat, agent, workflow 三种应用类型",
                        "options": ["chat", "agent", "workflow"],
                    },
                    "dify_workflow_output_key": {
                        "description": "Dify Workflow 输出变量名",
                        "type": "string",
                        "hint": "Dify Workflow 输出变量名。当应用类型为 workflow 时才使用。默认为 astrbot_wf_output。",
                    },
                    "dify_query_input_key": {
                        "description": "Prompt 输入变量名",
                        "type": "string",
                        "hint": "发送的消息文本内容对应的输入变量名。默认为 astrbot_text_query。",
                        "obvious": True,
                    },
                },
            },
            "provider_settings": {
                "description": "大语言模型设置",
                "type": "object",
                "items": {
                    "enable": {
                        "description": "启用大语言模型聊天",
                        "type": "bool",
                        "hint": "如需切换大语言模型提供商，请使用 `/provider` 命令。",
                        "obvious_hint": True,
                    },
                    "wake_prefix": {
                        "description": "LLM 聊天额外唤醒前缀",
                        "type": "string",
                        "hint": "使用 LLM 聊天额外的触发条件。如填写 `chat`，则需要消息前缀加上 `/chat` 才能触发 LLM 聊天，是一个防止滥用的手段。",
                    },
                    "web_search": {
                        "description": "启用网页搜索",
                        "type": "bool",
                        "obvious_hint": True,
                        "hint": "能访问 Google 时效果最佳（国内需要在 `其他配置` 开启 HTTP 代理）。如果 Google 访问失败，程序会依次访问 Bing, Sogo 搜索引擎。",
                    },
                    "web_search_link": {
                        "description": "网页搜索引用链接",
                        "type": "bool",
                        "obvious_hint": True,
                        "hint": "开启后，将会传入网页搜索结果的链接给模型，并引导模型输出引用链接。",
                    },
                    "identifier": {
                        "description": "启动识别群员",
                        "type": "bool",
                        "obvious_hint": True,
                        "hint": "在 Prompt 前加上群成员的名字以让模型更好地了解群聊状态。启用将略微增加 token 开销。",
                    },
                    "datetime_system_prompt": {
                        "description": "启用日期时间系统提示",
                        "type": "bool",
                        "obvious_hint": True,
                        "hint": "启用后，会在系统提示词中加上当前机器的日期时间。",
                    },
                    "default_personality": {
                        "description": "默认采用的人格情景的名称",
                        "type": "string",
                        "hint": "",
                    },
                    "prompt_prefix": {
                        "description": "Prompt 前缀文本",
                        "type": "string",
                        "hint": "添加之后，会在每次对话的 Prompt 前加上此文本。",
                    },
                },
            },
            "persona": {
                "description": "人格情景设置",
                "type": "list",
                "config_template": {
                    "新人格情景": {
                        "name": "",
                        "prompt": "",
                        "begin_dialogs": [],
                        "mood_imitation_dialogs": [],
                    }
                },
                "tmpl_display_title": "name",
                "items": {
                    "name": {
                        "description": "人格名称",
                        "type": "string",
                        "hint": "人格名称，用于在多个人格中区分。使用 /persona 指令可切换人格。在 大语言模型设置 处可以设置默认人格。",
                        "obvious_hint": True,
                    },
                    "prompt": {
                        "description": "设定(系统提示词)",
                        "type": "text",
                        "hint": "填写人格的身份背景、性格特征、兴趣爱好、个人经历、口头禅等。",
                    },
                    "begin_dialogs": {
                        "description": "预设对话",
                        "type": "list",
                        "items": {"type": "string"},
                        "hint": "可选。在每个对话前会插入这些预设对话。对话需要成对(用户和助手)，输入完一个角色的内容之后按【回车】。需要偶数个对话",
                        "obvious_hint": True,
                    },
                    "mood_imitation_dialogs": {
                        "description": "对话风格模仿",
                        "type": "list",
                        "items": {"type": "string"},
                        "hint": "旨在让模型尽可能模仿学习到所填写的对话的语气风格。格式和 `预设对话` 一致。对话需要成对(用户和助手)，输入完一个角色的内容之后按【回车】。需要偶数个对话",
                        "obvious_hint": True,
                    },
                },
            },
            "provider_stt_settings": {
                "description": "语音转文本(STT)",
                "type": "object",
                "items": {
                    "enable": {
                        "description": "启用语音转文本(STT)",
                        "type": "bool",
                        "hint": "启用前请在 服务提供商配置 处创建支持 语音转文本任务 的提供商。如 whisper。",
                        "obvious_hint": True,
                    },
                    "provider_id": {
                        "description": "提供商 ID，不填则默认第一个STT提供商",
                        "type": "string",
                        "hint": "语音转文本提供商 ID。如果不填写将使用载入的第一个提供商。",
                    },
                },
            },
            "provider_tts_settings": {
                "description": "文本转语音(TTS)",
                "type": "object",
                "items": {
                    "enable": {
                        "description": "启用文本转语音(TTS)",
                        "type": "bool",
                        "hint": "启用前请在 服务提供商配置 处创建支持 语音转文本任务 的提供商。如 openai_tts。",
                        "obvious_hint": True,
                    },
                    "provider_id": {
                        "description": "提供商 ID，不填则默认第一个TTS提供商",
                        "type": "string",
                        "hint": "文本转语音提供商 ID。如果不填写将使用载入的第一个提供商。",
                    },
                },
            },
            "provider_ltm_settings": {
                "description": "聊天记忆增强(Beta)",
                "type": "object",
                "items": {
                    "group_icl_enable": {
                        "description": "群聊内记录各群员对话",
                        "type": "bool",
                        "obvious_hint": True,
                        "hint": "启用后，会记录群聊内各群员的对话。使用 /reset 命令清除记录。推荐使用 gpt-4o-mini 模型。",
                    },
                    "group_message_max_cnt": {
                        "description": "群聊消息最大数量",
                        "type": "int",
                        "obvious_hint": True,
                        "hint": "群聊消息最大数量。超过此数量后，会自动清除旧消息。",
                    },
                    "image_caption": {
                        "description": "启用图像转述(需要模型支持)",
                        "type": "bool",
                        "obvious_hint": True,
                        "hint": "启用后，当接收到图片消息时，会使用模型先将图片转述为文字再进行后续处理。推荐使用 gpt-4o-mini 模型。",
                    },
                    "image_caption_provider_id": {
                        "description": "图像转述提供商 ID",
                        "type": "string",
                        "obvious_hint": True,
                        "hint": "可选。图像转述提供商 ID。如为空将选择聊天使用的提供商。",
                    },
                    "image_caption_prompt": {
                        "description": "图像转述提示词",
                        "type": "string",
                    },
                    "active_reply": {
                        "description": "主动回复",
                        "type": "object",
                        "items": {
                            "enable": {
                                "description": "启用主动回复",
                                "type": "bool",
                                "obvious_hint": True,
                                "hint": "启用后，会根据触发概率主动回复群聊内的对话。QQ官方API(qq_official)不可用",
                            },
                            "whitelist": {
                                "description": "主动回复白名单",
                                "type": "list",
                                "items": {"type": "string"},
                                "obvious_hint": True,
                                "hint": "启用后，只有在白名单内的群聊会被主动回复。为空时不启用白名单过滤。需要通过 /sid 获取 SID 添加到这里。",
                            },
                            "method": {
                                "description": "回复方法",
                                "type": "string",
                                "options": ["possibility_reply"],
                                "hint": "回复方法。possibility_reply 为根据概率回复",
                            },
                            "possibility_reply": {
                                "description": "回复概率",
                                "type": "float",
                                "obvious_hint": True,
                                "hint": "回复概率。当回复方法为 possibility_reply 时有效。当概率 >= 1 时，每条消息都会回复。",
                            },
                            "prompt": {
                                "description": "提示词",
                                "type": "string",
                                "obvious_hint": True,
                                "hint": "提示词。当提示词为空时，如果触发回复，则向 LLM 请求的是触发的消息的内容；否则是提示词。此项可以和定时回复（暂未实现）配合使用。",
                            },
                        },
                    },
                },
            },
        },
    },
    "misc_config_group": {
        "name": "其他配置",
        "metadata": {
            "wake_prefix": {
                "description": "机器人唤醒前缀",
                "type": "list",
                "items": {"type": "string"},
                "obvious_hint": True,
                "hint": "在不 @ 机器人的情况下，可以通过外加消息前缀来唤醒机器人。更改此配置将影响整个 Bot 的功能唤醒，包括所有指令。如果您不保留 `/`，则内置指令（help等）将需要通过您的唤醒前缀来触发。",
            },
            "t2i": {
                "description": "文本转图像",
                "type": "bool",
                "hint": "启用后，超出一定长度的文本将会通过 AstrBot API 渲染成 Markdown 图片发送。可以缓解审核和消息过长刷屏的问题，并提高 Markdown 文本的可读性。",
            },
            "t2i_word_threshold": {
                "description": "文本转图像字数阈值",
                "type": "int",
                "hint": "超出此字符长度的文本将会被转换成图片。字数不能低于 50。",
            },
            "admins_id": {
                "description": "管理员 ID",
                "type": "list",
                "items": {"type": "string"},
                "hint": "管理员 ID 列表，管理员可以使用一些特权命令，如 `update`, `plugin` 等。ID 可以通过 `/sid` 指令获得。回车添加，可添加多个。",
            },
            "http_proxy": {
                "description": "HTTP 代理",
                "type": "string",
                "hint": "启用后，会以添加环境变量的方式设置代理。格式为 `http://ip:port`",
            },
            "log_level": {
                "description": "控制台日志级别",
                "type": "string",
                "hint": "控制台输出日志的级别。",
                "options": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            },
            "t2i_endpoint": {
                "description": "文本转图像服务接口",
                "type": "string",
                "hint": "为空时使用 AstrBot API 服务",
            },
            "pip_install_arg": {
                "description": "pip 安装参数",
                "type": "string",
                "hint": "安装插件依赖时，会使用 Python 的 pip 工具。这里可以填写额外的参数，如 `--break-system-package` 等。",
            },
            "plugin_repo_mirror": {
                "description": "插件仓库镜像",
                "type": "string",
                "hint": "已废弃，请使用管理面板->设置页的代理地址选择",
                "obvious_hint": True,
                "options": [
                    "default",
                    "https://ghp.ci/",
                    "https://github-mirror.us.kg/",
                ],
            },
        },
    },
}

DEFAULT_VALUE_MAP = {
    "int": 0,
    "float": 0.0,
    "bool": False,
    "string": "",
    "text": "",
    "list": [],
    "object": {},
}


# "project_atri": {
#     "description": "Project ATRI 配置",
#     "type": "object",
#     "items": {
#         "enable": {"description": "启用", "type": "bool"},
#         "long_term_memory": {
#             "description": "长期记忆",
#             "type": "object",
#             "items": {
#                 "enable": {"description": "启用", "type": "bool"},
#                 "summary_threshold_cnt": {
#                     "description": "摘要阈值",
#                     "type": "int",
#                     "hint": "当一个会话的对话记录数量超过该阈值时，会自动进行摘要。",
#                 },
#                 "embedding_provider_id": {
#                     "description": "Embedding provider ID",
#                     "type": "string",
#                     "hint": "只有当启用了长期记忆时，才需要填写此项。将会使用指定的 provider 来获取 Embedding，请确保所填的 provider id 在 `配置页` 中存在并且设置了 Embedding 配置",
#                     "obvious_hint": True,
#                 },
#                 "summarize_provider_id": {
#                     "description": "Summary provider ID",
#                     "type": "string",
#                     "hint": "只有当启用了长期记忆时，才需要填写此项。将会使用指定的 provider 来获取 Summary，请确保所填的 provider id 在 `配置页` 中存在。",
#                     "obvious_hint": True,
#                 },
#             },
#         },
#         "active_message": {
#             "description": "主动消息",
#             "type": "object",
#             "items": {
#                 "enable": {"description": "启用", "type": "bool"},
#             },
#         },
#         "vision": {
#             "description": "视觉理解",
#             "type": "object",
#             "items": {
#                 "enable": {"description": "启用", "type": "bool"},
#                 "provider_id_or_ofa_model_path": {
#                     "description": "提供商 ID 或 OFA 模型路径",
#                     "type": "string",
#                     "hint": "将会使用指定的 provider 来进行视觉处理，请确保所填的 provider id 在 `配置页` 中存在。",
#                 },
#             },
#         },
#         "split_response": {
#             "description": "是否分割回复",
#             "type": "bool",
#             "hint": "启用后，将会根据句子分割回复以更像人类回复。每次回复之间具有随机的时间间隔。默认启用。",
#         },
#         "persona": {
#             "description": "人格",
#             "type": "string",
#             "hint": "默认人格。当启动 ATRI 之后，在 Provider 处设置的人格将会失效。",
#             "obvious_hint": True,
#         },
#         "chat_provider_id": {
#             "description": "Chat provider ID",
#             "type": "string",
#             "hint": "将会使用指定的 provider 来进行文本聊天，请确保所填的 provider id 在 `配置页` 中存在。",
#             "obvious_hint": True,
#         },
#         "chat_base_model_path": {
#             "description": "用于聊天的基座模型路径",
#             "type": "string",
#             "hint": "用于聊天的基座模型路径。当填写此项和 Lora 路径后，将会忽略上面设置的 Chat provider ID。",
#             "obvious_hint": True,
#         },
#         "chat_adapter_model_path": {
#             "description": "用于聊天的 Lora 模型路径",
#             "type": "string",
#             "hint": "Lora 模型路径。",
#             "obvious_hint": True,
#         },
#         "quantization_bit": {
#             "description": "量化位数",
#             "type": "int",
#             "hint": "模型量化位数。如果你不知道这是什么，请不要修改。默认为 4。",
#             "obvious_hint": True,
#         },
#     },
# },
