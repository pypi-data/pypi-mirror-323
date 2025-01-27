from sophnet import Client

# 初始化客户端
client = Client(
    api_key="",
    project_id="6R4XsrhtHAnVeht6eCEUXx"
)
stream = False
# 从控制台获取用户输入的内容
user_input = "青岛的天气"
# 调用接口
response = client.agent.threads.create_and_run(
    agent_id="49ter1ApTeUhPOA2cCGdIp",
    messages=[
        {"role": "user", "content": user_input},
    ],
    stream=stream
)

# 打印输出
print(response.thread_id)
print(response.run_id)
print(response.required_action.submit_tool_outputs.tool_calls[0].id)

#调用工具（虚拟）
tool_outputs = []

if response.tools[1].function.name == "get_weather":
    weather = "70 degrees F and raining"   #weather = get_weather()
    tool_outputs.append({
      "tool_call_id": response.required_action.submit_tool_outputs.tool_calls[0].id,
      "output": weather
    })

# 提交工具结果
submit_outputs_response = client.agent.threads.submit_tool_outputs(
    agent_id="49ter1ApTeUhPOA2cCGdIp",
    thread_id=response.thread_id,
    run_id=response.run_id,
    tool_outputs=tool_outputs,

    stream=stream
)

print(submit_outputs_response.content[0].text.value)
