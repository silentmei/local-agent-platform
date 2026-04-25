def mock_tool(tool_input: dict) -> dict:
    return {
        "success": True,
        "data": {
            "message": "mock tool executed",
            "input": tool_input,
        },
        "error": None,
    }
    
def list_files(tool_input:dict)->dict:
    """
    列出当前目录下所有文件
    """
    import os
    path=tool_input.get("path",".")
    if not os.path.isdir(path):
        return {
            "success":False,
            "data":None,
            "error":f"目录 {path} 不存在",
        }
    files=os.listdir(path)
    if not files:
        return {
            "success":False,
            "data":None,
            "error":f"目录 {path} 下没有文件",
        }
    return {
        "success":True,
        "data":{
            "path":path,
            "files":files,
        },
        "error":None,
    }

def read_file(tool_input:dict)->dict:
    """
    读取指定文件内容
    """
    import os
    path=tool_input.get("path")
    if not path:
        return {
            "success":False,
            "data":None,
            "error":"缺少参数：path",
        }
    if not os.path.isfile(path):
        return {
            "success":False,
            "data":None,
            "error":f"文件 {path} 不存在",
        }
    with open(path,"r") as f:
        content=f.read()
    return {
        "success":True,
        "data":{
            "path":path,
            "content":content,
        },
        "error":None,
    }
    
def write_file(tool_input:dict)->dict:
    """
    写入内容到指定文件
    """
    path=tool_input.get("path")
    content=tool_input.get("content")
    if not path or content is None:
        return {
            "success":False,
            "data":None,
            "error":"缺少参数：path 或 content",
        }
    with open(path,"w") as f:
        f.write(content)
    return {
        "success":True,
        "data":{
            "path":path,
            "message":f"内容已写入文件 {path}",
        },
        "error":None,
    }
