# 推荐

## 创建 Chinese-Holidays MCP for Python 服务器

### 1、初始化项目
1. 首先安装 [uv>=0.4.10](https://docs.astral.sh/uv/)，作为 Python 项目和虚拟环境的管理工具;

2. 执行命令并通过提示引导创建 MCP 服务器项目：
    ```bash
    uvx create-mcp-server
    ```

3. 完成安装后，启动服务器：
    ```bash
    cd <project-name>
    uv sync --dev --all-extras
    uv run <project-name>
    ```

### 2、开发 MCP Tools
1. 完善 `handle_list_tools` 函数，添加对 **Tools** 的定义、描述、和参数约束条件：
    ```python
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        return [
            types.Tool(
                name="get-all-holidays",
                description="Get all holidays for a year",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "year": {"type": "int"},
                    },
                    "required": ["year"],
                },
            )
        ]
    ```

2. 完善 `handle_call_tool` 函数，在完成 `name` 和 `arguments` 的校验后，执行具体函数的调用：
    ```python
    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution requests"""
        try:
            if name == "get-all-holidays":
                if not arguments or "year" not in arguments:
                    raise ValueError("Missing year argument")
                result = await get_all_holidays(arguments["year"])
                return [types.TextContent(type="text", text=str(result))]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    ```

3. 编写具体的函数，用于实现具体的工具功能：
    ```python
    async def get_all_holidays(year: int) -> str:
        """Get all holidays for a year.

        Args:
            year: The year to get holidays for.
        """
        url = f"{BASE_API}/v1/holidays/{year}"
        data = await make_request(url)
        formatted_holidays = format_holidays(data)
        return f"{year}年节假日安排：\n{formatted_holidays}"
    ```

4. 编写必要的辅助函数和常量设置：
    ```python
    def format_holidays(holiday_data: dict[str, Any]) -> str:
        """
        格式化节假日数据为指定格式，处理国庆节和中秋节的合并与分开情况。

        Args:
            holiday_data: 一个字典，键为日期字符串，值为包含节假日信息的字典。

        Returns:
            格式化后的节假日字符串，每个节假日一行，包含序号和日期列表。
        """
        # 初始化节假日映射
        formatted_holidays: dict[str, list[str]] = {}
        
        # 收集所有节假日数据
        for holiday_info in holiday_data.values():
            name = holiday_info['name']
            date = holiday_info['date']
            formatted_holidays.setdefault(name, []).append(date)
        
        # 定义节假日顺序和格式化模板
        HOLIDAY_ORDER = {
            "元旦": 1,
            "春节": 2,
            "清明节": 3,
            "劳动节": 4,
            "端午节": 5,
            "国庆节": 6,
            "中秋节": 6,  # 默认序号，可能会根据组合情况调整
            "国庆节、中秋节": 6,
            "中秋节、国庆节": 6
        }
        
        output = []
        
        # 处理常规节假日
        for holiday in ["元旦", "春节", "清明节", "劳动节", "端午节"]:
            if holiday in formatted_holidays:
                dates = "、".join(formatted_holidays[holiday])
                output.append(f"{HOLIDAY_ORDER[holiday]}、{holiday}：{dates};\n")
        
        # 特殊处理国庆节和中秋节的组合情况
        combined_names = ["国庆节、中秋节", "中秋节、国庆节"]
        for combined_name in combined_names:
            if combined_name in formatted_holidays:
                dates = "、".join(formatted_holidays[combined_name])
                output.append(f"{HOLIDAY_ORDER[combined_name]}、{combined_name}：{dates};\n")
                break
        else:
            # 如果没有组合节日，分别处理国庆节和中秋节
            if "国庆节" in formatted_holidays:
                dates = "、".join(formatted_holidays["国庆节"])
                output.append(f"6、国庆节：{dates};\n")
            
            if "中秋节" in formatted_holidays:
                dates = "、".join(formatted_holidays["中秋节"])
                index = "7" if "国庆节" in formatted_holidays else "6"
                output.append(f"{index}、中秋节：{dates};\n")
        
        return "".join(output)
    ```

### 3、使用 MCP Inspector 进行调试

1. 执行命令并启动 MCP Inspector：
    ```bash
    npx @modelcontextprotocol/inspector uv --directory ./ run chinese-holidays
    ```
    注：根据项目实际情况，需要调整 `--directory` 参数的值。

2. 在 Inspector 中添加 `PYTHONIOENCODING` 环境变量:

    ```txt
    # Environment Variables / Add Environment Variable
    PYTHONIOENCODING=utf-8
    ```
3. 点击 `Connect` 连接到服务器，并导航到 Tools 选项；

4. 在列出的工具中选择 `get-all-holidays`，在设置必要的参数后，点击 `Run Tool` 运行工具。