import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from langchain_core.messages import SystemMessage, HumanMessage
from graphs.state import PlotInput, PlotOutput


def plot_design_node(
    state: PlotInput, config: RunnableConfig, runtime: Runtime[Context]
) -> PlotOutput:
    """
    title: 情节设计
    desc: 根据用户需求设计六个主要情节场景，包括时间、地点、人物、事件和结果
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
    user_prompt_content = up_tpl.render({"user_requirement": state.user_requirement})

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
        temperature=llm_config.get("temperature", 0.9),
        max_completion_tokens=llm_config.get("max_completion_tokens", 32768),
    )

    # 处理响应内容
    content = response.content
    if isinstance(content, str):
        plot_scenes = content.strip()
    elif isinstance(content, list):
        plot_scenes = " ".join(
            item.get("text", "") for item in content if isinstance(item, dict)
        ).strip()
    else:
        plot_scenes = str(content)

    return PlotOutput(plot_scenes=plot_scenes)