from typing import Any,Optional
from typing_extensions import TypedDict


class AgentState(TypedDict):
    Task:str
    status:str #状态：待执行、执行中、已完成、失败
    plan:list[str] #计划
    selected_tool:str #选中的工具
    tool_input:dict #工具参数
    tool_output:dict #工具结果
    final_response:str 
    error:str|None