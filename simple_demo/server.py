from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("Server")

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    return a - b

@mcp.prompt("operation-decider")
def operation_decider_prompt(user_query: str) -> list[base.Message]:
    return [
        base.UserMessage(f"""Strictly extract numbers and operation from: {user_query}. Reply **ONLY in JSON string** like this: {{"a": a, "b": b, "operation": "add / subtract"}}"""),
    ]

if __name__ == "__main__":
    print("MCP server is running using stdio transport ...")
    mcp.run(transport="stdio")