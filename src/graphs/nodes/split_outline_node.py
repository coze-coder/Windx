import re
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import SplitOutlineInput, SplitOutlineOutput


def split_outline_node(
    state: SplitOutlineInput, config: RunnableConfig, runtime: Runtime[Context]
) -> SplitOutlineOutput:
    """
    title: 拆分大纲
    desc: 从完整大纲文本中提取各部分的标题和编写要求
    integrations:
    """
    ctx = runtime.context

    input_text = state.novel_outline

    # 定义提取函数
    def extract_text(text: str, keyword: str) -> str:
        # 匹配多种情况：中英文冒号或等号
        pattern = re.compile(
            rf"{keyword}\s*[：:=]\s*([^第\n]+(?:\n(?![第])[^\n]+)*)", re.MULTILINE
        )
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
        return ""

    # 提取各个部分
    part1_title = extract_text(input_text, "第一部分大纲标题")
    part1_requirement = extract_text(input_text, "第一部分编写要求")
    part2_title = extract_text(input_text, "第二部分大纲标题")
    part2_requirement = extract_text(input_text, "第二部分编写要求")
    part3_title = extract_text(input_text, "第三部分大纲标题")
    part3_requirement = extract_text(input_text, "第三部分编写要求")
    part4_title = extract_text(input_text, "第四部分大纲标题")
    part4_requirement = extract_text(input_text, "第四部分编写要求")
    part5_title = extract_text(input_text, "第五部分大纲标题")
    part5_requirement = extract_text(input_text, "第五部分编写要求")
    part6_title = extract_text(input_text, "第六部分大纲标题")
    part6_requirement = extract_text(input_text, "第六部分编写要求")

    return SplitOutlineOutput(
        novel_outline=state.novel_outline,
        target_word_count=state.target_word_count,
        part1_title=part1_title,
        part1_requirement=part1_requirement,
        part2_title=part2_title,
        part2_requirement=part2_requirement,
        part3_title=part3_title,
        part3_requirement=part3_requirement,
        part4_title=part4_title,
        part4_requirement=part4_requirement,
        part5_title=part5_title,
        part5_requirement=part5_requirement,
        part6_title=part6_title,
        part6_requirement=part6_requirement,
    )