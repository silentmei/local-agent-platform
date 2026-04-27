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

def run_shell(tool_input:dict)->dict:
    """
    执行shell命令
    """
    import subprocess
    command=tool_input.get("command")
    cwd=tool_input.get("cwd",".")
    timeout=tool_input.get("timeout",30)
    
    if not command:
        return{
            "success":False,
            "data":None,
            "error":"缺少参数：command",
        }
    
    try:
        completed=subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "success": completed.returncode == 0,
            "data": {
                "command": command,
                "cwd": cwd,
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            },
            "error": None if completed.returncode == 0 else f"命令执行失败，returncode={completed.returncode}",
        }
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "data": {
                "command": command,
                "cwd": cwd,
                "timeout": timeout,
            },
            "error": f"命令执行超时，超过 {timeout} 秒",
        }
    
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"命令执行异常：{str(e)}",
        }
        
def http_request(tool_input:dict)->dict:
    """
    发送http请求
    """
    import requests
    
    method=tool_input.get("method","GET").upper()
    url=tool_input.get("url")
    headers=tool_input.get("headers",{})
    params=tool_input.get("params",{})
    json_body=tool_input.get("data",{})
    timeout=tool_input.get("timeout",30)
    
    if not url:
        return {
            "success":False,
            "data":None,
            "error":"缺少参数：url",
        }
        
    try:
        response=requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_body,
            timeout=timeout,
        )
        return {
            "success": response.status_code >= 200 and response.status_code < 400,
            "data": {
                "method": method,
                "url": url,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text,
            },
            "error": None if response.status_code >= 200 and response.status_code < 400 else f"HTTP请求失败，状态码 {response.status_code}",
        }
    except requests.RequestException as e:
        return {
            "success": False,
            "data": None,
            "error": f"HTTP请求异常：{str(e)}",
        }