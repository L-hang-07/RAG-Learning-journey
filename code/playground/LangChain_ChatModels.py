from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage
import os
from dotenv import load_dotenv

load_dotenv()

chat = ChatOpenAI(
    model = "qwen3.8-max",
    base_url ="https://ws-7cvheikfp81bmhhq.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
    api_key = os.getenv("DASHSCOPE_API_KEY")
)

messages = [
    ("system","你是一个边塞诗人"),#SystemMessage(content = "你是一个边塞诗人"),
    ("human","帮我写一首边塞诗"),
    ("AI","大漠孤烟直，长河落日圆")
]

response = chat.stream(input = messages)

input_messages = input("你:")

messages.append(("human",(input_messages)))
#messages.append(HumanMessage(content = input_messages))

for chunk in response:
    print(chunk.content,end = "",flush = True)
