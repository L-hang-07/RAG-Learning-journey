import random
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

prompt = """
    你是一个一个专业的大厂HR兼简历优化师，乐于助人且细心

    #任务目标
    你的任务是检查用户的简历，并指出问题后给出修改意见,使其符合STAR原则(情景，任务，行动，结果)，并量化结果

    #执行步骤(Cot)
    请先在<analysis>标签中进行分析，然后再在<result>标签内输出最终结果
    1.找出简历中模糊不清的内容并提出修改意见
    2.尽量使用量化词
    3.运用强动词如(主导，落地)

    #少量示例(Few-shot)
    用户输入:我负责公司网站的建立
    你的输出:
    <analysis>
    原文过于简略，缺乏具体技术栈和业务结果，动词“负责”缺乏力量感，建议改成你具体负责哪个网站的开发，使用了什么技术。
    </analysis>
    <result>
    主导公司核心官网的从0到1开发，采用React + Node.js 架构，上线后网页加载速度提升40%，日均支撑10,000+ UV 访问。
    </result>

    #输出格式约束
    你的最终回复必须以纯文本形式返回，包含<analysis>和<result>两部分，不要说其他废话。
    绝对不要输出<analysis>等尖括号标签
"""

#配置区
API_URL = "https://api.deepseek.com/v1/chat/completions"
API_KEY = os.getenv("DEEPSEEK_API_KEY")
MODEL = "deepseek-chat"

#超时配置
TIMEOUT = (5,30)

#可重试的状态码
RETRYABLE_STATUS_CODES = (429,500,502,503,504)

#重试配置
MAX_RETRY = 5
RETRY_BACKOFF = 1.0 #基础退避系数(秒)

#核定代码请求
def api_retry(session,messages):
    """
    带重试机制且可复用的API请求
    :param session: requests.Session对象
    :param messages:消息列表
    return:成功则返回字典，失败返回None
    """

    headers = {
        "Authorization":f"Bearer {API_KEY}",
        "Content-Type":"application/json"
    }

    payload = {
        "model":f"{MODEL}",
        "messages":messages,
        "stream":False
    }

    for attempt in range(MAX_RETRY):
        try:
            response = session.post(
                API_URL,
                json = payload,
                headers = headers,
                timeout = TIMEOUT
            )
            #如果成功连接并取得返回值
            if response.ok:
                return response.json()

            #如果是可重试的状态码且有重试次数
            if response.status_code in RETRYABLE_STATUS_CODES and attempt < MAX_RETRY - 1:
                wait = min(30,RETRY_BACKOFF * (2 ** attempt) * random.uniform(0.5,1.5))
                print(f"[重试]:{wait:.1f}秒后重试")
                time.sleep(wait)
                continue

            #如果是不可重试的状态码,直接抛出
            response.raise_for_status()

        #时间超时类错误
        except requests.exceptions.Timeout:
            #有重试次数
            if attempt < MAX_RETRY - 1:
                wait = min(30,RETRY_BACKOFF * (2 ** attempt) * random.uniform(0.5,1.5))
                print(f"[重试]:{wait:.1f}秒后重试")
                time.sleep(wait)
                continue
            #没有重试次数
            else:
                print("[失败],请求超时")
                return None

        #连接错误
        except requests.exceptions.ConnectionError:
            #有重试次数
            if attempt < MAX_RETRY - 1:
                wait = min(30,RETRY_BACKOFF * (2 ** attempt) * random.uniform(0.5,1.5))
                print(f"[重试]:{wait:.1f}秒后重试")
                time.sleep(wait)
                continue
            #没有重试次数
            else:
                print("[失败]:客户端连接失败")
                return None

        #经过上面两个处理后仍然不可重试的状态码
        except requests.exceptions.HTTPError as e:
            print(f"[错误]客户端错误，不可重试:{e}")

#主函数
def main():
    with requests.Session() as session:
        #初始化对话程序，定义ai性格
        conversation = [
            {"role":"system","content":prompt}
            ]
        print("对话程序已启动，输入quit或者exit退出程序")
        while True:
            try:
                user_input = input("你:").strip()
            except (EOFError,KeyboardInterrupt):
                print("再见！")
                break

            if not user_input.strip():
                continue
            if user_input.lower() in ("quit","exit"):
                print("再见！")
                break

            #将用户输入的内容加入对话历史
            conversation.append({"role":"user","content":user_input})

            #开始调用API
            print("正在生成回复\n")
            data = api_retry(session,conversation)

            #如果没有返回任何值
            if data is None:
                print("[错误]:没有获得任何回复")
                conversation.pop() #避免污染上下文，将用户提的问题踢出对话历史
                continue

            #正常返回了内容
            try:
                reply = data["choices"][0]["message"]["content"]
                print(f"AI:{reply}")
                conversation.append({"role":"assistant","content":reply})
            except (KeyError,IndexError) as e:
                print("[错误]收到的响应格式异常")
                #将用户问的问题踢出对话历史
                conversation.pop()

if __name__ == "__main__":
    main()