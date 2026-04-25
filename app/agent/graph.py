from app.agent.state import AgentState
from app.agent.node import plan_task,select_tool,execute_tool,finalize_task
from langgraph.graph import StateGraph, START, END





graph = StateGraph(AgentState)


graph.add_node("plan_task", plan_task)
graph.add_node("select_tool", select_tool)
graph.add_node("execute_tool", execute_tool)
graph.add_node("finalize_task", finalize_task)


graph.add_edge(START, "plan_task")
graph.add_edge("plan_task", "select_tool")
graph.add_edge("select_tool", "execute_tool")
graph.add_edge("execute_tool", "finalize_task")
graph.add_edge("finalize_task", END)


app=graph.compile()