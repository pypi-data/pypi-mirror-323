from sophnet import Client

# 初始化客户端
client = Client(
    api_key="",
    project_id=""
)

stream = True
meeting_minutes_response = client.easyllm.pota_anlyst.create(
    easyllm_id="",
    prompt="POTA是什么",
    stream=stream,

)

# 打印输出
if stream:
    for chunk in meeting_minutes_response:
        for choice in chunk.choices:
            print(f"Index: {choice.index}, Content: {choice.delta.content}, Finish Reason: {choice.finish_reason}")
else:
    print(meeting_minutes_response.choices[0].message.content)