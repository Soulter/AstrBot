import os
import ssl
import shutil
import socket
import time
import aiohttp
import base64
import zipfile
import uuid
import psutil
from typing import Union

from PIL import Image


def on_error(func, path, exc_info):
    """
    a callback of the rmtree function.
    """
    print(f"remove {path} failed.")
    import stat

    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def remove_dir(file_path) -> bool:
    if not os.path.exists(file_path):
        return True
    try:
        shutil.rmtree(file_path, onerror=on_error)
        return True
    except BaseException:
        return False


def port_checker(port: int, host: str = "localhost"):
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(1)
    try:
        sk.connect((host, port))
        sk.close()
        return True
    except Exception:
        sk.close()
        return False


def save_temp_img(img: Union[Image.Image, str, bytes]) -> str:
    os.makedirs("data/temp", exist_ok=True)
    # 获得文件创建时间，清除超过 12 小时的
    try:
        for f in os.listdir("data/temp"):
            path = os.path.join("data/temp", f)
            if os.path.isfile(path):
                ctime = os.path.getctime(path)
                if time.time() - ctime > 3600 * 12:
                    os.remove(path)
    except Exception as e:
        print(f"清除临时文件失败: {e}")

    # 获得时间戳
    timestamp = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
    p = f"data/temp/{timestamp}.jpg"

    if isinstance(img, Image.Image):
        img.save(p)
    else:
        with open(p, "wb") as f:
            f.write(img)
    return p


async def download_image_by_url(
        url: str, post: bool = False, post_data: dict = None, path=None, use_proxy=False
) -> str:
    """
    下载图片, 返回 path
    """
    proxy = os.environ.get("https_proxy", None)
    try:
        async with aiohttp.ClientSession() as session:
            # 根据请求类型选择方法
            request_method = session.post if post else session.get

            # 构造请求参数
            request_kwargs = {}
            if use_proxy and proxy:  # 仅在需要代理时添加
                request_kwargs["proxy"] = proxy

            # 构造基础请求参数
            request_args = {"url": url, **request_kwargs}

            # 仅在 POST 请求时添加 json 参数
            if post and post_data:
                request_args["json"] = post_data

            async with request_method(**request_args) as resp:
                content = await resp.read()
                if path:
                    # 如果指定了路径，保存文件
                    with open(path, "wb") as f:
                        f.write(content)
                    return path
                else:
                    # 未指定路径，则保存为临时图片
                    return save_temp_img(content)
    except aiohttp.client.ClientConnectorSSLError:
        # 关闭 SSL 验证
        ssl_context = ssl.create_default_context()
        ssl_context.set_ciphers("DEFAULT")

        async with aiohttp.ClientSession() as session:
            request_method = session.post if post else session.get

            request_kwargs = {}
            if use_proxy and proxy:
                request_kwargs["proxy"] = proxy

            request_args = {"url": url, "ssl": ssl_context, **request_kwargs}
            if post and post_data:
                request_args["json"] = post_data

            async with request_method(**request_args) as resp:
                content = await resp.read()
                return save_temp_img(content)
    except Exception as e:
        raise e

async def download_file(
        url: str, path: str, show_progress: bool = False, use_proxy: bool=False
):
    """
    从指定 url 下载文件到指定路径 path
    """
    proxy = os.environ.get("https_proxy", None)
    try:
        async with aiohttp.ClientSession() as session:
            # 构造请求参数
            request_kwargs = {"timeout": aiohttp.ClientTimeout(total=1800)}  # 设置超时
            if use_proxy and proxy:  # 仅当代理启用时添加
                request_kwargs["proxy"] = proxy

            # 发起请求
            async with session.get(url, **request_kwargs) as resp:
                if resp.status != 200:
                    raise Exception(f"下载文件失败: {resp.status}")

                # 获取总文件大小（如果服务器响应中有 Content-Length）
                total_size = int(resp.headers.get("content-length", 0))
                downloaded_size = 0
                start_time = time.time()

                if show_progress:
                    print(f"文件大小: {total_size / 1024:.2f} KB | 文件地址: {url}")

                # 保存文件到指定路径
                with open(path, "wb") as f:
                    while True:
                        chunk = await resp.content.read(8192)
                        if not chunk:  # 如果无更多数据，退出循环
                            break
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        # 实时打印下载进度
                        if show_progress:
                            elapsed_time = time.time() - start_time
                            speed = downloaded_size / 1024 / elapsed_time  # KB/s
                            print(
                                f"\r下载进度: {downloaded_size / total_size:.2%} "
                                f"速度: {speed:.2f} KB/s",
                                end="",
                            )

    except aiohttp.client.ClientConnectorSSLError:
        # 捕获 SSL 错误时，创建自定义 SSL 上下文来禁用验证
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # 重新建立会话并发出请求
        async with aiohttp.ClientSession(trust_env=True) as session:
            request_kwargs = {"timeout": aiohttp.ClientTimeout(total=120), "ssl": ssl_context}
            if use_proxy and proxy:
                request_kwargs["proxy"] = proxy

            async with session.get(url, **request_kwargs) as resp:
                if resp.status != 200:
                    raise Exception(f"下载文件失败: {resp.status}")

                total_size = int(resp.headers.get("content-length", 0))
                downloaded_size = 0
                start_time = time.time()

                if show_progress:
                    print(f"文件大小: {total_size / 1024:.2f} KB | 文件地址: {url}")

                with open(path, "wb") as f:
                    while True:
                        chunk = await resp.content.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        if show_progress:
                            elapsed_time = time.time() - start_time
                            speed = downloaded_size / 1024 / elapsed_time  # KB/s
                            print(
                                f"\r下载进度: {downloaded_size / total_size:.2%} "
                                f"速度: {speed:.2f} KB/s",
                                end="",
                            )

    except Exception as e:
        raise Exception(f"下载失败: {e}")

    if show_progress:
        print()



def file_to_base64(file_path: str) -> str:
    with open(file_path, "rb") as f:
        data_bytes = f.read()
        base64_str = base64.b64encode(data_bytes).decode()
    return "base64://" + base64_str


def get_local_ip_addresses():
    net_interfaces = psutil.net_if_addrs()
    network_ips = []

    for interface, addrs in net_interfaces.items():
        for addr in addrs:
            if addr.family == socket.AF_INET:  # 使用 socket.AF_INET 代替 psutil.AF_INET
                network_ips.append(addr.address)

    return network_ips


async def get_dashboard_version():
    if os.path.exists("data/dist"):
        if os.path.exists("data/dist/assets/version"):
            with open("data/dist/assets/version", "r") as f:
                v = f.read().strip()
                return v
    return None


async def download_dashboard():
    """下载管理面板文件"""
    dashboard_release_url = "https://astrbot-registry.soulter.top/download/astrbot-dashboard/latest/dist.zip"
    try:
        await download_file(
            dashboard_release_url, "data/dashboard.zip", show_progress=True
        )
    except BaseException as _:
        dashboard_release_url = (
            "https://github.com/Soulter/AstrBot/releases/latest/download/dist.zip"
        )
        await download_file(
            dashboard_release_url, "data/dashboard.zip", show_progress=True
        )
    print("解压管理面板文件中...")
    with zipfile.ZipFile("data/dashboard.zip", "r") as z:
        z.extractall("data")
