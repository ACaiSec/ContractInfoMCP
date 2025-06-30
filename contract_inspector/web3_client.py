"""
Web3 客户端
"""

import asyncio
from typing import Any, Dict, List, Optional
from web3 import Web3
from web3.exceptions import ContractLogicError, Web3Exception

from .config import config
from .utils import retry_with_backoff, to_checksum_address


class Web3Client:
    """Web3 客户端"""
    
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(config.rpc_url))
        self._connection_verified = False
        
    async def verify_connection(self) -> bool:
        """
        验证与区块链的连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            def check_connection():
                return self.w3.is_connected()
            
            self._connection_verified = await retry_with_backoff(
                check_connection,
                max_retries=3
            )
            
            if self._connection_verified:
                print("✅ Web3 连接成功")
            else:
                print("❌ Web3 连接失败")
            
            return self._connection_verified
            
        except Exception as e:
            print(f"验证 Web3 连接时发生错误: {str(e)}")
            return False
    
    async def is_contract_address(self, address: str) -> bool:
        """
        检查地址是否为合约地址
        
        Args:
            address: 以太坊地址
            
        Returns:
            bool: 是否为合约地址
        """
        try:
            checksum_address = to_checksum_address(address)
            
            def get_code():
                code = self.w3.eth.get_code(checksum_address)
                return len(code) > 0
            
            return await retry_with_backoff(
                get_code,
                max_retries=config.max_retries
            )
            
        except Exception as e:
            print(f"检查合约地址时发生错误: {str(e)}")
            return False
    
    async def get_contract_instance(self, address: str, abi: List[Dict]) -> Optional[Any]:
        """
        获取合约实例
        
        Args:
            address: 合约地址
            abi: 合约 ABI
            
        Returns:
            合约实例或 None
        """
        try:
            checksum_address = to_checksum_address(address)
            
            def create_contract():
                return self.w3.eth.contract(
                    address=checksum_address,
                    abi=abi
                )
            
            return await retry_with_backoff(
                create_contract,
                max_retries=config.max_retries
            )
            
        except Exception as e:
            print(f"创建合约实例时发生错误: {str(e)}")
            return None
    
    async def call_view_function(
        self, 
        contract: Any, 
        function_name: str
    ) -> Dict[str, Any]:
        """
        调用合约的 view 函数
        
        Args:
            contract: 合约实例
            function_name: 函数名称
            
        Returns:
            Dict: 函数调用结果
        """
        try:
            # 获取函数对象
            func = getattr(contract.functions, function_name, None)
            if func is None:
                return {
                    "function_name": function_name,
                    "status": "error",
                    "error": f"函数 {function_name} 不存在"
                }
            
            def call_function():
                return func().call()
            
            result = await retry_with_backoff(
                call_function,
                max_retries=config.max_retries
            )
            
            return {
                "function_name": function_name,
                "result": result,
                "status": "success"
            }
            
        except ContractLogicError as e:
            return {
                "function_name": function_name,
                "status": "error",
                "error": f"合约逻辑错误: {str(e)}"
            }
        except Web3Exception as e:
            return {
                "function_name": function_name,
                "status": "error",
                "error": f"Web3 错误: {str(e)}"
            }
        except Exception as e:
            return {
                "function_name": function_name,
                "status": "error",
                "error": f"未知错误: {str(e)}"
            }
    
    async def batch_call_view_functions(
        self, 
        contract: Any, 
        function_names: List[str]
    ) -> List[Dict[str, Any]]:
        """
        批量调用 view 函数
        
        Args:
            contract: 合约实例
            function_names: 函数名称列表
            
        Returns:
            List[Dict]: 所有函数调用结果
        """
        # 并发调用所有函数
        tasks = [
            self.call_view_function(contract, func_name)
            for func_name in function_names
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "function_name": function_names[i],
                    "status": "error",
                    "error": f"调用异常: {str(result)}"
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def get_block_number(self) -> Optional[int]:
        """
        获取当前区块号
        
        Returns:
            Optional[int]: 区块号
        """
        try:
            def get_latest_block():
                return self.w3.eth.block_number
            
            return await retry_with_backoff(
                get_latest_block,
                max_retries=config.max_retries
            )
            
        except Exception as e:
            print(f"获取区块号时发生错误: {str(e)}")
            return None 