from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import SplitOutlineOutput, AllChaptersOutput
from graphs.loop_graph import chapter_loop_graph


def chapter_creation_node(
    state: SplitOutlineOutput, config: RunnableConfig, runtime: Runtime[Context]
) -> AllChaptersOutput:
    """
    title: 章节创作
    desc: 调用子图循环创作六个章节内容
    integrations:
    """
    ctx = runtime.context

    # 准备子图输入
    parts_data = [
        {"title": state.part1_title, "requirement": state.part1_requirement},
        {"title": state.part2_title, "requirement": state.part2_requirement},
        {"title": state.part3_title, "requirement": state.part3_requirement},
        {"title": state.part4_title, "requirement": state.part4_requirement},
        {"title": state.part5_title, "requirement": state.part5_requirement},
        {"title": state.part6_title, "requirement": state.part6_requirement},
    ]

    # 调用子图进行章节创作
    result = chapter_loop_graph.invoke({"parts_data": parts_data})

    # 获取创作的章节列表
    chapters_list: list = []
    if isinstance(result, dict):
        chapters_list = result.get("chapters", [])
    elif hasattr(result, "chapters"):
        chapters_list = result.chapters

    return AllChaptersOutput(chapters=chapters_list)