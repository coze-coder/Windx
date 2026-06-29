## 项目概述
- **名称**: 万字小说创作工作流（增强版）
- **功能**: 根据用户需求自动创作完整的万字小说，支持用户自定义字数（不超过150万字）、章节创作过程中的用户交互确认

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|---------|---------|---------|
| plot_design | `nodes/plot_design_node.py` | agent | 根据用户需求设计六个主要情节场景 | - | `config/plot_design_cfg.json` |
| title_gen | `nodes/title_gen_node.py` | agent | 根据情节场景生成小说标题 | - | `config/title_gen_cfg.json` |
| outline_gen | `nodes/outline_gen_node.py` | agent | 根据标题和情节创作六部分大纲，支持字数限制检查 | - | `config/outline_gen_cfg.json` |
| split_outline | `nodes/split_outline_node.py` | task | 从完整大纲提取各部分标题和要求 | - | - |
| chapter_creation | `nodes/chapter_creation_node.py` | looparray | 循环创作六个章节内容，支持用户交互确认 | - | - |
| count_words | `nodes/count_words_node.py` | task | 统计所有章节的中文字符总数 | - | - |

**类型说明**: task(task节点) / agent(大模型) / condition(条件分支) / looparray(列表循环) / loopcond(条件循环)

## 子图清单
| 子图名 | 文件位置 | 功能描述 | 被调用节点 |
|-------|---------|------|---------|
| chapter_loop_graph | `graphs/loop_graph.py` | 循环创作六个章节，每章创作后添加用户交互确认节点 | chapter_creation |

子图包含以下节点：
- create_single_chapter: 单章节创作节点（agent类型）
- user_interaction: 用户交互确认节点（task类型）
- should_continue: 条件判断节点（condition类型）

## 技能使用
- 节点 `plot_design` 使用大语言模型技能（DeepSeek）
- 节点 `title_gen` 使用大语言模型技能（DeepSeek）
- 节点 `outline_gen` 使用大语言模型技能（DeepSeek）
- 子图中的单章节创作节点使用大语言模型技能（DeepSeek）

## 工作流程
1. **输入**: 用户小说创作需求（包括角色性格、背景信息等）和目标字数（不超过150万字）
2. **字数验证**: 检查用户输入的字数是否超过150万字上限，超过则自动调整
3. **情节设计**: 设计六个主要情节场景，每个场景包含时间、地点、人物、事件、结果
4. **标题生成**: 根据情节场景创作简洁有力的小说标题
5. **大纲生成**: 创作包含六个部分的大纲，每部分有标题和编写要求，字数分配根据用户设定
6. **拆分大纲**: 提取大纲中各部分的标题和要求
7. **章节创作**: 循环创作六个章节内容（调用子图）
   - 每创作完一个章节后，暂停等待用户交互确认
   - 用户可提供反馈意见，确认是否需要修改
   - 根据用户反馈决定继续创作或重新创作当前章节
8. **统计字数**: 统计所有章节的中文字符总数
9. **输出**: 小说标题、情节场景、大纲、六个章节内容、总字数

## 新增功能说明
### 1. 字数限制验证
- 用户可以手动输入目标字数
- 系统自动验证字数不超过150万字
- 超过上限时自动调整并提示用户

### 2. 用户交互确认
- 每章创作完成后暂停工作流
- 等待用户确认并提供反馈意见
- 用户可以要求重新创作当前章节
- 确认无误后继续创作下一章节

### 3. DeepSeek模型配置
- 所有Agent节点使用DeepSeek模型（deepseek-v3-2-251201）
- 系统提示词包含完整的思考协议（Anthropic Thinking Protocol）
- 支持更深度、更自然的思考过程

## 配置文件说明
所有大模型配置文件位于 `config/` 目录：
- `plot_design_cfg.json`: 情节设计节点配置（DeepSeek + 思考协议）
- `title_gen_cfg.json`: 标题生成节点配置（DeepSeek + 思考协议）
- `outline_gen_cfg.json`: 大纲生成节点配置（DeepSeek + 思考协议）
- `chapter_creation_cfg.json`: 单章节创作节点配置（DeepSeek + 思考协议）

每个配置文件包含：
- `config`: 模型参数（model=deepseek-v3-2-251201、temperature、max_completion_tokens等）
- `sp`: 系统提示词（包含Anthropic Thinking Protocol）
- `up`: 用户提示词模板（User Prompt，支持Jinja2模板）
- `tools`: 工具列表（本工作流无工具调用，均为空数组）

## 状态定义说明
在 `src/graphs/state.py` 中定义了以下状态类型：
- `GlobalState`: 全局状态，包含所有中间结果和用户输入
- `GraphInput`: 工作流输入（user_requirement + target_word_count）
- `GraphOutput`: 工作流输出（novel_title + plot_scenes + novel_outline + chapters + total_word_count）
- 各节点的独立Input/Output类型，确保最小化范围原则