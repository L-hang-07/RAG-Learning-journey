from langchain_core.prompts import PromptTemplate,FewShotPromptTemplate
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

chat = ChatOpenAI(
    model = "qwen3.8-max",
    base_url ="https://ws-7cvheikfp81bmhhq.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
    api_key = os.getenv("DASHSCOPE_API_KEY")
)


example_template = PromptTemplate.from_template(
    "单词:{word},反义词:{antonym}"
)

example_data = [
    {"word":"开心","antonym":"难过"},
    {"word":"上","antonym":"下"}
]

few_shot_prompt = FewShotPromptTemplate(
    example_prompt = example_template,
    examples = example_data,
    prefix = "给定的单词，输出它的反义词",
    suffix = "基于示例请告诉我{input_word}的反义词是什么",
    input_variables = ["input_word"]    #显示声明输入变量
)

prompt_text = few_shot_prompt.invoke(input = {"input_word",input("请输入单词")}).to_string()

print(prompt_text)