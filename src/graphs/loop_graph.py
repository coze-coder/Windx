from typing import List, Dict
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

# 导入新的检查节点
from graphs.nodes.chapter_outline_gen_node import chapter_outline_gen_node
from graphs.nodes.outline_check_node import outline_check_node
from graphs.nodes.content_check_node import content_check_node


class ChapterLoopState(BaseModel):
    """章节创作循环子图的状态"""
    parts_data: List[Dict[str, str]] = Field(default=[], description="六个部分的数据列表")
    current_part: Dict[str, str] = Field(default={}, description="当前正在处理的章节")
    chapters: List[str] = Field(default=[], description="已创作的章节列表")
    current_index: int = Field(default=0, description="当前循环索引")
    user_feedback: str = Field(default="", description="用户对当前章节的反馈意见")
    needs_revision: bool = Field(default=False, description="是否需要根据反馈重新创作")
    overall_outline: str = Field(default="", description="小说总大纲")
    target_word_count: int = Field(default=15000, description="总字数目标")
    chapter_outline: str = Field(default="", description="当前章节的大纲")
    outline_check_result: str = Field(default="", description="章节大纲检查结果")
    content_check_result: str = Field(default="", description="章节内容检查结果")


class ChapterLoopInput(BaseModel):
    """循环子图输入"""
    parts_data: List[Dict[str, str]] = Field(..., description="六个部分的数据列表")
    overall_outline: str = Field(..., description="小说总大纲")
    target_word_count: int = Field(..., description="总字数目标")


class ChapterLoopOutput(BaseModel):
    """循环子图输出"""
    chapters: List[str] = Field(..., description="创作的六个章节内容")


class SingleChapterInput(BaseModel):
    """单个章节创作输入"""
    part_title: str = Field(..., description="章节标题")
    part_requirement: str = Field(..., description="编写要求")
    user_feedback: str = Field(default="", description="用户反馈意见（可选）")


class SingleChapterOutput(BaseModel):
    """单个章节创作输出"""
    chapter_content: str = Field(..., description="章节内容")


class UserFeedbackInput(BaseModel):
    """用户反馈输入"""
    chapter_content: str = Field(..., description="当前创作的章节内容")
    chapter_index: int = Field(..., description="章节索引")


class UserFeedbackOutput(BaseModel):
    """用户反馈输出"""
    user_feedback: str = Field(default="", description="用户反馈意见")
    needs_revision: bool = Field(default=False, description="是否需要修改")


def single_chapter_creation_node(
    state: SingleChapterInput, config: RunnableConfig, runtime: Runtime[Context]
) -> SingleChapterOutput:
    """
    title: 单章节创作
    desc: 创作单个章节的完整内容，可根据用户反馈调整
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

    # 构造用户反馈提示文本
    user_feedback_text = ""
    if state.user_feedback and state.user_feedback.strip():
        user_feedback_text = f"\n用户反馈意见：{state.user_feedback}\n请根据以上反馈意见调整创作内容。"

    # 使用Jinja2模板渲染用户提示词
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render(
        {
            "part_title": state.part_title,
            "part_requirement": state.part_requirement,
            "full_outline": "大纲内容在主图中已确定",
            "user_feedback_text": user_feedback_text,
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
        model=llm_config.get("model", "deepseek-v3-2-251201"),
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


def user_interaction_node(
    state: ChapterLoopState, config: RunnableConfig, runtime: Runtime[Context]
) -> ChapterLoopState:
    """
    title: 用户交互确认
    desc: 等待用户确认当前章节并提供反馈意见
    integrations:
    """
    ctx = runtime.context
    
    # 在实际运行中，这里应该通过某种机制（如interrupt）暂停工作流
    # 等待用户输入反馈意见
    # 这里我们简化处理：如果GlobalState中有user_feedback，则使用它
    # 否则默认为确认通过
    
    # 由于LangGraph的工作流特性，这里我们采用简化方案：
    # 通过条件判断是否需要用户交互
    # 如果是第一次运行，默认需要用户确认（但实际中无法暂停）
    # 所以这里我们返回状态，让条件节点判断
    
    # 记录用户交互信息（使用简单的文本记录）
    
    return ChapterLoopState(
        parts_data=state.parts_data,
        current_part=state.current_part,
        chapters=state.chapters,
        current_index=state.current_index,
        user_feedback=state.user_feedback,
        needs_revision=False  # 默认不需要修改，除非用户提供了反馈
    )


def init_loop_node(
    state: ChapterLoopInput, config: RunnableConfig, runtime: Runtime[Context]
) -> ChapterLoopState:
    """初始化循环状态"""
    return ChapterLoopState(
        parts_data=state.parts_data,
        current_part=state.parts_data[0] if state.parts_data else {},
        chapters=[],
        current_index=0,
        user_feedback="",
        needs_revision=False,
        overall_outline=state.overall_outline,
        target_word_count=state.target_word_count,
        chapter_outline="",
        outline_check_result="",
        content_check_result="",
    )


def create_single_chapter(
    state: ChapterLoopState, config: RunnableConfig, runtime: Runtime[Context]
) -> ChapterLoopState:
    """创作单个章节"""
    ctx = runtime.context

    # 构造单个章节输入
    chapter_input = SingleChapterInput(
        part_title=state.current_part.get("title", ""),
        part_requirement=state.current_part.get("requirement", ""),
        user_feedback=state.user_feedback if state.needs_revision else "",
    )

    # 调用单章节创作节点
    result = single_chapter_creation_node(chapter_input, config, runtime)

    # 更新状态
    new_chapters = state.chapters + [result.chapter_content]
    new_index = state.current_index

    return ChapterLoopState(
        parts_data=state.parts_data,
        current_part=state.current_part,
        chapters=new_chapters,
        current_index=new_index,
        user_feedback="",  # 清空用户反馈
        needs_revision=False,
    )


def check_user_feedback(state: ChapterLoopState) -> str:
    """判断是否需要根据用户反馈重新创作"""
    # 如果用户提供了反馈且需要修改，则重新创作
    if state.needs_revision and state.user_feedback.strip():
        return "根据反馈重新创作"
    else:
        return "继续下一章节"


def move_to_next_chapter(
    state: ChapterLoopState, config: RunnableConfig, runtime: Runtime[Context]
) -> ChapterLoopState:
    """移动到下一个章节"""
    new_index = state.current_index + 1

    if new_index < len(state.parts_data):
        next_part = state.parts_data[new_index]
    else:
        next_part = {}

    return ChapterLoopState(
        parts_data=state.parts_data,
        current_part=next_part,
        chapters=state.chapters,
        current_index=new_index,
        user_feedback="",
        needs_revision=False,
        overall_outline=state.overall_outline,
        target_word_count=state.target_word_count,
        chapter_outline="",  # 清空章节大纲，准备生成新章节的大纲
        outline_check_result="",  # 清空检查结果
        content_check_result="",  # 清空检查结果
    )


def generate_chapter_outline(
    state: ChapterLoopState, config: RunnableConfig, runtime: Runtime[Context]
) -> ChapterLoopState:
    """生成章节大纲"""
    ctx = runtime.context
    
    # 构造输入数据
    from graphs.state import ChapterOutlineGenInput
    outline_input = ChapterOutlineGenInput(
        overall_outline=state.overall_outline,
        current_title=state.current_part.get("title", ""),
        target_word_count=state.target_word_count,
    )
    
    # 创建包含metadata的config
    outline_config = RunnableConfig(
        metadata={"llm_cfg": "config/chapter_outline_gen_cfg.json"}
    )
    
    # 调用章节大纲生成节点
    result = chapter_outline_gen_node(outline_input, outline_config, runtime)
    
    # 更新状态
    return ChapterLoopState(
        parts_data=state.parts_data,
        current_part=state.current_part,
        chapters=state.chapters,
        current_index=state.current_index,
        user_feedback=state.user_feedback,
        needs_revision=state.needs_revision,
        overall_outline=state.overall_outline,
        target_word_count=state.target_word_count,
        chapter_outline=result.chapter_outline,
        outline_check_result=state.outline_check_result,
        content_check_result=state.content_check_result,
    )


def check_outline_consistency(
    state: ChapterLoopState, config: RunnableConfig, runtime: Runtime[Context]
) -> ChapterLoopState:
    """检查章节大纲一致性"""
    ctx = runtime.context
    
    # 构造输入数据
    from graphs.state import OutlineCheckInput
    check_input = OutlineCheckInput(
        overall_outline=state.overall_outline,
        chapter_outline=state.chapter_outline,
        current_title=state.current_part.get("title", ""),
    )
    
    # 创建包含metadata的config
    check_config = RunnableConfig(
        metadata={"llm_cfg": "config/outline_check_cfg.json"}
    )
    
    # 调用大纲检查节点
    result = outline_check_node(check_input, check_config, runtime)
    
    # 更新状态
    return ChapterLoopState(
        parts_data=state.parts_data,
        current_part=state.current_part,
        chapters=state.chapters,
        current_index=state.current_index,
        user_feedback=state.user_feedback,
        needs_revision=state.needs_revision,
        overall_outline=state.overall_outline,
        target_word_count=state.target_word_count,
        chapter_outline=state.chapter_outline,
        outline_check_result=result.outline_check_result,
        content_check_result=state.content_check_result,
    )


def check_content_consistency(
    state: ChapterLoopState, config: RunnableConfig, runtime: Runtime[Context]
) -> ChapterLoopState:
    """检查章节内容一致性"""
    ctx = runtime.context
    
    # 获取最新创作的章节内容
    current_content = state.chapters[-1] if state.chapters else ""
    
    # 获取前文内容（之前所有章节）
    previous_chapters = "\n\n".join(state.chapters[:-1]) if len(state.chapters) > 1 else ""
    
    # 构造输入数据
    from graphs.state import ContentCheckInput
    check_input = ContentCheckInput(
        overall_outline=state.overall_outline,
        chapter_outline=state.chapter_outline,
        current_content=current_content,
        previous_chapters=previous_chapters,
        current_title=state.current_part.get("title", ""),
    )
    
    # 创建包含metadata的config
    check_config = RunnableConfig(
        metadata={"llm_cfg": "config/content_check_cfg.json"}
    )
    
    # 调用内容检查节点
    result = content_check_node(check_input, check_config, runtime)
    
    # 更新状态
    return ChapterLoopState(
        parts_data=state.parts_data,
        current_part=state.current_part,
        chapters=state.chapters,
        current_index=state.current_index,
        user_feedback=state.user_feedback,
        needs_revision=state.needs_revision,
        overall_outline=state.overall_outline,
        target_word_count=state.target_word_count,
        chapter_outline=state.chapter_outline,
        outline_check_result=state.outline_check_result,
        content_check_result=result.content_check_result,
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
    output_schema=ChapterLoopOutput,
)

# 添加节点
loop_builder.add_node("init_loop", init_loop_node)
loop_builder.add_node("generate_outline", generate_chapter_outline)
loop_builder.add_node("check_outline", check_outline_consistency)
loop_builder.add_node("create_chapter", create_single_chapter)
loop_builder.add_node("check_content", check_content_consistency)
loop_builder.add_node("user_interaction", user_interaction_node)
loop_builder.add_node("move_next", move_to_next_chapter)

# 设置入口
loop_builder.set_entry_point("init_loop")
loop_builder.add_edge("init_loop", "generate_outline")

# 章节大纲生成后检查一致性
loop_builder.add_edge("generate_outline", "check_outline")

# 大纲检查后创作章节
loop_builder.add_edge("check_outline", "create_chapter")

# 章节创作后检查内容一致性
loop_builder.add_edge("create_chapter", "check_content")

# 内容检查后进行用户交互确认
loop_builder.add_edge("check_content", "user_interaction")

# 根据用户反馈判断下一步
loop_builder.add_conditional_edges(
    source="user_interaction",
    path=check_user_feedback,
    path_map={
        "根据反馈重新创作": "create_chapter",
        "继续下一章节": "move_next",
    },
)

# 移动到下一章节后判断是否继续
loop_builder.add_conditional_edges(
    source="move_next",
    path=should_continue,
    path_map={
        "继续创作": "generate_outline",
        "结束": END,
    },
)

# 编译子图
chapter_loop_graph = loop_builder.compile()