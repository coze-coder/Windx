## 项目概述
- **名称**: 万字小说创作工作流（完整版）
- **功能**: 根据用户需求自动创作完整的万字小说，支持用户自定义字数（不超过150万字）、章节创作过程中的用户交互确认、文生图提示词生成、上下文一致性检查

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|---------|---------|---------|
| plot_design | `nodes/plot_design_node.py` | agent | 根据用户需求设计六个主要情节场景 | - | `config/plot_design_cfg.json` |
| title_gen | `nodes/title_gen_node.py` | agent | 根据情节场景生成小说标题 | - | `config/title_gen_cfg.json` |
| style_input | `nodes/style_input_node.py` | task | 接收用户指定的图片风格（从GraphInput传入） | - | - |
| image_prompt_gen | `nodes/image_prompt_gen_node.py` | agent | 根据标题和风格生成适用于多个模型的文生图提示词（比例3:4，突出标题） | - | `config/image_prompt_gen_cfg.json` |
| outline_gen | `nodes/outline_gen_node.py` | agent | 根据标题和情节创作六部分大纲，支持字数限制检查 | - | `config/outline_gen_cfg.json` |
| split_outline | `nodes/split_outline_node.py` | task | 从完整大纲提取各部分标题和要求，传递总大纲和字数信息 | - | - |
| chapter_creation | `nodes/chapter_creation_node.py` | looparray | 循环创作六个章节内容，支持用户交互确认和上下文检查 | - | - |
| count_words | `nodes/count_words_node.py` | task | 统计所有章节的中文字符总数 | - | - |

**子图新增节点（用于上下文检查）**：
| chapter_outline_gen | `nodes/chapter_outline_gen_node.py` | agent | 根据总大纲生成当前章节的详细大纲 | - | `config/chapter_outline_gen_cfg.json` |
| outline_check | `nodes/outline_check_node.py` | agent | 检查章节大纲与总大纲的一致性 | - | `config/outline_check_cfg.json` |
| content_check | `nodes/content_check_node.py` | agent | 检查章节内容与大纲的一致性及上下文连贯性 | - | `config/content_check_cfg.json` |

**类型说明**: task(task节点) / agent(大模型) / condition(条件分支) / looparray(列表循环) / loopcond(条件循环)

## 子图清单
| 子图名 | 文件位置 | 功能描述 | 被调用节点 |
|-------|---------|------|---------|
| chapter_loop_graph | `graphs/loop_graph.py` | 循环创作六个章节，包含章节大纲生成、一致性检查、内容创作、内容检查、用户交互确认 | chapter_creation |

子图包含以下节点：
- generate_chapter_outline: 章节大纲生成节点（agent类型）
- check_outline_consistency: 章节大纲检查节点（agent类型）
- create_single_chapter: 单章节创作节点（agent类型）
- check_content_consistency: 章节内容检查节点（agent类型）
- user_interaction: 用户交互确认节点（task类型）
- should_continue: 条件判断节点（condition类型）

## 技能使用
- 节点 `plot_design` 使用大语言模型技能（DeepSeek）
- 节点 `title_gen` 使用大语言模型技能（DeepSeek）
- 节点 `image_prompt_gen` 使用大语言模型技能（DeepSeek）
- 节点 `outline_gen` 使用大语言模型技能（DeepSeek）
- 子图中的单章节创作节点使用大语言模型技能（DeepSeek）
- 子图中的章节大纲生成节点使用大语言模型技能（DeepSeek）
- 子图中的章节大纲检查节点使用大语言模型技能（DeepSeek）
- 子图中的章节内容检查节点使用大语言模型技能（DeepSeek）

## 工作流程
1. **输入**: 用户小说创作需求（包括角色性格、背景信息等）、目标字数（不超过150万字）、图片风格
2. **字数验证**: 检查用户输入的字数是否超过150万字上限，超过则自动调整
3. **情节设计**: 设计六个主要情节场景，每个场景包含时间、地点、人物、事件、结果
4. **标题生成**: 根据情节场景创作简洁有力的小说标题
5. **风格确认**: 接收用户指定的图片风格（从GraphInput的image_style字段传入）
6. **提示词生成**: 根据标题和风格生成适用于多个模型的文生图提示词
   - 支持模型：image2.0、香蕉、豆包等主流模型
   - 图片比例：固定为3:4竖版构图
   - 突出标题：在提示词中强调小说标题的视觉呈现
7. **大纲生成**: 创作包含六个部分的大纲，每部分有标题和编写要求，字数分配根据用户设定
8. **拆分大纲**: 提取大纲中各部分的标题和要求
9. **章节创作**: 循环创作六个章节内容（调用子图）
   - **章节大纲生成**: 为每个章节生成详细的章节大纲（包含场景划分、人物安排、情节推进）
   - **大纲一致性检查**: 对比章节大纲与总大纲，检查主题、人物、情节、设定、风格的一致性
   - **章节内容创作**: 根据章节大纲创作详细的章节内容
   - **内容一致性检查**: 检查章节内容是否与总大纲和章节大纲保持一致，同时检查跨章节的上下文连贯性
     - 设定检查：背景、环境、道具、人物设定是否一致
     - 对话检查：对话风格、人物语言习惯是否一致
     - 剧情检查：情节推进是否合理、是否有逻辑漏洞
     - 场景检查：场景描写是否完整、是否有时空混乱
     - 道具检查：道具使用是否合理、是否有前后矛盾
     - 上下文连贯：与前文的情节衔接、人物状态、时间线是否连贯
   - **用户交互确认**: 每创作完一个章节后，暂停等待用户交互确认
   - 用户可提供反馈意见，确认是否需要修改
   - 根据用户反馈决定继续创作或重新创作当前章节
10. **统计字数**: 统计所有章节的中文字符总数
11. **输出**: 小说标题、情节场景、图片提示词、大纲、六个章节内容、总字数

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

### 3. 文生图提示词生成
- 根据小说标题和用户指定的图片风格生成提示词
- 适用于多个主流模型：image2.0、香蕉、豆包等
- 图片比例固定为3:4竖版构图
- 突出小说标题的视觉呈现
- 提示词包含场景描述、色调、构图、氛围等完整要素

### 4. DeepSeek模型配置
- 所有Agent节点使用DeepSeek模型（deepseek-v3-2-251201）
- 系统提示词包含完整的思考协议（Anthropic Thinking Protocol）
- 支持更深度、更自然的思考过程

### 5. 上下文一致性检查
- **章节大纲生成**：每章创作前根据总大纲生成详细的章节大纲
  - 包含场景划分（3-5个场景）、人物安排、情节推进
  - 确保章节大纲与总大纲的主题、风格、人物设定保持一致
  - 控制场景数量和细节程度，符合目标字数要求
  
- **大纲一致性检查**：对比章节大纲与总大纲
  - 检查维度：主题、人物、情节、设定、风格五个维度
  - 给出一致性评分（0-100分）和具体的偏离点列表
  - 为每个偏离点提供修改建议
  
- **内容一致性检查**：检查章节内容质量
  - 检查章节内容是否与总大纲和章节大纲保持一致
  - 检查跨章节的上下文连贯性（设定、对话、剧情、场景、道具）
  - 检查与前文的情节衔接、人物状态、时间线是否连贯
  - 给出一致性评分（0-100分）和具体漏洞列表
  - 为每个漏洞提供修改建议

## 配置文件说明
所有大模型配置文件位于 `config/` 目录：
- `plot_design_cfg.json`: 情节设计节点配置（DeepSeek + 思考协议）
- `title_gen_cfg.json`: 标题生成节点配置（DeepSeek + 思考协议）
- `image_prompt_gen_cfg.json`: 提示词生成节点配置（DeepSeek + 思考协议）
- `outline_gen_cfg.json`: 大纲生成节点配置（DeepSeek + 思考协议）
- `chapter_creation_cfg.json`: 单章节创作节点配置（DeepSeek + 思考协议）
- `chapter_outline_gen_cfg.json`: 章节大纲生成节点配置（DeepSeek + 思考协议，temperature=0.7）
- `outline_check_cfg.json`: 大纲一致性检查节点配置（DeepSeek + 思考协议，temperature=0.3）
- `content_check_cfg.json`: 内容一致性检查节点配置（DeepSeek + 思考协议，temperature=0.3）

每个配置文件包含：
- `config`: 模型参数（model=deepseek-v3-2-251201、temperature、max_completion_tokens等）
- `sp`: 系统提示词（包含Anthropic Thinking Protocol）
- `up`: 用户提示词模板（User Prompt，支持Jinja2模板）
- `tools`: 工具列表（本工作流无工具调用，均为空数组）

## 状态定义说明
在 `src/graphs/state.py` 中定义了以下状态类型：
- `GlobalState`: 全局状态，包含所有中间结果和用户输入（新增image_style和image_prompt字段）
- `GraphInput`: 工作流输入（user_requirement + target_word_count + image_style）
- `GraphOutput`: 工作流输出（novel_title + plot_scenes + image_prompt + novel_outline + chapters + total_word_count）
- 各节点的独立Input/Output类型，确保最小化范围原则