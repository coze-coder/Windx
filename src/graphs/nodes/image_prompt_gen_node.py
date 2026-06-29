import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import ImagePromptInput, ImagePromptOutput
from coze_coding_dev_sdk.llm import LLMClient


def image_prompt_gen_node(state: ImagePromptInput, config: RunnableConfig, runtime: Runtime[Context]) -> ImagePromptOutput:
    """
    title: 文生图提示词生成
    desc: 根据小说标题和用户选择的图片风格，生成适用于多个模型的文生图提示词
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    # 从配置文件读取提示词和模型配置
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r') as fd:
        _cfg = json.load(fd)
    
    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")
    
    # 使用jinja2模板渲染用户提示词
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render({
        "novel_title": state.novel_title,
        "image_style": state.image_style
    })
    
    # 初始化LLM客户端
    client = LLMClient()
    
    # 构建消息列表 - 使用LangChain消息格式
    from langchain_core.messages import SystemMessage, HumanMessage
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt_content)
    ]
    
    # 调用大模型生成提示词
    resp = client.invoke(
        model=llm_config.get("model"),
        messages=messages,
        temperature=llm_config.get("temperature", 0.7),
        max_completion_tokens=llm_config.get("max_completion_tokens", 500)
    )
    
    # 提取生成的内容
    if isinstance(resp.content, str):
        generated_prompt = resp.content.strip()
    elif isinstance(resp.content, list):
        # 处理列表类型的内容
        text_parts = []
        for item in resp.content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        generated_prompt = " ".join(text_parts).strip()
    else:
        generated_prompt = str(resp.content)
    
    return ImagePromptOutput(image_prompt=generated_prompt)