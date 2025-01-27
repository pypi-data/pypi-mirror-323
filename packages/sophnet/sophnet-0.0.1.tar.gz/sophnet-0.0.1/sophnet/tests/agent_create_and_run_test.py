from sophnet import Client

# 初始化客户端
client = Client(
    api_key="uVxF_DpwZbm-EZQlCojduKuF3jufdSMCyWJEbVPM6zL6Zgxx5EpsNrZONzHUWdjPIROLr-dtrgziDmq2pySvPA",
    project_id="6R4XsrhtHAnVeht6eCEUXx"
)
stream = False
# 从控制台获取用户输入的内容
user_input = "青岛的天气"
# 调用接口
response = client.agent.threads.create_and_run(
    agent_id="4UrtsyuHWQ8QbFXBknUeYx",
    messages=[
        {"role": "user", "content": user_input},
    ],
    stream=stream
)

# 打印输出
if stream:
    for chunk in response:
        # 确保 chunk.delta、chunk.delta.content 存在且至少有一个元素
        if hasattr(chunk, 'delta') and chunk.delta and chunk.delta.content and len(chunk.delta.content) > 0:
            content = chunk.delta.content[0]
            # 确保 content.text 存在并有 value 属性
            if hasattr(content, 'text') and content.text and hasattr(content.text, 'value'):
                print(f"Content: {content.text.value}, Finish Reason: {chunk.finish_reason}")

                # 确保 content.text.annotations 存在且至少有一个元素
                if hasattr(content.text, 'annotations') and content.text.annotations and len(
                        content.text.annotations) > 0:
                    annotation = content.text.annotations[0]
                    # 确保 annotation.file_citation 存在并有 filename 属性
                    if hasattr(annotation, 'file_citation') and annotation.file_citation and hasattr(
                            annotation.file_citation, 'filename'):
                        print(f"File Citation: {annotation.file_citation.filename}")
        if hasattr(chunk,'thread_id'):
            print(f"threadId: {chunk.thread_id}")
else:
    print(response.content[0].text.value)
    print(response.thread_id)




