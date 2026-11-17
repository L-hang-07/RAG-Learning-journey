#-------------------LangChain(Python的一个第三方库)
(1)六个主要功能
    Prompts:提示词工程，方便优化提示词
    Models:调用各类模型
    History:管理会话历史记录
    Indexes:管理和分析各类文档
    Chains:构建功能的执行链条
    Agent:构建智能体 

(2)三种类型的模型
    LLMs(大语言模型)，Chat Models(聊天模型)，Embeddings Models(嵌入模型)

(3)使用前导入要用的大模型相关模块
通过[.invoke]调用
    如:
    llm = Tongyi(model = "qwen3.8-max"，
        api_key = ,
        base_url = )
    res = llm.invoke("要问的问题")
    print(res)

#-------------------RAG
RAG:检索增强生成，提供从特定数据源检索到的信息，以此来修正和补充生成的答案
    RAG = 检索技术 + LLM提示

工作中的标准流程
    离线板块(索引阶段):从可接触到的数据库中 提取内容，划分段落区块后以 向量形式 嵌入向量库
    实时板块(检索阶段和生成阶段):用户提出问题后，转换成向量 在向量库内进行 相似匹配，将匹配到的内容和用户提出的原始问题 结合成Prompt发送给大模型

向量:文本的[数字身份证],把一段文字的[语义信息]，转换成一串固定长度的[数字列表],让计算机能看懂文字的含义并做[相似度计算]

流式输出:定义等与非流式输出一样，获取对话内容时将[.invoke]换成[.stream]
    response = llm.stream(input = "要问的问题")
    for chunk in responce:
        piece = chunk.choices[0].delta.content
        print(piece,end = "",flush = True)

LLMs Model(大语言模型)
    #传统的纯文本llm正在逐渐被淘汰，ChatModel就是调用大语言模型的标准且首选的写法
    
    可以先统一定义一个变量去包含model，base_url等
    之后配置时可以llm = ChatOpenAI(
        model_kwargs = 提前定义的那个变量  #相当于将配置好的字典传给了model_kwargs
    )

Chat Model(聊天模型)
    AIMessage(常规里的assistant一样的角色定位)
    HumanMessage(user)
    SystemMessage(system)

    from langchain_openai import ChatOpenai
    from langchain_core.messages import AIMessage,HumanMessage,SystemMessage
    #需要导入这个模块才能使用
        #初始化模型
        chat = ChatOpenai(model = "qwen3.8-max")
        #历史信息
        messages = [
            HumenMessage(content = "")
        ]
        for chunk in chat.stream(input=messages):#stream()方法需要输出 括号内的内容就是告诉程序 需要将messages这个变量内的内容传给模型,这段代码的本质是将messages这个变量的内容显式的赋值给stream里的input参数，LangChain内的_convert_input会把不同输出格式的内容同义转换成PromptValue,再进行后续的调用和流式输出
            print(chunk.content,end = "",flush = True)

        #其中message的编写还可以用字符串代替，这样简写与上边内容完全等价
        
        messages = [#里面写元组
            ("system","你是一个边塞诗人"),
            ("human","帮我写一首边塞诗"),
            ("ai","大漠孤烟直，长河落日圆")
        ]
        [简写好处]简写可是动态的，由LangChain内部函数将元组转换，可以省去非简写形式的导入模块代码
            更主要的是可以用 {变量} 占位，直接将代码内的内容写进历史对话中

Embeddings Models(文本嵌入模型)
    阿里云模型访问方式
    from langchain_community.embeddings import DashScopeEmbeddings

    .embed_query("")将括号内的内容转为向量，一次只能转换一个内容
    .embed_documents(['','',''])将括号内的内容批量转换为向量，一次可以转换多个内容