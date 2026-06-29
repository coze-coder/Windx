import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from langchain_core.messages import SystemMessage, HumanMessage
from graphs.state import OutlineInput, OutlineOutput


def outline_gen_node(
    state: OutlineInput, config: RunnableConfig, runtime: Runtime[Context]
) -> OutlineOutput:
    """
    title: 大纲生成
    desc: 根据标题和情节场景创作包含六个部分的小说大纲
    integrations: 大语言模型
    """
    ctx = runtime.context

    # 读取配置文件
    cfg_file = os.path.join(
        os.getenv("COZE_WORKSPACE_PATH"), config["metadata"]["llm_cfg"]
    )
    with open(cfg_file, "r", encoding="utf-8") as fd:
        _cfg = json.load(fd)

    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")

    # 使用Jinja2模板渲染用户提示词
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render(
        {"novel_title": state.novel_title, "plot_scenes": state.plot_scenes}
    )

    # 初始化LLM客户端
    client = LLMClient(ctx=ctx)

    # 组装消息
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt_content),
    ]

    # 调用大模型
    response = client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-1-8-251228"),
        temperature=llm_config.get("temperature", 0.8),
        max_completion_tokens=llm_config.get("max_completion_tokens", 32768),
    )

    # 处理响应内容
    content = response.content
    if isinstance(content, str):
        novel_outline = content.strip()
    elif isinstance(content, list):
        novel_outline = " ".join(
            item.get("text", "") for item in content if isinstance(item, dict)
        ).strip()
    else:
        novel_outline = str(content)

    return OutlineOutput(novel_outline=novel_outline)