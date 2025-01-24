from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from typing import Any

import mcp.types as types
import mcp.server.stdio
import httpx
import logging

logger = logging.getLogger('chinese-holidays')
logger.info("Starting MCP Chinese-Holidays Server")

server = Server("chinese-holidays")


BASE_API = "https://api.jiejiariapi.com"

async def make_request(url: str) -> dict[str, Any] | None:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_holidays(holiday_data: dict[str, Any]) -> str:
    """
    格式化节假日数据为指定格式，处理国庆节和中秋节的合并与分开情况。

    Args:
        holiday_data: 一个字典，键为日期字符串，值为包含节假日信息的字典。
    Returns: 格式化后的节假日字符串，每个节假日一行，包含序号和日期列表。
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

async def get_all_holidays(year: int) -> str:
    """Get all holidays for a year.

    Args:
        year: The year to get holidays for.
    """
    url = f"{BASE_API}/v1/holidays/{year}"
    logger.debug(f"Getting holidays for {year}")
    data = await make_request(url)
    formatted_holidays = format_holidays(data)
    return f"{year}年节假日安排：\n{formatted_holidays}"

async def is_holiday(date: str) -> str:
    """
    Check if a date is a holiday.

    Args:
        date: The date to check. Format: YYYY-MM-DD
    """
    url = f"{BASE_API}/v1/is_holiday?date={date}"
    logger.debug(f"Checking if {date} is a holiday")
    data = await make_request(url)

    result = ""
    if "is_holiday" in data:  # 状态 1：节假日信息
        if data["is_holiday"]:
            result = f"{data['holiday']['date']}是{data['holiday']['name']}"
        else:
            result = f"{date}不是节假日"
    elif "message" in data:  # 状态 3：错误信息
        result = f"错误: {data['message']}, 支持的格式：{data.get('supported_formats', '未知')}"
    return result

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
        ),
        types.Tool(
            name="is-holiday",
            description="Check if a date is a holiday",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {"type": "string"},
                },
                "required": ["date"],
            },
        )
    ]

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
        elif name == "is-holiday":
            if not arguments or "date" not in arguments:
                raise ValueError("Missing date argument")
            result = await is_holiday(arguments["date"])
            return [types.TextContent(type="text", text=str(result))]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="chinese-holidays",
                server_version="0.1.10",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )