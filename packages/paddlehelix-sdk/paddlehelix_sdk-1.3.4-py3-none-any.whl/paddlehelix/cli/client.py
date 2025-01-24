"""
API客户端
"""
import json
import os
import platform

from paddlehelix.api.api_common import MiddleCommonClient
from paddlehelix.api.api_helixfold3 import MiddleHelixFold3Client, BaseHelixFold3Client

def get_config_file_path():
    """根据操作系统选择合适的配置文件存储路径"""
    system_name = platform.system()

    if system_name == "Windows":
        # Windows: 使用 AppData 目录
        config_dir = os.path.join(os.getenv('APPDATA'), "PaddleHelix")
    else:
        # Linux / macOS: 使用用户主目录下的 .config 目录
        config_dir = os.path.join(os.path.expanduser("~"), ".config", "PaddleHelix")

    os.makedirs(config_dir, exist_ok=True)

    config_file = os.path.join(config_dir, "config.json")
    return config_file

def load_config(config_file):
    """加载配置文件中的 AK 和 SK"""

    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            config = json.load(file)
        return config.get("PADDLEHELIX_API_AK"), config.get("PADDLEHELIX_API_SK")
    return None, None

def save_config(ak, sk, config_file):
    """保存 AK 和 SK 到配置文件"""
    config = {
        "PADDLEHELIX_API_AK": ak,
        "PADDLEHELIX_API_SK": sk
    }

    with open(config_file, "w") as file:
        json.dump(config, file, indent=4)


def get_ak_sk_from_envs():
    """从环境变量中获取 AK 和 SK"""
    return os.getenv("PADDLEHELIX_API_AK"), os.getenv("PADDLEHELIX_API_SK")

_ak, _sk = get_ak_sk_from_envs()
config_file_path = get_config_file_path()

if not _ak or not _sk:
    print("PaddleHelix API Access Key or Secret Key not found in environment variables. Attempting to load from configuration file.")
    _ak, _sk = load_config(config_file_path)

    if _ak is None or _sk is None:
        print("PaddleHelix API Access Key or Secret Key not found in the configuration file. Please enter them manually.")
        _ak = input("Please enter your PaddleHelix API Access Key: ")
        _sk = input("Please enter your PaddleHelix API Secret Key: ")
        save_config(_ak, _sk, config_file_path)
        print(f"The PaddleHelix API Access Key and Secret Key have been saved to the configuration file at {config_file_path}, and will be automatically loaded on the next use.")
    else:
        print("PaddleHelix API Access Key and Secret Key successfully loaded from the configuration file.")

else:
    print("PaddleHelix API Access Key and Secret Key have been successfully loaded from the environment variables.")
    if os.path.exists(config_file_path):
        print('Updating the configuration file.')
    else:
        print(f"The PaddleHelix API Access Key and Secret Key have been saved to the configuration file at {config_file_path}, and will be automatically loaded on the next use.")
    save_config(_ak, _sk, config_file_path)


class APIClient:
    Common = MiddleCommonClient(_ak, _sk)
    MiddleHelixFold = MiddleHelixFold3Client(_ak, _sk)


