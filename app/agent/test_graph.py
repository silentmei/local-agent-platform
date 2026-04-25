
from app.agent.graph import app

result = app.invoke({
    "Task": "帮我写入 demo.txt，内容是 hello",
    "status": "created",
})

print(result)
