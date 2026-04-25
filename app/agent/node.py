from app.agent.state import AgentState
from langchain_openai import ChatOpenAI
import json
import os
from dotenv import load_dotenv
from app.tools.registry import TOOL_REGISTRY, get_tools_text
tools_text=get_tools_text()
load_dotenv()

# 导入env
KIMI_API_KEY = os.getenv("KIMI_API_KEY")
KIMI_BASE_URL = os.getenv("KIMI_BASE_URL")
KIMI_MODEL = os.getenv("KIMI_MODEL")


# plan
def plan_task(state: AgentState) -> dict:
    """
    根据当前任务，制定计划
    """

    llm = ChatOpenAI(
        model=KIMI_MODEL,
        temperature=1,
        openai_api_key=KIMI_API_KEY,
        base_url=KIMI_BASE_URL,
    )
    prompt = f"请根据以下任务描述，制定一个详细的计划：{state['Task']}"
    plan = llm.invoke(prompt)

    return {
        "plan": plan.content.split("\n"),
        "status": "planned",
    }


def select_tool(state: AgentState) -> dict:
    """
    根据计划，选择合适的工具
    """
    tools_text = """
可用工具：
1. mock_tool：不需要真实工具时使用
2. list_files：列出目录文件，参数：{"path": "目录路径"}
3. read_file：读取文件内容，参数：{"path": "文件路径"}
4. write_file：写入文件，参数：{"path": "文件路径", "content": "写入内容"}
"""

    prompt = f"""
你是一个工具选择器。

用户任务：
{state["Task"]}

执行计划：
{state["plan"]}

{tools_text}

请判断是否需要调用工具，并选择最合适的工具。

只返回 JSON，不要解释：
{{
  "need_tool": true,
  "selected_tool": "工具名",
  "tool_input": {{}}
}}
"""

    llm = ChatOpenAI(
        model=KIMI_MODEL,
        temperature=1,
        openai_api_key=KIMI_API_KEY,
        base_url=KIMI_BASE_URL,
    )

    response = llm.invoke(prompt)
    content = response.content.strip()
    content = content.removeprefix("```json").removesuffix("```").strip()
    result = json.loads(content)

    if not result.get("need_tool", True):
        return {
            "selected_tool": "mock_tool",
            "tool_input": {},
            "status": "tool_selected",
        }

    return {
        "selected_tool": result.get("selected_tool", "mock_tool"),
        "tool_input": result.get("tool_input", {}),
        "status": "tool_selected",
    }


def execute_tool(state: AgentState) -> AgentState:
    """
    执行选中的工具，获取结果
    """
    tool_name=state.get("selected_tool","mock_tool")
    tool_input=state.get("tool_input",{})
    
    tool_info=TOOL_REGISTRY.get(tool_name)
    
    if tool_info is None:
        return {
            "tool_output": {
                "success": False,
                "data": None,
                "error": f"未知工具：{tool_name}",
            },
            "status": "failed",
        }
    handler = tool_info["handler"]
    tool_output = handler(tool_input)          
   
    return {
        "tool_output": tool_output,
        "status": "tool_executed" if tool_output.get("success") else "failed",
    }


def finalize_task(state: AgentState) -> dict:
    """
    根据工具结果，生成最终响应
    """
    tool_output = state.get("tool_output", {})

    prompt = f"""
根据工具执行结果，生成对用户的最终响应。

用户任务：
{state["Task"]}

用户计划：
{state.get("plan", [])}

工具名称：
{state.get("selected_tool", "")}

工具结果：
{tool_output}

要求：
1. 用简洁中文回答
2. 如果工具执行失败，说明失败原因
3. 不要编造工具结果中没有的信息
"""

    llm = ChatOpenAI(
        model=KIMI_MODEL,
        temperature=1,
        openai_api_key=KIMI_API_KEY,
        base_url=KIMI_BASE_URL,
    )

    final_response = llm.invoke(prompt).content.strip()

    return {
        "final_response": final_response,
        "status": "completed" if tool_output.get("success") else "failed",
    }
