import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import ChapterOutlineGenInput, ChapterOutlineGenOutput
from coze_coding_dev_sdk.llm import LLMClient
from langchain_core.messages import SystemMessage, HumanMessage


def chapter_outline_gen_node(
    state: ChapterOutlineGenInput, 
    config: RunnableConfig, 
    runtime: Runtime[Context]
) -> ChapterOutlineGenOutput:
    """
    title: 章节大纲生成
    desc: 根据总大纲的当前部分标题和要求，生成该章节的详细大纲，包含场景划分、人物安排、情节推进等细节
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
        "current_title": state.current_title,
        "target_word_count": state.target_word_count
    })
    
    client = LLMClient(ctx=ctx)
    
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt),
    ]
    
    response = client.invoke(
        messages=messages,
        model=llm_config.get("model"),
        temperature=llm_config.get("temperature", 0.7),
        max_completion_tokens=llm_config.get("max_completion_tokens", 3000)
    )
    
    chapter_outline = response.content
    
    return ChapterOutlineGenOutput(chapter_outline=chapter_outline)