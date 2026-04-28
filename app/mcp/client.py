import asyncio
import threading
from typing import Any

from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

from app.mcp.config import MCP_SERVERS

def run_async_in_thread(coro):
    """
    在同步工具handler里运行async MCP调用，避免 FastAPI 事件循环里直接 asyncio.run 报错。
    """
    result={}
    error={}
    
    def runner():
        try:
            result["value"]=asyncio.run(coro)
        except Exception as e:
            error["value"]=e
            
    thread=threading.Thread(target=runner)
    thread.start()
    thread.join()
        
    if "value" in result:
        return result["value"]

    if "value" in error:
        raise error["value"]
        
    return result.get("value")
    

async def list_mcp_tools(server_name: str) -> list[dict]:
    """"
    连接某个 MCP Server，读取它提供了哪些工具，然后把工具列表整理成 list[dict] 返回。
    """
    server = MCP_SERVERS[server_name]

    params = StdioServerParameters(
        command=server["command"],
        args=server.get("args") or [],
        env=server.get("env"),
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.list_tools()

            return [
                {
                    "server_name": server_name,
                    "name": tool.name,
                    "description": tool.description or "",
                    "input_schema": tool.inputSchema or {},
                }
                for tool in result.tools
            ]

async def call_mcp_tool(
    server_name: str,
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> dict:
    server = MCP_SERVERS[server_name]

    params = StdioServerParameters(
        command=server["command"],
        args=server.get("args") or [],
        env=server.get("env"),
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                tool_name,
                arguments=arguments or {},
            )

            content = []
            for item in result.content:
                if hasattr(item, "model_dump"):
                    content.append(item.model_dump())
                else:
                    content.append(str(item))

            is_error = getattr(result, "isError", False)

            return {
                "success": not is_error,
                "data": {
                    "content": content,
                    "structured_content": getattr(result, "structuredContent", None),
                },
                "error": "MCP 工具调用失败" if is_error else None,
            }

#同步包装
def list_mcp_tools_sync(server_name: str) -> list[dict]:
    return run_async_in_thread(list_mcp_tools(server_name))

#同步包装
def call_mcp_tool_sync(
    server_name: str,
    tool_name: str,
    arguments: dict | None = None,
) -> dict:
    return run_async_in_thread(
        call_mcp_tool(
            server_name=server_name,
            tool_name=tool_name,
            arguments=arguments,
        )
    )
