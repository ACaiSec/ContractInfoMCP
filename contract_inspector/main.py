"""
Contract Inspector MCP Server - 使用 FastMCP
根据官方规范编写的 EVM 合约信息查询工具
"""

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import json
import os
import asyncio
from .contract_analyzer import ContractAnalyzer
from .config import config

# 加载环境变量
load_dotenv()

# 创建 FastMCP 实例
mcp = FastMCP("contract-inspector")

# 初始化合约分析器
analyzer = ContractAnalyzer()


@mcp.tool()
async def contract_info(contract_address: str):
    """
    获取 EVM 合约的完整链上信息，包括调用所有无参数的 view 函数
    
    Args:
        contract_address: EVM 合约地址 (0x开头的42位十六进制字符串)
    
    Returns:
        合约的详细信息，包括基础信息和所有view函数的调用结果
    """
    # 验证合约地址格式
    if not contract_address or not isinstance(contract_address, str):
        raise ValueError("合约地址不能为空且必须是字符串")
    
    if not contract_address.startswith("0x") or len(contract_address) != 42:
        raise ValueError("合约地址格式无效，必须是0x开头的42位十六进制字符串")
    
    try:
        print(f"🔍 开始分析合约: {contract_address}")
        
        # 执行合约分析
        result = await analyzer.analyze_contract(contract_address)
        
        # 格式化输出
        formatted_result = json.dumps(result, ensure_ascii=False, indent=2)
        
        print(f"✅ 合约分析完成: {contract_address}")
        
        return formatted_result
        
    except Exception as e:
        error_msg = f"合约分析失败: {str(e)}"
        print(f"❌ {error_msg}")
        
        error_response = {
            "status": "error",
            "error": error_msg,
            "contract_address": contract_address,
            "tool": "contract_info"
        }
        
        return json.dumps(error_response, ensure_ascii=False, indent=2)


@mcp.tool()
async def contract_summary(contract_address: str):
    """
    获取合约基本摘要信息，不调用合约函数，快速获取合约概况
    
    Args:
        contract_address: EVM 合约地址 (0x开头的42位十六进制字符串)
    
    Returns:
        合约的基本摘要信息
    """
    # 验证合约地址格式
    if not contract_address or not isinstance(contract_address, str):
        raise ValueError("合约地址不能为空且必须是字符串")
    
    if not contract_address.startswith("0x") or len(contract_address) != 42:
        raise ValueError("合约地址格式无效，必须是0x开头的42位十六进制字符串")
    
    try:
        print(f"📋 获取合约摘要: {contract_address}")
        
        # 获取合约摘要
        result = await analyzer.get_contract_summary(contract_address)
        
        # 格式化输出
        formatted_result = json.dumps(result, ensure_ascii=False, indent=2)
        
        print(f"✅ 合约摘要获取完成: {contract_address}")
        
        return formatted_result
        
    except Exception as e:
        error_msg = f"获取合约摘要失败: {str(e)}"
        print(f"❌ {error_msg}")
        
        error_response = {
            "status": "error",
            "error": error_msg,
            "contract_address": contract_address,
            "tool": "contract_summary"
        }
        
        return json.dumps(error_response, ensure_ascii=False, indent=2)


def main():
    """主入口函数"""
    print("🚀 启动 Contract Inspector MCP 服务器 (FastMCP)...")
    print(f"📡 RPC URL: {config.rpc_url}")
    print(f"🔑 Etherscan API: {config.etherscan_base_url}")
    print(f"⛓️  Chain ID: {config.chain_id}")
    print("=" * 50)
    
    try:
        # 验证配置
        config.validate()
        print("✅ 配置验证通过")
        
        # 运行 FastMCP 服务器
        mcp.run(transport="stdio")
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main() 