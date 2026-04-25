
from app.agent.graph import app

result = app.invoke({
    "Task": "帮我制定一个学习 LangGraph 的计划",
    "status": "created",
})

print(result)
