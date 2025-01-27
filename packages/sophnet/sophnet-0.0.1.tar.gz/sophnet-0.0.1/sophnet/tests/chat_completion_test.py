from sophnet import SophNet

client = SophNet(
    base_url="http://127.0.0.1:8859/open-apis",
    api_key="8-dzAVPWA_oIjb1OUdBUjEjlwZVCevkwxcrX3TCs3emXgXHdxgmOLsyTr3rPRfmRcWUmVHAeLe0yziyu9utW2w",
)

completion = client.chat.completions.create(
    model="spn3/Qwen2.5-72B-Instruct",
    messages=[
        {
            "role": "user",
            "content": "你好"
        }
    ],
    stream=True
)

# print(completion.choices[0].message.content)
for chunk in completion:
    print(chunk.choices[0].delta)