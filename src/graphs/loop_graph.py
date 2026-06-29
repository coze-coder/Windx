from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
import os
import json
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from langchain_core.messages import SystemMessage, HumanMessage


class ChapterLoopState(BaseModel):
    """章节创作循环子图的状态"""
    parts_data: List[Dict[str, str]] = Field(default=[], description="六个部分的数据列表")
    current_part: Dict[str, str] = Field(default={}, description="当前正在处理的章节")
    chapters: List[str] = Field(default=[], description="已创作的章节列表")
    current_index: int = Field(default=0, description="当前循环索引")


class ChapterLoopInput(BaseModel):
    """循环子图输入"""
    parts_data: List[Dict[str, str]] = Field(..., description="六个部分的数据列表")


class ChapterLoopOutput(BaseModel):
    """循环子图输出"""
    chapters: List[str] = Field(..., description="创作的六个章节内容")


class SingleChapterInput(BaseModel):
    """单个章节创作输入"""
    part_title: str = Field(..., description="章节标题")
    part_requirement: str = Field(..., description="编写要求")


class SingleChapterOutput(BaseModel):
    """单个章节创作输出"""
    chapter_content: str = Field(..., description="章节内容")


def single_chapter_creation_node(
    state: SingleChapterInput, config: RunnableConfig, runtime: Runtime[Context]
) -> SingleChapterOutput:
    """
    title: 单章节创作
    desc: 创作单个章节的完整内容
    integrations: 大语言模型
    """
    ctx = runtime.context

    # 读取配置文件
    cfg_file = os.path.join(
        os.getenv("COZE_WORKSPACE_PATH"), "config/chapter_creation_cfg.json"
    )
    with open(cfg_file, "r", encoding="utf-8") as fd:
        _cfg = json.load(fd)

    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")

    # 使用Jinja2模板渲染用户提示词
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render(
        {
            "part_title": state.part_title,
            "part_requirement": state.part_requirement,
            "full_outline": "大纲内容在主图中已确定",
        }
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
        temperature=llm_config.get("temperature", 0.9),
        max_completion_tokens=llm_config.get("max_completion_tokens", 32768),
    )

    # 处理响应内容
    content = response.content
    if isinstance(content, str):
        chapter_content = content.strip()
    elif isinstance(content, list):
        chapter_content = " ".join(
            item.get("text", "") for item in content if isinstance(item, dict)
        ).strip()
    else:
        chapter_content = str(content)

    return SingleChapterOutput(chapter_content=chapter_content)


def init_loop_node(state: ChapterLoopInput, config: RunnableConfig, runtime: Runtime[Context]) -> ChapterLoopState:
    """初始化循环状态"""
    return ChapterLoopState(
        parts_data=state.parts_data,
        current_part=state.parts_data[0] if state.parts_data else {},
        chapters=[],
        current_index=0
    )


def create_single_chapter(state: ChapterLoopState, config: RunnableConfig, runtime: Runtime[Context]) -> ChapterLoopState:
    """创作单个章节"""
    ctx = runtime.context
    
    # 构造单个章节输入
    chapter_input = SingleChapterInput(
        part_title=state.current_part.get("title", ""),
        part_requirement=state.current_part.get("requirement", "")
    )
    
    # 调用单章节创作节点
    result = single_chapter_creation_node(chapter_input, config, runtime)
    
    # 更新状态
    new_chapters = state.chapters + [result.chapter_content]
    new_index = state.current_index + 1
    
    if new_index < len(state.parts_data):
        next_part = state.parts_data[new_index]
    else:
        next_part = {}
    
    return ChapterLoopState(
        parts_data=state.parts_data,
        current_part=next_part,
        chapters=new_chapters,
        current_index=new_index
    )


def should_continue(state: ChapterLoopState) -> str:
    """判断是否继续循环"""
    if state.current_index < len(state.parts_data):
        return "继续创作"
    else:
        return "结束"


# 创建循环子图
loop_builder = StateGraph(
    ChapterLoopState,
    input_schema=ChapterLoopInput,
    output_schema=ChapterLoopOutput
)

# 添加节点
loop_builder.add_node("init_loop", init_loop_node)
loop_builder.add_node("create_chapter", create_single_chapter)

# 设置入口
loop_builder.set_entry_point("init_loop")
loop_builder.add_edge("init_loop", "create_chapter")

# 添加条件分支
loop_builder.add_conditional_edges(
    source="create_chapter",
    path=should_continue,
    path_map={
        "继续创作": "create_chapter",
        "结束": END
    }
)

# 编译子图
chapter_loop_graph = loop_builder.compile()