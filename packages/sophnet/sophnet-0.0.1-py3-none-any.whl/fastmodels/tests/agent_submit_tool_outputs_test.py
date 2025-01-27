from sophnet import Client

# 初始化客户端
client = Client(
    api_key="",
    project_id="6R4XsrhtHAnVeht6eCEUXx"
)
# 从控制台获取用户输入的内容
user_input = "青岛的天气"
# 调用create_and_run接口
response = client.agent.threads.create_and_run(
    agent_id="49ter1ApTeUhPOA2cCGdIp",
    messages=[
        {"role": "user", "content": user_input},
    ]
)

# 获取返回的function参数
location = response.required_action.submit_tool_outputs.tool_calls[0].function.arguments
print(f"function参数：{location}")


# 调用工具（虚拟）
tool_outputs = []

if response.tools[0].function.name == "get_weather":
    def get_weather(location:str):
        return "70 degrees F and raining"

    # 模拟调用get_weather方法
    weather = get_weather(location=location)
    tool_outputs.append({
        "tool_call_id": response.required_action.submit_tool_outputs.tool_calls[0].id,
        "output": weather
    })

# 提交工具调用结果
submit_outputs_response = client.agent.threads.submit_tool_outputs(
    agent_id="49ter1ApTeUhPOA2cCGdIp",
    thread_id=response.thread_id,
    run_id=response.run_id,
    tool_outputs=tool_outputs,
)

# 打印最终结果
print(f"最终结果：{submit_outputs_response.content[0].text.value}")