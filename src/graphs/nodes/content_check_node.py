import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import ContentCheckInput, ContentCheckOutput
from coze_coding_dev_sdk.llm import LLMClient
from langchain_core.messages import SystemMessage, HumanMessage


def content_check_node(
    state: ContentCheckInput, 
    config: RunnableConfig, 
    runtime: Runtime[Context]
) -> ContentCheckOutput:
    """
    title: 章节内容检查
    desc: 检查章节内容是否与总大纲和章节大纲一致，检查上下文是否有设定、对话、剧情、场景、道具等方面的漏洞和矛盾
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH"), config['metadata']['llm_cfg'])
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        _cfg = json.load(fd)
    
    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up_tpl = Template(_cfg.get("up", ""))
    
    previous_chapters_text = state.previous_chapters if state.previous_chapters else "这是第一章，没有之前的章节内容"
    
    user_prompt = up_tpl.render({
        "overall_outline": state.overall_outline,
        "chapter_outline": state.chapter_outline,
        "current_content": state.current_content,
        "previous_chapters": previous_chapters_text,
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
        max_completion_tokens=llm_config.get("max_completion_tokens", 2500)
    )
    
    check_result = response.content
    
    return ContentCheckOutput(content_check_result=check_result)