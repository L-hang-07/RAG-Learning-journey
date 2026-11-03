import requests
import time
import random
import sys
import os
from dotenv import load_dotenv
import json

load_dotenv()

#整合了系统提示，CoT，Few—shot的提示词
prompt = """
    你是一个顶尖的互联网大厂HR兼简历优化专家。
    
    #任务目标
    帮助用户优化简历中的项目经历描述，使其符合STAR原则（情境、任务、行动、结果），并量化结果

    执行步骤(Chain of Thought):
    请先在<analysis>标签中进行分析，然后再在<result>标签内输出最终结果。
    1.找出原文中模糊不清的描述（如“负责的项目名称”）
    2.找出原文中缺失的量化词
    3.运用强动词（如“主导”、“重构”、“落地”）
    4.提供修改意见，指出原文中的不足

    #示例(Few-shot):
    用户输入：我负责了公司的网站开发。
    你的输出：
    <analysis>
    原文过于简略，缺乏具体技术栈和业务结果，动词“负责”缺乏力量感，建议改成你具体负责哪个网站的开发，使用了什么技术。
    </analysis>
    <result>
    主导公司核心官网的从0到1开发，采用React + Node.js 架构，上线后网页加载速度提升40%，日均支撑10,000+ UV 访问。
    </result>

    #输出格式约束
    你的最终输出必须以纯文本格式返回，包含<analysis>和<result>两个部分。不要输出其他废话。
    """

#配置区
API_URL = "https://api.deepseek.com/v1/chat/completions"
API_KEY = os.getenv("DEEPSEEK_API_KEY")
MODEL = "deepseek-chat"

#可重试的HTTP状态码
RETRYABLE_STATUS_CODES = {429,500,502,503,504}

#超时配置（连接超时，读取超时）
TIMEOUT = (5,60)

#重试配置
MAX_RETRIES = 3
BASE_BACKOFF = 1.0 #基础退避时间（秒）

#核心请求函数
def call_api_with_retry(session,messages):
    """
    带重试机制的API调用
    :param session: requests.Session对象
    :param messages: 对话消息列表
    :return:成功则返回PAPI的响应字典，失败则返回None
    """
    headers = {
        "Authorization":f"Bearer {API_KEY}",
        "Content-Type":"application/json"
    }
    payload = {"model":MODEL,
               "messages":messages,
               "stream":True}

    for attempt in range(MAX_RETRIES+1):
        try:
            response = session.post(
                API_URL,
                json = payload,
                headers = headers,
                timeout = TIMEOUT,
                stream = True
            )

            #状态码为2xx表示成功
            if response.ok:
                #解析SSE
                parts = []
                try:
                    for line in response.iter_lines():
                        if not line:
                            continue
                        line = line.decode("utf-8").strip()
                        if not line.startswith("data:"):
                            continue
                        data_str = line[5:].strip()
                        if data_str =="[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                        except json.JSONDecodeError:
                            continue
                        delta = chunk["choices"][0].get("delta",{})
                        piece = delta.get("content")
                        if piece:
                            parts.append(piece)
                            print(piece,end="",flush=True) #打字机输出
                    print() #换行
                except (requests.exceptions.ChunkedEncodingError,
                        requests.exceptions.ConnectionError) as e:
                    #流中断，走重试
                    if attempt < MAX_RETRIES:
                        wait = min(30, BASE_BACKOFF * (2 ** attempt)) * random.uniform(0.5, 1.5)
                        print(f"\n[流中断 {wait}秒后重试({attempt + 1}/{MAX_RETRIES})]")
                        time.sleep(wait)
                        continue
                    print("\n[失败]流式传输中断，已达最大重试")
                    return None
                #返回一个同意结构，让下游代码不用改
                return {"choices":[{"message":{"content":"".join(parts)}}]}
            
            #可重试的状态码，并且有重试次数
            if response.status_code in RETRYABLE_STATUS_CODES and attempt < MAX_RETRIES:
                #计算指数退避+随即抖动
                wait = min(30,BASE_BACKOFF*(2**attempt))*random.uniform(0.5,1.5)
                print(f"[重试]状态码{response.status_code}，等待{wait:.1f}秒后重试"
                    f"({attempt + 1}/{MAX_RETRIES})")
                time.sleep(wait)
                continue

            #不可重试的错误，直接抛出
            response.raise_for_status()

        except requests.exceptions.Timeout:
            if attempt<MAX_RETRIES:
                wait = min(30,BASE_BACKOFF*(2**attempt))*random.uniform(0.5,1.5)
                print(f"[重试]请求超时，等待{wait:.1f}秒后重试")
                time.sleep(wait)
            else:
                print("[失败]请求超时，已达到最大重试次数。")
                return None

        except requests.exceptions.ConnectionError:
            if attempt<MAX_RETRIES:
                wait = min(30,BASE_BACKOFF*(2**attempt))*random.uniform(0.5,1.5)
                print(f"[网络错误]{wait:.1f}秒后重试({attempt + 1}/{MAX_RETRIES})")
                time.sleep(wait)
            else:
                print("[失败]网络错误，已达到最大重试次数。")
                return None

        except requests.exceptions.HTTPError as e:
            #经过上面处理后，仍然不可重试的非2xx状态码
            print(f"[客户端错误]不可重试:{e}")
            return None

    return None

#主循环
def main():
    #使用session复用链接
    with requests.Session()as session:
        #初始化对话历史，system消息用于设置助手的人设
        conversation = [
            {"role":"system","content":prompt}
        ]

        print("对话程序已启动，输入quit或者exit退出程序。\n")

        while True:
            try:
                user_input = input("你：").strip()
            except (EOFError,KeyboardInterrupt):
                print("\n再见！")
                break

            if user_input.lower() in ("quit","exit"):
                print("再见！")
                break
            if not user_input:
                continue

            #将用户输入加入对话历史
            conversation.append({"role":"user","content":user_input})

            #调用API
            print("正在生成回复，请稍后")
            data = call_api_with_retry(session,conversation)

            if data is None:
                print("[错误]，暂时无法获得回答")
                #避免污染上下文，导致后续请求出错，将刚才用户的输入移除
                conversation.pop()
                continue

            #提取AI的回复
            try:
                reply = data["choices"][0]["message"]["content"]
                #将AI的回复加入对话历史
                conversation.append({"role":"assistant","content":reply})
            except (KeyError,IndexError) as e:
                print("AI：抱歉，收到的相应格式异常\n")
                #清理掉有问题的用户消息
                conversation.pop()

if __name__ == "__main__":
    main()
                          