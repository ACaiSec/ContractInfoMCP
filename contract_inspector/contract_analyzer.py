"""
合约分析器 - 核心业务逻辑
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from .etherscan_client import EtherscanClient
from .web3_client import Web3Client
from .utils import (
    is_valid_ethereum_address, 
    to_checksum_address, 
    extract_view_functions,
    format_function_result
)


class ContractAnalyzer:
    """合约分析器"""
    
    def __init__(self):
        self.etherscan_client = EtherscanClient()
        self.web3_client = Web3Client()
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        初始化分析器
        
        Returns:
            bool: 初始化是否成功
        """
        if self._initialized:
            return True
        
        # 验证 Web3 连接
        connection_ok = await self.web3_client.verify_connection()
        if not connection_ok:
            print("❌ Web3 连接失败，无法继续")
            return False
        
        self._initialized = True
        print("✅ 合约分析器初始化成功")
        return True
    
    async def analyze_contract(self, contract_address: str) -> Dict[str, Any]:
        """
        分析合约信息 - 主要业务逻辑
        
        Args:
            contract_address: 合约地址
            
        Returns:
            Dict: 分析结果
        """
        # 初始化检查
        if not await self.initialize():
            return {
                "status": "error",
                "error": "分析器初始化失败",
                "timestamp": datetime.now().isoformat()
            }
        
        # 步骤1: 验证地址格式
        if not is_valid_ethereum_address(contract_address):
            return {
                "status": "error",
                "error": f"无效的以太坊地址格式: {contract_address}",
                "timestamp": datetime.now().isoformat()
            }
        
        # 转换为校验和格式
        checksum_address = to_checksum_address(contract_address)
        
        # 步骤2: 检查是否为合约地址
        is_contract = await self.web3_client.is_contract_address(checksum_address)
        if not is_contract:
            return {
                "status": "error",
                "error": f"地址 {checksum_address} 不是合约地址",
                "timestamp": datetime.now().isoformat()
            }
        
        # 步骤3: 从 Etherscan 获取合约 ABI
        print(f"📡 正在获取合约 {checksum_address} 的 ABI...")
        abi = await self.etherscan_client.get_contract_abi(checksum_address)
        if not abi:
            return {
                "status": "error",
                "error": f"无法获取合约 ABI，可能合约未验证",
                "contract_address": checksum_address,
                "timestamp": datetime.now().isoformat()
            }
        
        # 步骤4: 筛选无参数的 view 函数
        view_functions = extract_view_functions(abi)
        if not view_functions:
            return {
                "status": "warning",
                "message": "合约中没有找到无参数的 view 函数",
                "contract_address": checksum_address,
                "total_functions": len([f for f in abi if f.get("type") == "function"]),
                "timestamp": datetime.now().isoformat()
            }
        
        print(f"🔍 找到 {len(view_functions)} 个无参数的 view 函数")
        
        # 步骤5: 创建合约实例
        contract = await self.web3_client.get_contract_instance(checksum_address, abi)
        if not contract:
            return {
                "status": "error",
                "error": "创建合约实例失败",
                "contract_address": checksum_address,
                "timestamp": datetime.now().isoformat()
            }
        
        # 步骤6: 批量调用 view 函数
        function_names = [func["name"] for func in view_functions]
        print(f"🚀 正在调用 {len(function_names)} 个函数...")
        
        call_results = await self.web3_client.batch_call_view_functions(
            contract, function_names
        )
        
        # 步骤7: 处理和格式化结果
        successful_calls = []
        failed_calls = []
        
        for i, result in enumerate(call_results):
            if result["status"] == "success":
                # 获取函数的输出类型信息
                func_info = view_functions[i]
                output_type = self._get_output_type(func_info)
                
                formatted_result = {
                    "function_name": result["function_name"],
                    "result": result["result"],
                    "type": output_type,
                    "status": "success"
                }
                
                # 格式化特殊类型的值
                if output_type.startswith("uint") and isinstance(result["result"], int):
                    if result["result"] > 10**15:  # 可能是 wei 值
                        formatted_result["formatted_value"] = self._format_large_number(result["result"])
                elif output_type == "address":
                    formatted_result["checksum_address"] = to_checksum_address(str(result["result"]))
                
                successful_calls.append(formatted_result)
            else:
                failed_calls.append({
                    "function_name": result["function_name"],
                    "error": result.get("error", "未知错误"),
                    "status": "failed"
                })
        
        # 获取额外的合约信息
        contract_name = await self.etherscan_client.get_contract_name(checksum_address)
        
        # 组装最终结果
        final_result = {
            "status": "success",
            "contract_address": checksum_address,
            "contract_name": contract_name,
            "analysis_summary": {
                "total_view_functions": len(view_functions),
                "successful_calls": len(successful_calls),
                "failed_calls": len(failed_calls)
            },
            "successful_functions": successful_calls,
            "failed_functions": failed_calls if failed_calls else None,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"✅ 分析完成: 成功调用 {len(successful_calls)} 个函数，失败 {len(failed_calls)} 个")
        
        return final_result
    
    def _get_output_type(self, func_info: Dict) -> str:
        """
        获取函数输出类型
        
        Args:
            func_info: 函数信息
            
        Returns:
            str: 输出类型
        """
        outputs = func_info.get("outputs", [])
        if not outputs:
            return "void"
        
        if len(outputs) == 1:
            return outputs[0].get("type", "unknown")
        else:
            return "tuple"
    
    def _format_large_number(self, value: int) -> str:
        """
        格式化大数值
        
        Args:
            value: 数值
            
        Returns:
            str: 格式化后的字符串
        """
        if value >= 10**18:
            return f"{value / 10**18:.6f} Ether"
        elif value >= 10**15:
            return f"{value / 10**15:.6f} milli-Ether"
        elif value >= 10**12:
            return f"{value / 10**12:.6f} micro-Ether"
        else:
            return str(value)
    
    async def get_contract_summary(self, contract_address: str) -> Dict[str, Any]:
        """
        获取合约基本信息摘要
        
        Args:
            contract_address: 合约地址
            
        Returns:
            Dict: 合约摘要信息
        """
        if not is_valid_ethereum_address(contract_address):
            return {"error": "无效的地址格式"}
        
        checksum_address = to_checksum_address(contract_address)
        
        # 基本信息
        summary = {
            "address": checksum_address,
            "is_contract": await self.web3_client.is_contract_address(checksum_address),
            "is_verified": await self.etherscan_client.is_contract_verified(checksum_address),
            "contract_name": await self.etherscan_client.get_contract_name(checksum_address)
        }
        
        return summary 