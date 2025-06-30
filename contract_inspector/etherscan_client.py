"""
Etherscan API 客户端
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
import requests
from asyncio_throttle import Throttler

from .config import config
from .utils import safe_json_loads, retry_with_backoff


class EtherscanClient:
    """Etherscan API 客户端"""
    
    def __init__(self):
        self.base_url = config.etherscan_base_url
        self.api_key = config.etherscan_api_key
        self.timeout = config.request_timeout
        self.throttler = Throttler(rate_limit=config.rate_limit_per_second, period=1)
        
    async def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        发起 HTTP 请求
        
        Args:
            params: 请求参数
            
        Returns:
            Dict: 响应数据
        """
        async with self.throttler:
            # 添加 API key 和 chainid
            params.update({
                "apikey": self.api_key,
                "chainid": config.chain_id
            })
            
            def make_sync_request():
                response = requests.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            
            return await retry_with_backoff(
                make_sync_request,
                max_retries=config.max_retries
            )
    
    async def get_contract_abi(self, contract_address: str) -> Optional[List[Dict]]:
        """
        获取合约 ABI
        
        Args:
            contract_address: 合约地址
            
        Returns:
            Optional[List[Dict]]: 合约 ABI 或 None
        """
        try:
            params = {
                "module": "contract",
                "action": "getabi",
                "address": contract_address
            }
            
            response = await self._make_request(params)
            
            if response.get("status") != "1":
                print(f"获取 ABI 失败: {response.get('message', '未知错误')}")
                return None
            
            abi_string = response.get("result", "")
            if not abi_string:
                print("ABI 数据为空")
                return None
            
            # 解析 ABI JSON
            abi = safe_json_loads(abi_string)
            if not isinstance(abi, list):
                print("ABI 格式无效")
                return None
            
            return abi
            
        except Exception as e:
            print(f"获取合约 ABI 时发生错误: {str(e)}")
            return None
    
    async def get_contract_source_code(self, contract_address: str) -> Optional[Dict[str, Any]]:
        """
        获取合约源代码信息
        
        Args:
            contract_address: 合约地址
            
        Returns:
            Optional[Dict]: 合约源代码信息
        """
        try:
            params = {
                "module": "contract",
                "action": "getsourcecode",
                "address": contract_address
            }
            
            response = await self._make_request(params)
            
            if response.get("status") != "1":
                print(f"获取源代码失败: {response.get('message', '未知错误')}")
                return None
            
            result = response.get("result", [])
            if not result or not isinstance(result, list):
                return None
            
            return result[0] if result else None
            
        except Exception as e:
            print(f"获取合约源代码时发生错误: {str(e)}")
            return None
    
    async def is_contract_verified(self, contract_address: str) -> bool:
        """
        检查合约是否已验证
        
        Args:
            contract_address: 合约地址
            
        Returns:
            bool: 是否已验证
        """
        try:
            source_info = await self.get_contract_source_code(contract_address)
            if not source_info:
                return False
            
            # 检查是否有源代码或 ABI
            has_source = bool(source_info.get("SourceCode", "").strip())
            has_abi = bool(source_info.get("ABI", "").strip())
            
            return has_source or has_abi
            
        except Exception:
            return False
    
    async def get_contract_name(self, contract_address: str) -> Optional[str]:
        """
        获取合约名称
        
        Args:
            contract_address: 合约地址
            
        Returns:
            Optional[str]: 合约名称
        """
        try:
            source_info = await self.get_contract_source_code(contract_address)
            if not source_info:
                return None
            
            return source_info.get("ContractName", "").strip() or None
            
        except Exception:
            return None 