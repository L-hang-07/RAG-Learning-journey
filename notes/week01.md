#[关于流式输出]
(1)流式输出中.iter_lines()是处理SSE流的关键，由resques提供，会逐行读取响应体，阻塞每一行的到达

(2)iter_lines返回的是bytes,要用 [记录每行的变量].decode("utf-8").strip()转为字符串

(3)获取ai返回值时过滤掉非data行，用[记录每行的变量].startswith("data:")

(4)SSE规定：每行格式为field:value

(5)获取部分流片段时，每一次切掉多少字符用 data_str = line[要切掉的字符数量:].strip()，data:正好5个字符，所以可以用5，这样会直接拿到需要返回给用户的内容

(6)OPENAI兼容接口约定，流结束时发送一行[DONE]，所以判断是否结束可以用 if data_str == "[DONE]"后break

(7)解析单个JSON块
    try:
        chunk = json.loads(data_str)#
    except json.JSONDecodeError:
        continue
把data_str解析成Python字典 chunk

(8)提取delta内容
    delta = chunk["choices"][0].get("delta",{})
.get("delta",{})是安全取值，如果这个块没有delta字段，就返回空字典
OpenAI兼容响应结构:
    {
  "choices": [
    { "delta": { "content": "你" }, "index": 0, ... }
  ]
}

(9)取出文本片段用 piece = delta.get("content") 

(10)收集并实时打印
    if piece:
        parts.append(piece)
        print(piece,end = "",flush = True)
if piece 过滤掉None和空字符串
parts.append(piece)把piece记录的片段存入列表parts
end = "" 告诉系统不换行，后续内容直接接上上次的内容记录
flush = True 是关键，强制立即刷新输出缓冲区，不然用户看到的内容会是一大块一大块内容蹦出，而不是一个字一个字输出

(11)一定要让主函数拿到记录的内容，如果用parts列表记录，可以这样写
    return {
                    "choices":[{
                        "message":{"role":"assistant",
                                    "content":"".join(parts)
                                    },
                        "finish_reason":finish_reason or "stop",
                                    }]
                    }
把返回可是手动修改成这样，主函数使用是和非流式就一样去写
finish_reason是告诉你模型为什么停止，要手动定义
    if choice.get("finish_reason"):
                            finish_reason = choice["finish_reason"]

(12)所有片段打印完成之后记得换行，用
    print()
让终端光标回到下一行开头，不然后续输出会紧贴在这行的末尾

#[学会用OpenAI库可以节省很多时间]