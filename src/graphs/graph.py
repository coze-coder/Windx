from langgraph.graph import StateGraph, END
from graphs.state import (
    GlobalState,
    GraphInput,
    GraphOutput,
)
from graphs.nodes.plot_design_node import plot_design_node
from graphs.nodes.title_gen_node import title_gen_node
from graphs.nodes.outline_gen_node import outline_gen_node
from graphs.nodes.split_outline_node import split_outline_node
from graphs.nodes.chapter_creation_node import chapter_creation_node
from graphs.nodes.count_words_node import count_words_node


# 创建主图
builder = StateGraph(
    GlobalState,
    input_schema=GraphInput,
    output_schema=GraphOutput
)

# 添加节点
builder.add_node(
    "plot_design",
    plot_design_node,
    metadata={"type": "agent", "llm_cfg": "config/plot_design_cfg.json"}
)
builder.add_node(
    "title_gen",
    title_gen_node,
    metadata={"type": "agent", "llm_cfg": "config/title_gen_cfg.json"}
)
builder.add_node(
    "outline_gen",
    outline_gen_node,
    metadata={"type": "agent", "llm_cfg": "config/outline_gen_cfg.json"}
)
builder.add_node("split_outline", split_outline_node)
builder.add_node(
    "chapter_creation",
    chapter_creation_node,
    metadata={"type": "looparray"}
)
builder.add_node("count_words", count_words_node)

# 设置入口点
builder.set_entry_point("plot_design")

# 添加边连接节点
builder.add_edge("plot_design", "title_gen")
builder.add_edge("title_gen", "outline_gen")
builder.add_edge("outline_gen", "split_outline")
builder.add_edge("split_outline", "chapter_creation")
builder.add_edge("chapter_creation", "count_words")
builder.add_edge("count_words", END)

# 编译主图
main_graph = builder.compile()