from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import StyleInput, StyleOutput


def style_input_node(state: StyleInput, config: RunnableConfig, runtime: Runtime[Context]) -> StyleOutput:
    """
    title: 图片风格询问
    desc: 询问用户想要的图片风格，为后续文生图提示词生成做准备
    """
    ctx = runtime.context
    
    # 预定义的图片风格选项（用于引导用户选择）
    predefined_styles = [
        "写实风格（realistic）",
        "动漫风格（anime）",
        "油画风格（oil painting）",
        "水彩风格（watercolor）",
        "赛博朋克风格（cyberpunk）",
        "奇幻风格（fantasy）",
        "科幻风格（sci-fi）",
        "复古风格（retro）",
        "极简风格（minimalist）",
        "中国风（chinese style）"
    ]
    
    # 优先使用用户通过工作流参数传入的风格
    # 如果用户在调用工作流时已经指定了image_style参数，直接使用该参数
    if state.image_style and state.image_style.strip():
        user_style = state.image_style.strip()
    else:
        # 如果用户没有指定风格，使用默认推荐风格
        user_style = "写实风格（realistic），适合展现真实场景和人物细节"
    
    return StyleOutput(image_style=user_style)