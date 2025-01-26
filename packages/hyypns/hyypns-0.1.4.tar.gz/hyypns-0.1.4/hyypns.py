# -*- encoding: utf-8 -*-

"""
一些工具:
    比如复制文件,获取当前工作目录,
    获取桌面位置,获取用户名,获取Python版本,
    获取当前时间,暂停程序多少秒...

使用某些函数时,可能需要适当权限!
在查询用户历史记录时，请确保遵循隐私法律和最佳实践.
"""

#module
import os
import re
import wmi
import sys
import time
import hmac
import math
import docker
import signal
import ctypes
import shutil
import winreg
import base64
import hashlib
import sqlite3
import requests
import platform
import threading
import subprocess
import ctypes.util
import http.client
from tkinter import *
from PIL import Image
from pyfiglet import Figlet
from decimal import Decimal, getcontext


close_list = ['normal','sys','decr',' ']

returns_list = ['data','reshead','state','response']


def open_app(app_path = None,app_name = None):
    """
    打开应用程序
    app_path:如果是Windows系统的话填app的路径,
    app_name:如果是Linux系统的话填app的名称.
    """
    if system() == 'Windows':
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "open", app_path, None, None, 1)
        except Exception as e:
            print(f"Error: {e}")


    else:
        try:
            subprocess.run([app_name])

        except Exception as e:
            print('Error:',e)


class Errormess(Exception):
    """捕获异常,和Exception一样"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


def totp(secret, time_step=30, length=6):
    """生成基于 HMAC 的一次性密码 (OTP)(必须是Base32编码)"""
    current_time = int(time.time()) // time_step

    time_bytes = current_time.to_bytes(8, byteorder='big')

    hmac_hash = hmac.new(base64.b32decode(secret), time_bytes, hashlib.sha1).digest()

    offset = hmac_hash[-1] & 0x0F
    binary = (hmac_hash[offset] & 0x7F) << 24 | (hmac_hash[offset + 1] & 0xFF) << 16 | \
                (hmac_hash[offset + 2] & 0xFF) << 8 | (hmac_hash[offset + 3] & 0xFF)

    otp = binary % (10 ** length)
        
    return str(otp).zfill(length)


def convert_to_utf8(input_file, input_encoding, output_file, contents = False):
    try:
        # 以指定编码打开输入文件
        with open(input_file, 'r', encoding=input_encoding) as infile:
            content = infile.read()

        # 以 UTF - 8 编码打开输出文件并写入内容
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write(content)

        if contents == False:
            pass

        else:
            return content

    except UnicodeDecodeError:
        print(f"无法以 {input_encoding} 编码读取 {input_file} 文件，请检查编码是否正确。")
    except Exception as e:
        print(f"转换过程中出现错误: {e}")


def Version():
    """获取当前 Python 版本"""
    try:
        # 运行 python --version 命令
        result = subprocess.run(["python", "--version"], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"获取版本信息失败: {e}"


version = Version()

def hard():
    """获取硬件信息(主板,声卡,CPU,显卡等)"""

    hardware_info = {
        "CPU": None,
        "Motherboard": None,
        "GPU": None,
        "Sound Card": None,
        "Screen": None,
    }

    # 获取 CPU 信息
    cpu_info = subprocess.run("wmic cpu get name", capture_output=True, text=True)
    hardware_info["CPU"] = cpu_info.stdout.splitlines()[1].strip()

    # 获取主板信息
    motherboard_info = subprocess.run("wmic baseboard get product", capture_output=True, text=True)
    hardware_info["Motherboard"] = motherboard_info.stdout.splitlines()[1].strip()

    # 获取显卡信息
    gpu_info = subprocess.run("wmic path win32_VideoController get name", capture_output=True, text=True)
    hardware_info["GPU"] = [line.strip() for line in gpu_info.stdout.splitlines() if line.strip()][1:]  # 过滤空行

    # 获取声卡信息
    sound_info = subprocess.run("wmic sounddev get name", capture_output=True, text=True)
    hardware_info["Sound Card"] = [line.strip() for line in sound_info.stdout.splitlines() if line.strip()][1:]  # 过滤空行

    # 假设“屏幕”信息为监视器名（使用 `wmic` 查询）
    screen_info = subprocess.run("wmic path win32_monitor get name", capture_output=True, text=True)
    hardware_info["Screen"] = [line.strip() for line in screen_info.stdout.splitlines() if line.strip()][1:]  # 过滤空行

    return hardware_info

hardware_info = hard()
for key, value in hardware_info.items():
    pass


class hardware:
    global c
    c = wmi.WMI()

    def cpu():
        """获取 CPU 型号信息"""
        for cpu in c.Win32_Processor():
            print(f"CPU 名称: {cpu.Name}")
            print(f"CPU 核心数: {cpu.NumberOfCores}")
        
    def memory():
        """获取内存信息"""
        for mem in c.Win32_PhysicalMemory():
            print(f"内存大小: {int(mem.Capacity) / (1024 ** 2):.2f} MB")
        
    def disk():
        """获取硬盘信息"""
        for disk in c.Win32_LogicalDisk():
            print(f"磁盘: {disk.DeviceID},  可用空间: {int(disk.FreeSpace) / (1024 ** 3):.2f} GB")

    def heatdiss():
        """获取系统中的声卡信息"""
        sound_cards = c.Win32_SoundDevice()  # 获取声音设备列表

        sound_list = []

        for sound_card in sound_cards:
            sound_card_info = {
                "name": sound_card.Name,
                "manufacturer": sound_card.AdapterCompatibility,
                "productID": sound_card.ProductID,
                "status": sound_card.Status
            }
            sound_list.append(sound_card_info)

        return sound_list

    def GPU(get = 'name'):
        """获取系统中的 GPU 信息 并以字典的方式返回"""
        gpu_info_list = []
        gpus = c.Win32_VideoController()  # 获取视频控制器列表（GPU）
        
        for gpu in gpus:
            gpu_info = {
                "name": gpu.Name,
                "manufacturer": gpu.AdapterCompatibility,
                "memory": int(gpu.AdapterRAM) / (1024 ** 2),  # 转换为 MB
                "status": gpu.Status
            }
            gpu_info_list.append(gpu_info)

        return gpu_info_list


class Sandbox:
    """云沙箱"""
    def sandbox(program_name):
        """创建 Docker 沙箱并运行指定程序"""
        client = docker.from_env()

        try:
            # 创建 Docker 镜像
            client.images.build(path='.', tag='my_sandbox')

            # 运行容器并执行指定程序
            container = client.containers.run('my_sandbox', program_name, detach=True)
            print(f"容器 '{container.id}' 正在运行...")

            # 等待容器完成，并获取输出
            container.wait()
            logs = container.logs()
            return logs.decode()
            """
            print("容器输出：")
            print(logs.decode())
            """

        except docker.errors.BuildError as build_error:
            print(f"构建镜像失败: {build_error}")
        except Exception as e:
            print(f"发生错误: {e}")


def browser(browser):
    """
    获取指定浏览器的历史记录
    browser:浏览器,可填:chrome,firefox(火狐),edge.
    示例:

    browser_name = input("请输入浏览器名称 (Chrome, Firefox, Edge): ").strip()
    history_list = browser(browser_name)
    
    print(f"{browser_name} 用户的历史记录:")
    for record in history_list:
        if browser_name.lower() == 'firefox':
            url, title, visit_count, last_visit_time = record
            print(f"{title} ({url}) - 访问次数: {visit_count} - 最后访问时间: {last_visit_time}")
        else:
            url, title, visit_count, last_visit_time = record
            print(f"{title} ({url}) - 访问次数: {visit_count}")

    """
    history_records = []

    if browser.lower() == 'chrome':
        # Chrome 历史记录文件路径
        user_profile = os.environ.get('USERPROFILE')
        history_db_path = os.path.join(user_profile, r'AppData\Local\Google\Chrome\User Data\Default\History')

        if not os.path.exists(history_db_path):
            print("Chrome 历史记录文件不存在")
            return []
        
        # 连接到 SQLite 数据库
        connection = sqlite3.connect(history_db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 10")
        history_records = cursor.fetchall()
        connection.close()

    elif browser.lower() == 'firefox':
        # Firefox 历史记录文件路径
        user_profile = os.environ.get('APPDATA')
        history_db_path = os.path.join(user_profile, r'Mozilla\Firefox\Profiles')

        # 找到 places.sqlite 文件
        profile = None
        for folder in os.listdir(history_db_path):
            if folder.endswith('.default-release') or 'default' in folder:
                profile = folder
                break

        if profile is None:
            print("Firefox 配置文件不存在")
            return []

        places_db_path = os.path.join(history_db_path, profile, 'places.sqlite')
        if not os.path.exists(places_db_path):
            print("Firefox 历史记录文件不存在")
            return []

        # 连接到 SQLite 数据库
        connection = sqlite3.connect(places_db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT url, title, visit_count, last_visit_date FROM moz_places ORDER BY last_visit_date DESC LIMIT 10")
        history_records = cursor.fetchall()
        connection.close()

    elif browser.lower() == 'edge':
        # Edge 历史记录文件路径
        user_profile = os.environ.get('USERPROFILE')
        history_db_path = os.path.join(user_profile, r'AppData\Local\Microsoft\Edge\User Data\Default\History')

        if not os.path.exists(history_db_path):
            print("Edge 历史记录文件不存在")
            return []
        
        # 连接到 SQLite 数据库
        connection = sqlite3.connect(history_db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 10")
        history_records = cursor.fetchall()
        connection.close()

    else:
        print("不支持的浏览器，请选择 Chrome、Firefox 或 Edge。")
        return []

    return history_records


def users():
    """
    获取当前电脑上的所有用户列表
    返回:列表
    """
    users = []
    
    if system() == 'Windows':

        registry_path = r'Software\Microsoft\Windows NT\CurrentVersion\ProfileList'

        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
                num_values = winreg.QueryInfoKey(key)[0]
                
                for i in range(num_values):
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        try:
                            profile_path = winreg.QueryValueEx(subkey, 'ProfileImagePath')[0]
                            user_name = profile_path.split('\\')[-1]
                            users.append(user_name)
                        except FileNotFoundError:
                            continue
        except Exception as e:
            print(f"发生错误: {e}")

        return users
    
    else:
        users = []

        try:
            with open("/etc/passwd", "r") as f:
                for line in f:
                    parts = line.split(":")
                    user_name = parts[0]
                    users.append(user_name)
        except Exception as e:
            print(f"发生错误: {e}")

        return users


def fetch_url(url, method='GET', body=None, headers=None, encoding='utf-8', returns='data'):
    """
    从指定的 URL 获取内容
    url:请求的url,
    method:请求方式(GET或POST),
    encoding:编码格式,
    returns:返回的数据可print一下returns_list获取参数(默认返回Data).
    """
    # 解析 URL
    scheme, host, path = parse_url(url)

    # 创建连接
    conn = http.client.HTTPSConnection(host) if scheme == "https" else http.client.HTTPConnection(host)

    try:
        # 发送请求：支持 GET 或 POST
        conn.request(method, path, body, headers or {})

        # 获取响应
        response = conn.getresponse()

        # 打印状态代码和响应头
        print("状态:", response.status)
        print("响应头:", response.getheaders())

        # 读取响应数据
        data = response.read()

        if returns == 'data':
            return data.decode(encoding)
        
        elif returns == 'reshead':
            return response.getheaders()
        
        elif returns == 'state':
            return response.status
        
        elif returns == 'response':
            return response

    except Exception as e:
        print(f"发生错误: {e}")  # 修复了错误信息的打印
    finally:
        conn.close()  # 确保连接关闭

def parse_url(url):
    """解析 URL,返回 schema, host, path"""
    if url.startswith("http://"):
        scheme = "http"
        path = url[7:]  # 去掉 "http://"
    elif url.startswith("https://"):
        scheme = "https"
        path = url[8:]  # 去掉 "https://"
    else:
        raise ValueError("不支持的 URL 协议")

    # 从 URL 中提取 host 和 path
    if '/' in path:
        host, path = path.split('/', 1)
        return scheme, host, '/' + path
    else:
        return scheme, path, '/'

"""
if __name__ == "__main__":
    # 示例 URL
    url = "https://httpbin.org/get"  # 替换为您要请求的网址
    response_data = fetch_url(url)
    print("响应数据:", response_data)"""


def default(txt,font = "larry3d"):
    """
    艺术字(pyfiglet)
    txt:字
    font:字体(默认3D字体)
    """
    f = Figlet(font=font, width=200)

    print(f.renderText(txt))


class WordArt:
    global DEFAULT_FONT
    global COLOR_CODES
    global RESET_COLOR
    global parse_color
    global figlet_format
    global FONTS

    DEFAULT_FONT = 'standard'

    COLOR_CODES = {
        'BLACK': 30, 'RED': 31, 'GREEN': 32, 'YELLOW': 33,
        'BLUE': 34, 'MAGENTA': 35, 'CYAN': 36, 'LIGHT_GRAY': 37,
        'DEFAULT': 39, 'WHITE': 97, 'RESET': 0
    }

    RESET_COLOR = '\033[0m'

    FONTS = {
        "standard": {
            "A": "  A  \n A A \nAAAAA\nA   A\nA   A",
            "B": "BBBB \nB   B\nBBBB \nB   B\nBBBB ",
            "C": " CCC \nC   C\nC    \nC   C\n CCC ",
            "D": "DDDD \nD   D\nD   D\nD   D\nDDDD ",
            "E": "EEEEE\nE    \nEEEEE\nE    \nEEEEE",
            "F": "FFFFF\nF    \nFFFFF\nF    \nF    ",
            "G": " GGG \nG    \nG  GG\nG   G\n GGG ",
            "H": "H   H\nH   H\nHHHHH\nH   H\nH   H",
            "I": "IIIII\n  I  \n  I  \n  I  \nIIIII",
            "J": "JJJJJ\n    J\n    J\nJ   J\n JJJ ",
            "K": "K   K\nK  K \nKK   \nK  K \nK   K",
            "L": "L    \nL    \nL    \nL    \nLLLLL",
            "M": "M   M\nMM MM\nM M M\nM   M\nM   M",
            "N": "N   N\nN N N\nN  NN\nN   N\nN   N",
            "O": " OOO \nO   O\nO   O\nO   O\n OOO ",
            "P": "PPPP \nP   P\nPPPP \nP    \nP    ",
            "Q": " QQQ \nQ   Q\nQ  Q \nQQQQ \n    Q",
            "R": "RRRR \nR   R\nRRRR \nR R  \nR  RR",
            "S": " SSS \nS    \n SSS \n    S\n SSS ",
            "T": "TTTTT\n  T  \n  T  \n  T  \n  T  ",
            "U": "U   U\nU   U\nU   U\nU   U\n UUU ",
            "V": "V   V\nV   V\nV   V\n V V \n  V  ",
            "W": "W   W\nW   W\nW W W\nWW WW\nW   W",
            "X": "X   X\n X X \n  X  \n X X \nX   X",
            "Y": "Y   Y\n Y Y \n  Y  \n  Y  \n  Y  ",
            "Z": "ZZZZZ\n   Z \n  Z  \n Z   \nZZZZZ",
            " ": "     \n     \n     \n     \n     "
        }
    }

    def figlet_format(text, font=DEFAULT_FONT):
        """渲染文本为所选字体的 ASCII 艺术"""
        output_lines = ['' for _ in range(5)]
        current_font = FONTS.get(font, FONTS[DEFAULT_FONT])

        for char in text:
            if char in current_font:
                char_representation = current_font[char].splitlines()
                for i in range(len(output_lines)):
                    if i < len(char_representation):
                        output_lines[i] += char_representation[i] + "  "
                    else:
                        output_lines[i] += " " * 5
            else:
                # 处理未知字符，留白
                for i in range(len(output_lines)):
                    output_lines[i] += " " * 5  # 留出字符宽度

        return "\n".join(output_lines)

    def parse_color(color_str):
        """解析颜色字符串"""
        return f'\033[{COLOR_CODES.get(color_str.upper(), COLOR_CODES["DEFAULT"])}m'

    def wordart(text, font=DEFAULT_FONT, color='DEFAULT'):
        ansi_color = parse_color(color)  # 获取 ANSI 颜色码

        # 格式化输出文本
        formatted_text = figlet_format(text, font)

        # 打印文本
        print(ansi_color + formatted_text + RESET_COLOR)

    # 例子
    # 直接调用函数来渲染文本
    #wordart("HELLO", font='standard', color='RED')
    #wordart("WORLD", font='standard', color='GREEN')


def opens(url = '',browser = 'msedge'):
    """
    对应不同的操作系统打开浏览器和url
    url:url
    如果url为空那就打开浏览器主页.
    browser:使用的浏览器,默认msedge(Edge).可以自己切换,
    比如firefox,chrome等,不过你得确认你有没有安装这个浏览器!(browser也是执行的文件名)(Edge测试正常).
    如果你把默认的浏览器改成空,那他就会打开用户主页.
    """
    if system() == 'Windows':
        try:
            subprocess.run(["start", browser, url], shell=True)

        except Exception as e:
            print(f"打开浏览器失败: {e}")

    elif system() == 'macOS':
        try:
            if browser == 'msedge':
                #Microsoft Edge
                subprocess.run(["open", "-a", "Microsoft Edge", url])
            else:
                subprocess.run(["open", "-a", "Safari", url])  # 替换为相应浏览器
        except Exception as e:
            print(f"打开浏览器失败: {e}")

    elif system() == 'Linux':
        try:
            if browser == 'msedge':
                #microsoft-edge
                subprocess.run(["microsoft-edge", url])
            else:
                subprocess.run(["xdg-open", url])  # xdg-open 是在大多数 Linux 发行版中使用的命令
        except Exception as e:
            print(f"打开浏览器失败: {e}")


def download(url, destination, Savelocation,
              Sen = 'get'):
    """
    在互联网上下载文件
    url:下载链接
    destination:下载完成后的名字
    Savelocation:保存位置
    Sen:发送方式,可填'get'和'post',默认get.
    """
    try:
        os.chdir(Savelocation)
        if Sen == 'get':
            response = requests.get(url, stream=True)

        if Sen == 'post':
            response = requests.post(url, stream=True)

        else:
            response = requests.get(url, stream=True)

        response.raise_for_status()

        with open(destination, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)

    except Exception as e:
        print(f"Failed to download the file due to error: {e}")


def system(none = None):
    """通过调用系统命令识别操作系统"""
    if none == None:
        try:
            result = subprocess.run("ver", capture_output=True, text=True, shell=True)
            if "Microsoft" in result.stdout:
                return "Windows"
            
            result = subprocess.run("uname", capture_output=True, text=True, shell=True)
            if "Darwin" in result.stdout:
                return "macOS"
            
            result = subprocess.run("uname", capture_output=True, text=True, shell=True)
            if "Linux" in result.stdout:
                return "Linux"
            
        except Exception as e:
            return f"发生错误: {e}"

        return "未知操作系统"

    else:
        return none


def desktop():
    """获取桌面位置(Desktop)"""
    return os.path.join(os.path.expanduser("~"), "Desktop")


def username():
    """获取用户名"""

    if platform.system() == "Windows":
        return os.getenv("USERNAME")

    else:
        return os.getenv("USER")


def timecur():
    """获取当前时间"""
    if platform.system() == "Windows":
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    else:
        return os.popen('date').read().strip()


def timemin(minutes):
    """获取minutes分钟前的时间"""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - minutes * 60))


def sleep(seconds):
    """
    暂停程序指定的秒数
    seconds:秒
    """
    event = threading.Event()
    event.wait(timeout=seconds)


def close(method = 'sys'):
    """
    关闭程序
    method:关闭方式
    """
    if system() == 'Windows':
        if method == 'decr':
            raise Exception("程序结束")
        
        elif method == 'sys':
            sys.exit()

        else:
            print('not method')

    else:
        if method == 'decr':
            raise Exception("程序结束")
        
        elif method == 'sys':
            sys.exit()
        
        elif method == 'normal':
            os.kill(os.getpid(), signal.SIGTERM)

        else:
            print('not method')


def route(relative_path):
    """
    从相对路径获取绝对路径
    relative_path:相对路径
    """
    # 检查该路径是否存在
    if os.path.exists(relative_path):
        print("该路径存在。")
    else:
        print("该路径不存在。")

    # 获取对应的绝对路径
    return os.path.abspath(relative_path)


def filehash(file_path):
    """
    计算给定文件的 SHA256 哈希值
    file_path:文件路径
    """
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        # 按块读取文件内容以避免占用大量内存
        for byte_block in iter(lambda: f.read(4096), b""):
            hash_sha256.update(byte_block)
            
    return hash_sha256.hexdigest()


def copy(source_file,destination_file):
    """
    复制文件
    source_file:源文件路径,例如 "C:/path/to/source.txt"
    destination_file:目标文件路径,例如 "C:/path/to/destination.txt"
    """
    try:

        with open(source_file, 'rb') as src:
            content = src.read()
            
        with open(destination_file, 'wb') as dest:
            dest.write(content)
        
    except FileNotFoundError:
        print("源文件不存在:", source_file)
    except Exception as e:
        print("发生错误:", e)

def copy_secure(source_file,destination_file):
    """
    更保险的复制文件
    source_file:源文件路径,例如 "C:/path/to/source.txt"
    destination_file:目标文件路径,例如 "C:/path/to/destination.txt"
    """
    try:
        source_hash = filehash(source_file)

        with open(source_file, 'rb') as src, open(destination_file, 'wb') as dest:
            dest.write(src.read())

        destination_hash = filehash(destination_file)

        if source_hash == destination_hash:
            pass

        else:
            print("文件复制完成，但验证失败：内容不匹配。")

    except FileNotFoundError:
        print("源文件不存在:", source_file)
    except Exception as e:
        print("发生错误:", e)

def copy_secure2(source_file,destination_file):
    """
    更更更保险的复制文件
    source_file:源文件路径,例如 "C:/path/to/source.txt"
    destination_file:目标文件路径,例如 "C:/path/to/destination.txt"
    """

    temp_file = destination_file + '.tmp'

    try:
        shutil.copy2(source_file, temp_file)# 使用copy2

        source_hash = filehash(source_file)

        destination_hash = filehash(temp_file)

        if source_hash == destination_hash:
            os.rename(temp_file, destination_file)

        else:
            print("文件复制完成，但验证失败：内容不匹配。")
            os.remove(temp_file)

    except Exception as e:
        print("发生错误:", e)
        if os.path.exists(temp_file):
            os.remove(temp_file)

def execute_command(command):
    """
    执行给定的命令(Android)
    command:命令
    """
    try:
        # 使用 ADB 执行命令
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"命令执行失败: {e}")
        return None

def copy3_secure(source_file,destination_file,yes_or_no = False):
    """
    更更更更保险的方式复制文件
    source_file:源文件路径,例如 "C:/path/to/source.txt"
    destination_file:目标文件路径,例如 "C:/path/to/destination.txt"
    yes_or_no:是否覆盖文件,默认不覆盖.False:不覆盖,True:覆盖
    """
    if os.path.exists(destination_file):
        if yes_or_no != False:
            return

    source_hash = filehash(source_file)
    temp_file = destination_file + '.tmp'

    try:
        chunk_size=4096
        with open(temp_file, 'rb') as source_file:
            with open(destination_file, 'wb') as dest_file:
                while True:
                    chunk = source_file.read(chunk_size)
                    if not chunk:
                        break
                    dest_file.write(chunk)

        temp_hash = filehash(temp_file)

        if source_hash == temp_hash:
                os.rename(temp_file, destination_file)
        else:
            print("文件复制完成，但验证失败：内容不匹配。")
            os.remove(temp_file)

    except FileNotFoundError:
        print("源文件不存在:", source_file)
    except Exception as e:
        print("发生错误:", str(e))
        if os.path.exists(temp_file):
            os.remove(temp_file)


def software():
    """获取当前安装的软件列表(实验性)"""
    software_list = []

    # Windows 64-bit 和 32-bit 注册表路径
    registry_keys = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    for registry_key in registry_keys:
        try:
            # 打开注册表项
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_key) as key:
                for i in range(0, winreg.QueryInfoKey(key)[0]):
                    try:
                        # 读取每个子键的 DisplayName
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            software_list.append(display_name)
                    except FileNotFoundError:
                        continue
        except FileNotFoundError:
            continue

    return software_list

class adb:
    """
    执行ADB命令需要用USB链接安卓设备!!!
    如果没有链接安卓设备ADB命令是无效的!!!
    设备需要 Root 权限:此方法仅在设备已经获得 Root 权限的情况下有效。如果没有 Root 权限，将无法成功切换到 Root 用户。
    电脑需要安装ADB,并且需要存在于环境变量path中ADB命令才有效
    
    安全性:Root 权限将使用户能访问系统的所有文件和资源，这既带来了灵活性，也会提高安全风险。因此要谨慎使用。

    ADB 设置:确保 ADB 已正确安装并与设备成功连接。USB 调试需开启。

    使用风险:使用 Root 权限时需要小心操作，尽量避免侵入系统关键文件或应用，这可能导致系统崩溃或其他技术问题。

    链接安卓设备示例:

    #通过USB链接
    usb()
        
    # 获取设备 IP 地址
    device_ip = getip()
    if device_ip:
        # 通过 Wi-Fi 连接
        wifi(device_ip)
        #尝试切换到root用户(Android最高权限,需要Android已解锁root)
        root()
    """

    def install_apk(apk_path):
        """
        安装指定的 APK 文件
        apk_path:apk文件的路径
        """
        try:
            # 使用 ADB 安装 APK 文件
            subprocess.run(["adb", "install", apk_path], check=True)
            print(f"成功安装 APK: {apk_path}")
        except subprocess.CalledProcessError as e:
            print(f"安装失败: {e}")
        except FileNotFoundError:
            print("未找到 ADB，确保 ADB 已安装并正确配置在 PATH 中。")

    def uninstall_app(package_name):
        """
        卸载指定包名的应用
        package_name:应用名称
        """
        try:
            # 使用 ADB 卸载应用
            subprocess.run(["adb", "uninstall", package_name], check=True)
            print(f"成功卸载应用: {package_name}")
        except subprocess.CalledProcessError as e:
            print(f"卸载失败: {e}")
        except FileNotFoundError:
            print("未找到 ADB，确保 ADB 已安装并正确配置在 PATH 中。")

    def shutdown_device():
        """通过 ADB 命令关闭 Android 设备"""
        try:
            # 使用 ADB 进行关机
            subprocess.run(["adb", "shell", "reboot", "-p"], check=True)
            print("设备正在关机...")
        except subprocess.CalledProcessError as e:
            print(f"关机失败: {e}")
        except FileNotFoundError:
            print("未找到 ADB，确保 ADB 已安装并正确配置在 PATH 中。")

    def reboot_device():
        """通过 ADB 命令重启 Android 设备"""
        try:
            # 使用 ADB 进行关机
            subprocess.run(["adb", "reboot"], check=True)
            print("设备正在关机...")
        except subprocess.CalledProcessError as e:
            print(f"关机失败: {e}")
        except FileNotFoundError:
            print("未找到 ADB，确保 ADB 已安装并正确配置在 PATH 中。")

    def reboot_to_recovery():
        """通过 ADB 命令重启 Android 设备到恢复模式"""
        try:
            # 使用 ADB 进入恢复模式
            subprocess.run(["adb", "reboot", "recovery"], check=True)
            print("设备正在重启到恢复模式...")
        except subprocess.CalledProcessError as e:
            print(f"重启到恢复模式失败: {e}")
        except FileNotFoundError:
            print("未找到 ADB，确保 ADB 已安装并正确配置在 PATH 中。")

    def usb():
        """通过 USB 连接 Android 设备"""
        try:
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True)

            if "device" in result.stdout:
                """设备已通过 USB 连接"""
                pass

            else:
                print("没有找到已连接的设备，请确认 USB 调试已开启。")
        except FileNotFoundError:
            print("未找到 ADB，确保 ADB 已安装并正确配置在 PATH 中。")

    def getip():
        """获取设备的 IP 地址"""
        try:
            result = subprocess.run(["adb", "shell", "ip", "route"], capture_output=True, text=True)
            # 使用正则表达式提取 IP 地址
            ip_address = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
            if ip_address:
                return ip_address.group(0)
            else:
                print("未能获取设备 IP 地址，请确认设备已连接。")
                return None
        except FileNotFoundError:
            print("未找到 ADB，确保 ADB 已安装并正确配置在 PATH 中。")
            return None

    def wifi(ip_address):
        """
        通过 Wi-Fi 连接 Android 设备
        ip_address:Android设备的ip地址,可以从getip函数获取.
        """
        try:
            """进入无限调试模式"""
            subprocess.run(["adb", "tcpip", "5555"], check=True)
            # 通过 IP 地址连接设备
            subprocess.run(["adb", "connect", ip_address + ":5555"], check=True)
            print(f"成功连接到设备：{ip_address}")
        except subprocess.CalledProcessError as e:
            print(f"连接失败: {e}")

    def commands(command):
        """
        执行给定的命令
        command:命令
        """
        try:
            # 使用 ADB 执行命令
            result = subprocess.run(command, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            print(f"命令执行失败: {e}")
            return None

    def root():
        """尝试切换到 Root 用户"""
        command = ["adb", "shell", "su"]
        output = execute_command(command)

        if "permission denied" in output.lower():
            print("没有权限切换到 Root 用户，确保设备已 Root 并安装了适当的权限管理。")

        else:
            print("已成功切换到 Root 用户。")

def admin():
    """判断有没有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def uac():
    """弹出请求管理员权限界面"""
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

class Setting(adb):
    desktop = desktop()
    user = username()
    time_cur = timecur()
    admin = admin()
    
ADB = adb
android = adb
DESKTOP = desktop()
USERNAME = username()
folder_path = os.path.expanduser("~")

def getcwd():
    """get? 获取当前工作目录"""
    if os.name == 'nt':  # Windows
        kernel32 = ctypes.WinDLL('kernel32')
        buffer = ctypes.create_unicode_buffer(260)
        kernel32.GetCurrentDirectoryW(260, buffer)
        return buffer.value
        
    else:  # Unix/Linux
        libc = ctypes.CDLL(ctypes.util.find_library('c'))
        buffer = ctypes.create_string_buffer(4096)
        libc.getcwd(buffer, 4096)
        return buffer.value.decode('utf-8')


def pytodll(file):
    """将py文件编译成dll文件(实验性,可能无法生成可用的dll文件)"""
    python_file = file
    if python_file:
        with open("converted.pyx", "w") as f:
            with open(python_file, "r") as py_file:
                f.write(py_file.read())

        with open("setup.py", "w") as f:
            f.write("""
    from setuptools import setup
    from Cython.Build import cythonize

    setup(
        ext_modules=cythonize("converted.pyx"),
    )
    """)
        # 运行 setup.py 以编译 .pyx 文件为 DLL
        result = subprocess.run(["python", "setup.py", "build_ext", "--inplace"], capture_output=True, text=True)
        if result.returncode == 0:
            print("DLL 文件已生成。")
        else:
            print("生成 DLL 失败:", result.stderr)

    else:
        print("未选择文件。")


def vmxfile(vmx_path, iso_path):
    """创建虚拟机的 VMX 文件配置"""
    with open(vmx_path, 'w') as vmx_file:
        vmx_file.write('''# Virtual Machine Configuration
.encoding = "UTF-8"
memsize = "2048"
numvcpus = "1"
displayName = "My Virtual Machine"
guestOS = "otherGuest64"
ide1:0.fileName = "{}"
floppy0.startConnected = "FALSE"
ethernet0.connectionType = "nat"
ethernet0.addressType = "generated"
'''.format(iso_path))

def virt(vmx_path, iso_path):
    """创建虚拟机"""
    vmxfile(vmx_path, iso_path)
    command = ["vmrun", "create", vmx_path]
    subprocess.run(command, check=True)
    print("虚拟机创建成功:", vmx_path)

def startvirt(vmx_path,hidden = True):
    """启动虚拟机进行安装"""
    if hidden == True:
        command = ["vmrun", "start", vmx_path, "nogui"]  # "nogui" 表示隐藏 GUI

    else:
        command = ["vmrun", "start", vmx_path]

    subprocess.run(command, check=True)
    print("虚拟机已启动.")


def virtrun(iso_path,vmx_path,start = True):
    virt(vmx_path, iso_path)

    if start == True:
        startvirt(vmx_path)

    else:
        pass

#示例:
"""
vmx_path = "C:\\Path\\To\\Your\\VirtualMachine.vmx"  # 替换为实际 VMX 文件路径
iso_path = "C:\\Path\\To\\Your\\test.iso"  # 替换为实际 ISO 文件路径
virtrun(iso_path,vmx_path,start = True)(True是创建完后启动虚拟机,False是不)
"""


count = """public class AdvancedMathWithoutMathClass {

    public static double factorial(double n) {
        double result = 1;
        for (int i = 1; i <= n; i++) {
            result *= i;
        }
        return result;
    }

    public static double sin(double x, int numTerms) {
        x = x % (2 * 3.141592653589793);
        double result = 0;
        for (int n = 0; n < numTerms; n++) {
            double term = Math.pow(-1, n) * Math.pow(x, 2 * n + 1) / factorial(2 * n + 1);
            result += term;
        }
        return result;
    }

    public static double cos(double x, int numTerms) {
        x = x % (2 * 3.141592653589793);
        double result = 0;
        for (int n = 0; n < numTerms; n++) {
            double term = Math.pow(-1, n) * Math.pow(x, 2 * n) / factorial(2 * n);
            result += term;
        }
        return result;
    }

    public static double exp(double x, int numTerms) {
        double result = 0;
        for (int n = 0; n < numTerms; n++) {
            double term = Math.pow(x, n) / factorial(n);
            result += term;
        }
        return result;
    }

    public static double log(double x, double tolerance, int maxIterations) {
        if (x <= 0) {
            throw new IllegalArgumentException("对数的输入必须大于 0");
        }
        double y = 1;  // 初始猜测值
        for (int i = 0; i < maxIterations; i++) {
            double f = exp(y) - x;
            double f_prime = exp(y);
            double y_new = y - f / f_prime;
            if (Math.abs(y_new - y) < tolerance) {
                return y_new;
            }
            y = y_new;
        }
        throw new IllegalArgumentException("未能在最大迭代次数内收敛");
    }

    public static double d_sin(double x) {
        /**计算 sin(x) 的导数*/
        return cos(x, 10);
    }

    public static double d_cos(double x) {
        /**计算 cos(x) 的导数*/
        return -sin(x, 10);
    }

    public static double tan(double x) {
        double cosVal = cos(x, 10);
        if (cosVal == 0) {
            throw new IllegalArgumentException("tan(x) 在 cos(x)=0 处无定义");
        }
        return sin(x, 10) / cosVal;
    }

    public static double d_tan(double x) {
        double cosVal = cos(x, 10);
        return 1 / (cosVal * cosVal);
    }

    public static double sinh(double x, int numTerms) {
        double result = 0;
        for (int n = 0; n < numTerms; n++) {
            double term = Math.pow(x, 2 * n + 1) / factorial(2 * n + 1);
            result += term;
        }
        return result;
    }

    public static double cosh(double x, int numTerms) {
        double result = 0;
        for (int n = 0; n < numTerms; n++) {
            double term = Math.pow(x, 2 * n) / factorial(2 * n);
            result += term;
        }
        return result;
    }

    public static double tanh(double x) {
        double sinhVal = sinh(x, 10);
        double coshVal = cosh(x, 10);
        return sinhVal / coshVal;
    }

    public static double evaluateExpression(String expression) {
        java.util.StringTokenizer tokens = new java.util.StringTokenizer(expression, "+-*/()sincoslogd_sind_costand_tansinhcoshtanh! ", true);
        java.util.Stack<Double> values = new java.util.Stack<>();
        java.util.Stack<String> operators = new java.util.Stack<>();

        while (tokens.hasMoreTokens()) {
            String token = tokens.nextToken().trim();
            if (token.isEmpty()) {
                continue;
            }

            if (token.matches("\\d+(\\.\\d+)?")) {
                values.push(Double.parseDouble(token));
            } else if (token.equals("(")) {
                operators.push(token);
            } else if (token.equals(")")) {
                while (!operators.isEmpty() && !operators.peek().equals("(")) {
                    values.push(applyOperation(operators.pop(), values.pop(), values.isEmpty() ? null : values.pop()));
                }
                operators.pop();
            } else if (isOperator(token)) {
                while (!operators.isEmpty() && hasPrecedence(token, operators.peek())) {
                    values.push(applyOperation(operators.pop(), values.pop(), values.isEmpty() ? null : values.pop()));
                }
                operators.push(token);
            } else if (token.equals("sin") || token.equals("cos") || token.equals("log") || token.equals("!") ||
                    token.equals("d_sin") || token.equals("d_cos") || token.equals("tan") || token.equals("d_tan") ||
                    token.equals("sinh") || token.equals("cosh") || token.equals("tanh")) {
                operators.push(token);
            }
        }

        while (!operators.isEmpty()) {
            values.push(applyOperation(operators.pop(), values.pop(), values.isEmpty() ? null : values.pop()));
        }

        return values.pop();
    }

    private static boolean isOperator(String token) {
        return token.equals("+") || token.equals("-") || token.equals("*") || token.equals("/");
    }

    private static boolean hasPrecedence(String op1, String op2) {
        if ((op1.equals("+") || op1.equals("-")) && (op2.equals("*") || op2.equals("/"))) {
            return false;
        }
        return true;
    }

    private static double applyOperation(String operator, double b, Double a) {
        switch (operator) {
            case "+":
                return a + b;
            case "-":
                return a - b;
            case "*":
                return a * b;
            case "/":
                if (b == 0) {
                    throw new UnsupportedOperationException("除数不能为零");
                }
                return a / b;
            case "sin":
                return sin(b, 10);
            case "cos":
                return cos(b, 10);
            case "log":
                return log(b, 1e-6, 100);
            case "d_sin":
                return d_sin(b);
            case "d_cos":
                return d_cos(b);
            case "tan":
                return tan(b);
            case "d_tan":
                return d_tan(b);
            case "sinh":
                return sinh(b, 10);
            case "cosh":
                return cosh(b, 10);
            case "tanh":
                return tanh(b);
            case "!":
                return factorial(b);
        }
        return 0;
    }

    public static void main(String[] args) {
        String[] expressions = {
                "sin(3.14 / 2)",
                "cos(0)",
                "5!",
                "log(2.71828)",
                "d_sin(0)",
                "d_cos(3.14 / 2)",
                "tan(0)",
                "d_tan(0)",
                "sinh(1)",
                "cosh(1)",
                "tanh(1)"
        };

        for (String expr : expressions) {
            try {
                double result = evaluateExpression(expr);
                System.out.printf("%s = %f%n", expr, result);
            } catch (Exception e) {
                System.out.printf("表达式 %s 计算出错: %s%n", expr, e.getMessage());
            }
        }
    }
}"""


class image:
    """对图像的处理"""
    def crop_image(input_path, output_path, left, top, right, bottom):
        """"""
        # 打开图像文件
        try:
            image = Image.open(input_path)
        except Exception as e:
            print(f"打开图像时出错: {e}")
            return

        # 裁剪图像
        cropped_image = image.crop((left, top, right, bottom))

        # 保存裁剪后的图像
        cropped_image.save(output_path)

    class Bmp:
        """对bmp文件的设置"""
        def read_bmp(file_path):
            with open(file_path, 'rb') as bmp_file:
                bmp_data = bmp_file.read()
            return bmp_data

        def crop_bmp(bmp_data, x, y, width, height):
            # BMP 文件头大小
            bmp_header_size = 54
            pixel_array_offset = int.from_bytes(bmp_data[10:14], 'little')
            bmp_width = int.from_bytes(bmp_data[18:22], 'little')
            bmp_height = int.from_bytes(bmp_data[22:26], 'little')
            bpp = int.from_bytes(bmp_data[28:30], 'little') // 8  # 每个像素的字节数

            # 验证裁剪参数是否有效
            if x < 0 or y < 0 or x + width > bmp_width or y + height > bmp_height:
                raise ValueError("裁剪参数超出图像范围")

            cropped_data = bytearray(bmp_data[:bmp_header_size])  # 复制 BMP 头部
            cropped_data[18:22] = (width).to_bytes(4, 'little')       # 更新宽度
            cropped_data[22:26] = (height).to_bytes(4, 'little')      # 更新高度
            row_size = ((bmp_width * bpp + 3) & ~3)                    # 行填充
            cropped_row_size =((width * bpp + 3) & ~3)                  # 新行填充

            # 逐行复制数据
            for h in range(height):
                for w in range(width):
                    pixel_index = pixel_array_offset + ((y + h) * row_size) + ((x + w) * bpp)
                    cropped_data.extend(bmp_data[pixel_index:pixel_index + bpp])

                # 添加填充字节
                cropped_data.extend(b'\x00' * (cropped_row_size - (width * bpp)))

            return bytes(cropped_data)

        def save_bmp(cropped_bmp, output_path):
            with open(output_path, 'wb') as f:
                f.write(cropped_bmp)


print('Hello! hyypns 0.1.4 ('+version,'',timecur(),getcwd(),
      desktop()+')')

#print('users:',users())

sleep(0.5)


class Screen:
    """鼠标和键盘的操作(Windows)"""
    global user32, MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP, MOUSEEVENTF_MOVE
    global VK_SHIFT, VK_CONTROL, VK_RETURN, KEYEVENTF_KEYUP, MOUSEEVENTF_RIGHTDOWN
    global move, MOUSEEVENTF_RIGHTUP, key_mapping
    # 定义一些 Windows API 常量和函数
    user32 = ctypes.windll.user32


    # 鼠标事件常量
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_MOVE = 0x0001
    MOUSEEVENTF_RIGHTDOWN = 0x0008
    MOUSEEVENTF_RIGHTUP = 0x0010


    # 键盘事件常量
    VK_SHIFT = 0x10
    VK_CONTROL = 0x11
    VK_RETURN = 0x0D
    KEYEVENTF_KEYUP = 0x0002

    # 键名到键码的映射字典
    key_mapping = {
    # 字母键
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45, 'f': 0x46, 'g': 0x47,
    'h': 0x48, 'i': 0x49, 'j': 0x4A, 'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E,
    'o': 0x4F, 'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54, 'u': 0x55,
    'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59, 'z': 0x5A,
    # 数字键（主键盘区）
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34, '5': 0x35, '6': 0x36,
    '7': 0x37, '8': 0x38, '9': 0x39,
    # 数字小键盘区
    'numlock': 0x90,
    'kp0': 0x60, 'kp1': 0x61, 'kp2': 0x62, 'kp3': 0x63, 'kp4': 0x64,
    'kp5': 0x65, 'kp6': 0x66, 'kp7': 0x67, 'kp8': 0x68, 'kp9': 0x69,
    'kp.': 0x6E, 'kp+': 0x6B, 'kp-': 0x6D, 'kp*': 0x6A, 'kp/': 0x6F,
    # 功能键
    'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73, 'f5': 0x74,
    'f6': 0x75, 'f7': 0x76, 'f8': 0x77, 'f9': 0x78, 'f10': 0x79,
    'f11': 0x7A, 'f12': 0x7B, 'f13': 0x7C, 'f14': 0x7D, 'f15': 0x7E,
    'f16': 0x7F, 'f17': 0x80, 'f18': 0x81, 'f19': 0x82, 'f20': 0x83,
    'f21': 0x84, 'f22': 0x85, 'f23': 0x86, 'f24': 0x87,
    # 控制键
    'esc': 0x1B, 'backspace': 0x08, 'tab': 0x09, 'enter': 0x0D,
    'shift': 0x10, 'lshift': 0xA0, 'rshift': 0xA1,
    'ctrl': 0x11, 'lctrl': 0xA2, 'rctrl': 0xA3,
    'alt': 0x12, 'lalt': 0xA4, 'ralt': 0xA5,
    'capslock': 0x14, 'numlock': 0x90, 'scrolllock': 0x91,
    'insert': 0x2D, 'delete': 0x2E, 'home': 0x24, 'lwin': 0x5B,
    'rwin': 0x5C, 'win': 0x5B
    }



    def click_cur(button="left", delay = 0.1):
        """
        模拟鼠标在当前位置进行点击操作
        :param button: 点击的按钮，可选值为 "left" 或 "right"，默认为 "left"
        :param delay: 延时的时间，可填数字
        """

        if button == "left":
            # 模拟鼠标左键按下事件
            user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            # 稍微延迟一下，以模拟真实的点击操作
            time.sleep(delay)
            # 模拟鼠标左键释放事件
            user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

        elif button == "right":
            # 模拟鼠标右键按下事件
            user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            # 稍微延迟一下，以模拟真实的点击操作
            time.sleep(delay)
            # 模拟鼠标右键释放事件
            user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

        else:
            print("无效的按钮选择，请输入 'left' 或 'right'。")

    # 记录鼠标位置
    def mouse():
        """记录鼠标位置"""
        point = ctypes.wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(point))
        return point.x, point.y


    # 鼠标移动到指定位置
    def move(x, y):
        """鼠标移动到指定位置"""
        user32.SetCursorPos(x, y)


    # 鼠标点击
    def click(x, y, button, delay = 0.1):
        """鼠标点击"""
        move(x,y)
        time.sleep(delay)
        if button == 'left':
            user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(delay)
            user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

        elif button == 'right':
            user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(delay)
            user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)


    # 键盘输入单个键
    def press(key_name):
        """
        根据键名模拟键盘按键按下和释放操作
        :param key_name: 键名，如 'a', 'enter', 'space' 等
        """
        key_code = key_mapping.get(key_name.lower())
        if key_code is None:
            print(f"无效的键名: {key_name}")
            return
        # 模拟按键按下
        user32.keybd_event(key_code, 0, 0, 0)
        time.sleep(0.1)
        # 模拟按键释放
        user32.keybd_event(key_code, 0, KEYEVENTF_KEYUP, 0)



    # 键盘输入组合键
    def press_keys(key_names):
        """
        根据键名列表模拟键盘组合键操作
        :param key_names: 键名列表，如 ['ctrl', 'c']
        """
        key_codes = []
        for key_name in key_names:
            key_code = key_mapping.get(key_name.lower())
            if key_code is None:
                print(f"无效的键名: {key_name}")
                return
            key_codes.append(key_code)

        for key_code in key_codes:
            user32.keybd_event(key_code, 0, 0, 0)
        time.sleep(0.1)
        for key_code in reversed(key_codes):
            user32.keybd_event(key_code, 0, KEYEVENTF_KEYUP, 0)


class Count:
    """进行计算"""
    global sin, cos, factorial, exp, cosh, sinh
    global log, d_tan, d_cos, d_sin, tan, tanh

    def factorial(n):
        """计算阶乘"""
        if not isinstance(n, int) or n < 0:
            raise ValueError("阶乘的输入必须是一个非负整数")
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result


    def sin(x, num_terms=10):
        """使用泰勒级数展开计算 sin(x)"""
        try:
            x = x % (2 * 3.141592653589793)
            result = 0
            for n in range(num_terms):
                term = ((-1) ** n) * (x ** (2 * n + 1)) / factorial(2 * n + 1)
                result += term
            return result
        except OverflowError:
            raise ValueError("计算 sin(x) 时发生溢出错误，请检查输入值或减少项数")


    def cos(x, num_terms=10):
        """使用泰勒级数展开计算 cos(x)"""
        try:
            x = x % (2 * 3.141592653589793)
            result = 0
            for n in range(num_terms):
                term = ((-1) ** n) * (x ** (2 * n)) / factorial(2 * n)
                result += term
            return result
        except OverflowError:
            raise ValueError("计算 cos(x) 时发生溢出错误，请检查输入值或减少项数")


    def exp(x, num_terms=10):
        """使用泰勒级数展开计算 e^x"""
        try:
            result = 0
            for n in range(num_terms):
                term = (x ** n) / factorial(n)
                result += term
            return result
        except OverflowError:
            raise ValueError("计算 exp(x) 时发生溢出错误，请检查输入值或减少项数")


    def log(x, tolerance=1e-6, max_iterations=100):
        """使用牛顿 - 拉夫逊方法计算自然对数 ln(x)"""
        if x <= 0:
            raise ValueError("对数的输入必须大于 0")
        y = 1  # 初始猜测值
        for _ in range(max_iterations):
            try:
                f = exp(y) - x
                f_prime = exp(y)
                y_new = y - f / f_prime
                if abs(y_new - y) < tolerance:
                    return y_new
                y = y_new
            except OverflowError:
                raise ValueError("计算 log(x) 时发生溢出错误，请检查输入值或调整迭代参数")
        raise ValueError("未能在最大迭代次数内收敛，请检查输入值或调整迭代参数")


    def d_sin(x):
        """计算 sin(x) 的导数"""
        try:
            return cos(x)
        except ValueError as e:
            raise ValueError(f"计算 d_sin(x) 时出错: {e}")


    def d_cos(x):
        """计算 cos(x) 的导数"""
        try:
            return -sin(x)
        except ValueError as e:
            raise ValueError(f"计算 d_cos(x) 时出错: {e}")


    def tan(x):
        """计算 tan(x)"""
        cos_val = cos(x)
        if cos_val == 0:
            raise ValueError("tan(x) 在 cos(x)=0 处无定义")
        return sin(x) / cos_val


    def d_tan(x):
        """计算 tan(x) 的导数"""
        try:
            cos_val = cos(x)
            if cos_val == 0:
                raise ValueError("d_tan(x) 在 cos(x)=0 处无定义")
            return 1 / (cos_val ** 2)
        except ValueError as e:
            raise ValueError(f"计算 d_tan(x) 时出错: {e}")


    def sinh(x, num_terms=10):
        """使用泰勒级数展开计算双曲正弦函数 sinh(x)"""
        try:
            result = 0
            for n in range(num_terms):
                term = (x ** (2 * n + 1)) / factorial(2 * n + 1)
                result += term
            return result
        except OverflowError:
            raise ValueError("计算 sinh(x) 时发生溢出错误，请检查输入值或减少项数")


    def cosh(x, num_terms=10):
        """使用泰勒级数展开计算双曲余弦函数 cosh(x)"""
        try:
            result = 0
            for n in range(num_terms):
                term = (x ** (2 * n)) / factorial(2 * n)
                result += term
            return result
        except OverflowError:
            raise ValueError("计算 cosh(x) 时发生溢出错误，请检查输入值或减少项数")


    def tanh(x):
        """计算双曲正切函数 tanh(x)"""
        try:
            sinh_val = sinh(x)
            cosh_val = cosh(x)
            return sinh_val / cosh_val
        except ValueError as e:
            raise ValueError(f"计算 tanh(x) 时出错: {e}")


    def pi(iterations):
        """
        计算圆周率
        iterations:到多少位(最高1076)
        """
        getcontext().prec = 1000
        sum_series = Decimal(0)
        for k in range(iterations):
            numerator = Decimal(math.factorial(4 * k)) * (Decimal(1103) + Decimal(26390 * k))
            denominator = (Decimal(math.factorial(k)) ** 4) * (Decimal(396) ** (4 * k))
            term = numerator / denominator
            sum_series += term
        constant = (Decimal(2) * Decimal(2).sqrt()) / Decimal(9801)
        pi = 1 / (constant * sum_series)
        return pi


    def evaluate_expression(expression):
        """计算表达式的值"""
        try:
            # 定义自定义函数和常量
            local_vars = {
                'sin': sin,
                'cos': cos,
                'factorial': factorial,
                'log': log,
                'd_sin': d_sin,
                'd_cos': d_cos,
                'tan': tan,
                'd_tan': d_tan,
                'sinh': sinh,
                'cosh': cosh,
                'tanh': tanh
            }
            return eval(expression, {"__builtins__": None}, local_vars)
        except SyntaxError:
            print(f"表达式 '{expression}' 语法错误，请检查表达式格式。")
        except ValueError as e:
            print(f"计算表达式 '{expression}' 时发生值错误: {e}")
        except Exception as e:
            print(f"计算表达式 '{expression}' 时发生未知错误: {e}")
        return None


    # 示例表达式
    expressions = [
        "sin(3.14 / 2)",
        "cos(0)",
        "factorial(5)",
        "log(2.71828)",
        "d_sin(0)",
        "d_cos(3.14 / 2)",
        "tan(0)",
        "d_tan(0)",
        "sinh(1)",
        "cosh(1)",
        "tanh(1)",
        # 可能引发错误的表达式
        "factorial(-1)",
        "log(-1)",
        "tan(3.14 / 2)"
    ]


    def java():
        with open('count.java','w',encoding='utf-8') as file:
            file.write(count)

    PI = 3.14159265358979323846264338327950288419716939937510582097494
    459230781640628620899862803482534211706798214808651328230664709384
    460955058223172535940812848111745028410270193852110555964462294895
    493038196442881097566593344612847564823378678316527120190914564856
    692346034861045432664821339360726024914127372458700660631558817488
    152092096282925409171536436789259036001133053054882046652138414695
    194151160943305727036575959195309218611738193261179310511854807446
    237996274956735188575272489122793818301194912983367336244065664308
    602139494639522473719070217986094370277053921717629317675238467481
    846766940513200056812714526356082778577134275778960917363717872146
    8440901224953430146549585371050792279689258923542019956112129021960
    86403441815981362977477130996051870721134999999837297804995105973
    173281609631859502445945534690830264252230825334468503526193118817
    101000313783875288658753320838142061717766914730359825349042875546
    873115956286388235378759375195778185778053217122680661300192787661
    1195909216420182#(pi(1076))


class SimpleContainer:
    def __init__(self, image_name):
        self.image_name = image_name
        self.container_id = None
        self.running = False  # 状态标志

    def create(self):
        """创建一个容器"""
        print(f"创建容器 {self.image_name}...")
        self.container_id = f"container-{self.image_name}-{os.getpid()}"
        print(f"容器 {self.container_id} 已创建.")

    def start(self, command):
        """启动容器并运行指定的命令"""
        if self.container_id:
            print(f"启动容器 {self.container_id}...")
            # 通过 subprocess 调用指定的命令
            try:
                self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                self.running = True
                print(f"容器 {self.container_id} 正在运行, 启动命令: {command}")
            except Exception as e:
                print(f"启动命令失败: {e}")
        else:
            print("请首先创建容器。")

    def stop(self):
        """停止容器"""
        if self.running:
            print(f"停止容器 {self.container_id}...")
            self.process.terminate()  # 有条件地终止进程
            self.process.wait()  # 等待进程结束
            self.running = False
            print(f"容器 {self.container_id} 已停止.")
        else:
            print("容器未在运行.")

    def remove(self):
        """删除容器"""
        if self.container_id:
            print(f"删除容器 {self.container_id}...")
            self.container_id = None
            print("容器已删除.")
        else:
            print("没有可删除的容器.")

    def logs(self):
        """查看当前容器的输出日志"""
        if self.running:
            stdout, stderr = self.process.communicate()
            print("标准输出:", stdout.decode())
            print("错误输出:", stderr.decode())
        else:
            print("容器未运行，无法获取日志.")


if __name__ == '__main__':
    print('当前时间:',timecur())
    default('hyypns','larry3d')
    default('module','larry3d')
    input('hyypns module')
    Screen.press_keys(['win'])