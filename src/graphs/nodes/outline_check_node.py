import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import OutlineCheckInput, OutlineCheckOutput
from coze_coding_dev_sdk.llm import LLMClient
from langchain_core.messages import SystemMessage, HumanMessage


def outline_check_node(
    state: OutlineCheckInput, 
    config: RunnableConfig, 
    runtime: Runtime[Context]
) -> OutlineCheckOutput:
    """
    title: 章节大纲对比检查
    desc: 对比章节大纲与总大纲，检查是否偏离总纲设定，包括主题、人物性格、剧情走向、背景设定等方面的对应性
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        _cfg = json.load(fd)
    
    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up_tpl = Template(_cfg.get("up", ""))
    
    user_prompt = up_tpl.render({
        "overall_outline": state.overall_outline,
        "chapter_outline": state.chapter_outline,
        "current_title": state.current_title
    })
    
    client = LLMClient(ctx=ctx)
    
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt),
    ]
    
    response = client.invoke(
        messages=messages,
        model=llm_config.get("model"),
        temperature=llm_config.get("temperature", 0.3),
        max_completion_tokens=llm_config.get("max_completion_tokens", 2000)
    )
    
    check_result = response.content
    
    return OutlineCheckOutput(outline_check_result=check_result)