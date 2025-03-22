import wave
from io import BytesIO
import base64
import numpy as np


async def tencent_silk_to_wav(silk_path: str, output_path: str) -> str:
    import pysilk

    with open(silk_path, "rb") as f:
        input_data = f.read()
        if input_data.startswith(b"\x02"):
            input_data = input_data[1:]
        input_io = BytesIO(input_data)
        output_io = BytesIO()
        pysilk.decode(input_io, output_io, 24000)
        output_io.seek(0)
        with wave.open(output_path, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(24000)
            wav.writeframes(output_io.read())

    return output_path


async def wav_to_tencent_silk(wav_path: str, output_path: str) -> int:
    """返回 duration"""
    try:
        import pilk
    except (ImportError, ModuleNotFoundError) as _:
        raise Exception(
            "pilk 模块未安装，请前往管理面板->控制台->安装pip库 安装 pilk 这个库"
        )
    # with wave.open(wav_path, 'rb') as wav:
    #     wav_data = wav.readframes(wav.getnframes())
    #     wav_data = BytesIO(wav_data)
    #     output_io = BytesIO()
    #     pysilk.encode(wav_data, output_io, 24000, 24000)
    #     output_io.seek(0)

    #     # 在首字节添加 \x02,去除结尾的\xff\xff
    #     silk_data = output_io.read()
    #     silk_data_with_prefix = b'\x02' + silk_data[:-2]

    #     # return BytesIO(silk_data_with_prefix)
    #     with open(output_path, "wb") as f:
    #         f.write(silk_data_with_prefix)

    #     return 0
    with wave.open(wav_path, "rb") as wav:
        rate = wav.getframerate()
        duration = pilk.encode(wav_path, output_path, pcm_rate=rate, tencent=True)
        return duration




"""
将 Base64 编码的语音数据解码并存储为 WAV 文件。

:param base64_data: Base64 编码的语音数据
:param output_file: 输出的 WAV 文件路径
:param sample_rate: 采样率（默认 16000 Hz）
:param channels: 声道数（默认 1，单声道）
:param sample_width: 采样宽度（默认 2，16 位）
"""
async def base64_to_wav(base64_data, output_file : str, sample_rate=16000, channels=1, sample_width=2):
    # Base64 解码
    audio_data = base64.b64decode(base64_data)

    # 将解码后的数据转换为 numpy 数组（假设是 16 位 PCM 数据）
    audio_array = np.frombuffer(audio_data, dtype=np.int16)

    # 创建 WAV 文件
    with wave.open(output_file, 'wb') as wav_file:
        wav_file.setnchannels(channels)  # 设置声道数
        wav_file.setsampwidth(sample_width)  # 设置采样宽度
        wav_file.setframerate(sample_rate)  # 设置采样率
        wav_file.writeframes(audio_array.tobytes())  # 写入音频数据
