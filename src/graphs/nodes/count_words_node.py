import re
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import CountWordsInput, CountWordsOutput


def count_words_node(
    state: CountWordsInput, config: RunnableConfig, runtime: Runtime[Context]
) -> CountWordsOutput:
    """
    title: 统计字数
    desc: 统计所有章节的中文字符总数
    integrations:
    """
    ctx = runtime.context

    # 合并所有章节内容
    chapters = [
        state.chapter1,
        state.chapter2,
        state.chapter3,
        state.chapter4,
        state.chapter5,
        state.chapter6,
    ]

    combined_text = "".join(chapters)

    # 使用正则匹配中文字符
    chinese_chars = re.findall(r"[\u4e00-\u9fa5]", combined_text)

    # 计算总字数
    total_count = len(chinese_chars)

    return CountWordsOutput(total_word_count=total_count)