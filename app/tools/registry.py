from app.tools.builtin import mock_tool,list_files,read_file,write_file

TOOL_REGISTRY = {
    "mock_tool": {
      "name":"mock_tool",
      "description":"这是一个模拟工具，不执行实际操作，适用于测试和占位",
      "input_schema": {},
      "risk_level":"low",
      "handler":mock_tool
    },
    "list_files": {
    "name":"list_files",
    "description":"列出指定目录下的文件",
    "input_schema": {
        "path": "目录路径,默认是."
    },
    "risk_level":"low",
    "handler": list_files
    },
    "read_file": {
    "name":"read_file",
    "description":"读取指定文件的内容",
    "input_schema": {
        "path": "文件路径"    
    },
    "risk_level":"low",
    "handler": read_file
    },
    "write_file": {
    "name":"write_file",
    "description":"写入内容到指定文件",
    "input_schema": {
        "path": "文件路径",
        "content": "要写入的内容"
    },
    "risk_level":"high",
    "handler": write_file
    }
}

def get_tools_text()->str:
    lines=[]
    for tool in TOOL_REGISTRY.values():
        lines.append(
            f"- {tool['name']}：{tool['description']}，参数：{tool['input_schema']}，风险等级：{tool['risk_level']}"
        )
    return "\n".join(lines)