# Contract Inspector MCP Service

基于 MCP 协议的**本地**以太坊合约信息获取工具，支持在 Cursor 等 AI 工具中使用。采用 **uv** 作为现代化的 Python 项目管理工具。

> **重要说明**：这是一个本地 MCP 服务，Cursor 会自动管理服务的启动和停止，无需用户手动启动服务器。

## 功能

- 🔍 获取 EVM 合约链上信息
- 📊 调用所有无参数 view 函数
- 🌐 整合 Etherscan 和 RPC 数据
- ⚡ 并发处理，性能优化
- 📋 标准 JSON 格式输出

## 环境要求

- Python 3.10+ 
- uv 包管理器

## 快速开始

### 1. 安装 uv（如果尚未安装）

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

### 2. 设置项目

```bash
# 克隆/进入项目目录
cd ContractInfoMCP

# 创建虚拟环境并安装所有依赖（一键搞定）
uv sync
```

### 3. 配置环境

```bash
# 复制环境变量模板
cp env.example .env

# 编辑 .env 文件，填入您的 API keys
# 需要配置：
# - RPC_URL：您的以太坊 RPC 节点地址（如 Infura、Alchemy 等）
# - ETHERSCAN_API_KEY：您的 Etherscan API 密钥
```

### 4. 完成配置

配置完成后，您只需要在 Cursor 中添加 MCP 配置即可。**无需手动启动任何服务器**，Cursor 会自动管理本地 MCP 服务的生命周期。

## 在 Cursor 中配置

在 Cursor 的 MCP 设置中添加以下配置。**Cursor 会根据此配置自动启动和管理 MCP 服务**。

请将 `<project_path>` 替换为您项目的实际绝对路径：

**macOS/Linux 用户**：
```json
{
  "mcpServers": {
    "contract-inspector": {
      "command": "<project_path>/.venv/bin/python",
      "args": ["-m", "contract_inspector.main"],
      "cwd": "<project_path>"
    }
  }
}
```

**Windows 用户**：
```json
{
  "mcpServers": {
    "contract-inspector": {
      "command": "<project_path>/.venv/Scripts/python.exe",
      "args": ["-m", "contract_inspector.main"],
      "cwd": "<project_path>"
    }
  }
}
```

### 路径配置说明

将 `<project_path>` 替换为您项目的实际绝对路径：

**获取项目路径**：
```bash
# 在项目目录中运行
pwd                # macOS/Linux
echo %cd%          # Windows CMD
echo $PWD          # Windows PowerShell
```

**配置示例**：
- macOS/Linux：`/Users/username/Projects/ContractInfoMCP`
- Windows：`C:\\Users\\username\\Projects\\ContractInfoMCP`

## 使用示例

配置完成后，当您在 Cursor 中首次使用 MCP 工具时，Cursor 会自动启动本地服务。您可以直接在 Cursor 聊天中输入：

```
查询 0xdac17f958d2ee523a2206206994597c13d831ec7 地址的基本信息
```

Cursor 会自动调用相应的 MCP 工具来处理您的请求。

## MCP 工具

### ContractInfo
- **功能**：获取合约完整信息，调用所有不需要参数的 view 函数
- **参数**：`contract_address` (合约地址)
- **输出**：JSON 格式的合约信息和函数调用结果

### ContractSummary  
- **功能**：获取合约基本摘要，不调用函数
- **参数**：`contract_address` (合约地址)
- **输出**：合约基本信息


## 项目结构

```
contract_inspector/
├── main.py              # MCP 服务器入口
├── contract_analyzer.py # 核心分析逻辑  
├── etherscan_client.py  # Etherscan API
├── web3_client.py       # Web3 RPC 客户端
├── config.py            # 配置管理
└── utils.py             # 工具函数
```

## 故障排除

### 常见问题

1. **"uv: command not found"**
   - 安装 uv：`pip install uv`
   - 或访问：https://github.com/astral-sh/uv

2. **"No solution found when resolving dependencies"**
   - 检查 Python 版本是否 >= 3.10
   - 运行：`uv --version` 和 `python --version`

3. **"ModuleNotFoundError: No module named 'contract_inspector'"**
   - 这通常是Cursor没有使用正确的虚拟环境导致的，请执行以下步骤：
   
   ```bash
   # 确保在项目目录中
   cd <project_path>
   
   # 以可编辑模式重新安装包
   uv pip install -e .
   
   # 验证模块可以正确导入
   .venv/bin/python -c "import contract_inspector; print('模块导入成功')"
   
   # 获取正确的项目路径
   pwd  # 将输出的路径用于Cursor配置
   ```

4. **MCP 配置问题**
   - 确保 Cursor 配置文件中的 `cwd` 路径正确指向项目根目录
   - 确保使用绝对路径而不是相对路径
   - 检查虚拟环境中的Python可执行文件是否存在
   - 如果 Cursor 无法启动 MCP 服务，检查配置文件语法是否正确

5. **本地 MCP 服务无响应**
   - 检查 `.env` 文件是否正确配置了 API 密钥
   - 查看 Cursor 的 MCP 日志获取详细错误信息
   - 确认项目依赖已通过 `uv sync` 正确安装

### 如何检查 MCP 服务状态

- 在 Cursor 中查看 MCP 连接状态（通常在设置或状态栏中显示）
- 如果需要调试，可以手动测试：`uv run python -c "import contract_inspector; print('模块可用')"`
- 查看 Cursor 的 MCP 日志文件以获取详细的错误信息

## 许可证

MIT License
