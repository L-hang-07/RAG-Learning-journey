from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path

# 获取当前文件(Aliyun_01.py)的绝对路径
current_dir = Path(__file__).resolve().parent
# 往上退两级，找到项目根目录的 .env
env_path = current_dir.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


prompt = """
    你是一个python开发专家兼python指导教师，精通python的各种库和框架，可以根据用户的需求给出用户需要的代码并教导用户为什么要这么写

    #任务目标:
    帮助用户根据需求生成python代码，并解释代码的实现原理和使用方法

    #执行步骤(Chain Of Thought):
    1.根据用户的需求分析用户需要什么样的代码
    2.给出用户需要的代码并对内容加以分析
    3.再给出代码后针对代码中使用的库和框架进行讲解。解释为什么要这么写

    #示例(Few-shot):
    用户输出：请帮我写一个函数，要求用户输入数字几就用一维数组实现杨辉三角的前几行
    你的输出：(代码)在该段代码中使用了什么库和框架，为什么要这么写

    #输出格式约束:
    你的输出必须以纯文本形式返回，不要编造内容，条理清晰先写代码再写分析

"""

client = OpenAI(
    base_url = "https://ws-7cvheikfp81bmhhq.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
    api_key = os.getenv("ALIYUNBAILIAN_API_KEY"),
)

messages =[
    {"role":"system","content":prompt},
    {"role":"user","content":"你好"}
]

response = client.chat.completions.create(
    model = "qwen3.8-max",
    messages = messages,
    stream = True
)

for chunk in response:
    if not chunk.choices:
        continue

    
    piece = chunk.choices[0].delta.content
    if piece:
        print(piece,end = "",flush = True)
