"""
工具函数模块
"""

import re
import json
import asyncio
from typing import Any, Dict, List, Optional
from web3 import Web3


def is_valid_ethereum_address(address: str) -> bool:
    """
    验证以太坊地址格式是否有效
    
    Args:
        address: 以太坊地址字符串
        
    Returns:
        bool: 地址是否有效
    """
    if not address:
        return False
    
    # 检查是否以 0x 开头且长度为 42
    if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
        return False
    
    return True


def is_checksum_address(address: str) -> bool:
    """
    验证地址是否为有效的校验和地址
    
    Args:
        address: 以太坊地址字符串
        
    Returns:
        bool: 是否为有效的校验和地址
    """
    try:
        return Web3.is_checksum_address(address)
    except Exception:
        return False


def to_checksum_address(address: str) -> str:
    """
    将地址转换为校验和格式
    
    Args:
        address: 以太坊地址字符串
        
    Returns:
        str: 校验和格式的地址
    """
    try:
        return Web3.to_checksum_address(address)
    except Exception:
        return address


def format_wei_value(value: int, decimals: int = 18) -> str:
    """
    格式化 Wei 值为可读的小数格式
    
    Args:
        value: Wei 值
        decimals: 小数位数，默认18
        
    Returns:
        str: 格式化后的数值字符串
    """
    try:
        if value == 0:
            return "0"
        
        divisor = 10 ** decimals
        result = value / divisor
        
        # 移除尾随零
        formatted = f"{result:.{decimals}f}".rstrip('0').rstrip('.')
        return formatted if formatted else "0"
    except Exception:
        return str(value)


def safe_json_loads(data: str) -> Optional[Any]:
    """
    安全的 JSON 解析
    
    Args:
        data: JSON 字符串
        
    Returns:
        解析后的数据或 None
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return None


def extract_view_functions(abi: List[Dict]) -> List[Dict]:
    """
    从 ABI 中提取无参数的 view 函数
    
    Args:
        abi: 合约 ABI 列表
        
    Returns:
        List[Dict]: 符合条件的函数列表
    """
    view_functions = []
    
    for item in abi:
        if (
            item.get("type") == "function" and
            item.get("stateMutability") in ["view", "pure"] and
            len(item.get("inputs", [])) == 0
        ):
            view_functions.append(item)
    
    return view_functions


def format_function_result(func_name: str, result: Any, output_type: str) -> Dict[str, Any]:
    """
    格式化函数调用结果
    
    Args:
        func_name: 函数名称
        result: 函数返回值
        output_type: 返回值类型
        
    Returns:
        Dict: 格式化后的结果
    """
    formatted_result = {
        "function_name": func_name,
        "result": result,
        "type": output_type,
        "status": "success"
    }
    
    # 对特定类型进行格式化
    if output_type.startswith("uint") and isinstance(result, int):
        formatted_result["formatted_value"] = format_wei_value(result) if "256" in output_type else str(result)
    elif output_type == "address" and isinstance(result, str):
        formatted_result["checksum_address"] = to_checksum_address(result)
    elif output_type == "bool":
        formatted_result["result"] = bool(result)
    
    return formatted_result


async def retry_with_backoff(
    func, 
    max_retries: int = 3, 
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    *args, 
    **kwargs
) -> Any:
    """
    带指数退避的重试机制
    
    Args:
        func: 要重试的函数
        max_retries: 最大重试次数
        base_delay: 基础延迟时间（秒）
        backoff_factor: 退避因子
        *args, **kwargs: 传递给函数的参数
        
    Returns:
        函数执行结果
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            if attempt == max_retries:
                break
                
            delay = base_delay * (backoff_factor ** attempt)
            await asyncio.sleep(delay)
    
    raise last_exception


def truncate_string(text: str, max_length: int = 100) -> str:
    """
    截断字符串到指定长度
    
    Args:
        text: 原始字符串
        max_length: 最大长度
        
    Returns:
        str: 截断后的字符串
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..." 