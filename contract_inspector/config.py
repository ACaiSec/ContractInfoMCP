"""
配置管理模块
"""

import os
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """配置管理类"""
    
    def __init__(self):
        # RPC 配置
        self.rpc_url = os.getenv(
            "RPC_URL", 
            "https://mainnet.infura.io/v3/6754eb4efd164b62bb05d6776a921baf"
        )
        
        # Etherscan 配置
        self.etherscan_api_key = os.getenv(
            "ETHERSCAN_API_KEY", 
            "79M3IZ537IW9XIEIE2ERQHKABY5SUQH7VA"
        )
        self.etherscan_base_url = os.getenv(
            "ETHERSCAN_BASE_URL", 
            "https://api.etherscan.io/v2/api"
        )
        
        # 网络配置
        self.chain_id = int(os.getenv("CHAIN_ID", "1"))
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.rate_limit_per_second = int(os.getenv("RATE_LIMIT_PER_SECOND", "4"))
        
    def validate(self) -> bool:
        """验证配置是否有效"""
        if not self.rpc_url:
            raise ValueError("RPC_URL 未配置")
        if not self.etherscan_api_key:
            raise ValueError("ETHERSCAN_API_KEY 未配置")
        return True


# 全局配置实例
config = Config() 