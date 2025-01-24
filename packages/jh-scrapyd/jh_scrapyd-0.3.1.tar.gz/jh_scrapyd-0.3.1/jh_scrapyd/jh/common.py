import json
import platform
import psutil
import os


def platform_os() -> str:
    """Get platform"""
    system = platform.system()
    if system == 'Linux':
        return 'linux'
    elif system == 'Darwin':
        return 'mac os'
    elif system == 'Windows':
        return 'windows'


def is_windows() -> bool:
    """Is it a Windows environment"""
    return platform_os() == 'windows'


def str_decode(b: str):
    """String decoding"""
    if isinstance(b, bytes):
        return b.decode('utf-8', errors='ignore')
    else:
        return str(b)


def data_encode(input_dict: dict):
    """Encode data into JSON format"""
    if not input_dict:
        return None
    return json.dumps(input_dict)


def data_decode(input_dict: str):
    """Decoding JSON formatted data"""
    if not input_dict:
        return None
    return json.loads(input_dict)


def process_dict_recursively(data, process_fn, parent_key=None, **kwargs):
    """
    Recursively process each element in a dictionary.

    :param data: The dictionary to process.
    :param process_fn: A function that takes a key and value as arguments and performs some operation.
    :param parent_key: The key of the parent element in case of nested dictionaries.
    :param kwargs: Any parameter.
    :return: A new dictionary with the processed elements.
    """
    if isinstance(data, dict):
        return {k: process_dict_recursively(v, process_fn, k, **kwargs) for k, v in data.items()}
    elif isinstance(data, list):
        return [process_dict_recursively(element, process_fn, parent_key, **kwargs) for element in data]
    else:
        return process_fn(parent_key, data, **kwargs)


def kill_process(pid, sig):
    """ 杀掉进程 """
    if is_windows():
        # 在 Windows 上使用 taskkill
        try:
            os.system(f"taskkill /pid {pid} /f")
            return True
        except Exception:
            return False
    else:
        # 在 Unix 上使用 os.kill
        try:
            os.kill(pid, sig)
            return True
        except OSError as e:
            return False


def is_process_running(pid):
    """ 判读进程是否存活 """
    try:
        psutil.Process(pid)
        return True
    except psutil.NoSuchProcess:
        return False
