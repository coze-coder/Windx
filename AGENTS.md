## 项目概述
- **名称**: 万字小说创作工作流
- **功能**: 根据用户需求自动创作完整的万字小说，包括情节设计、标题生成、大纲创作、章节撰写和字数统计

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|---------|---------|---------|
| plot_design | `nodes/plot_design_node.py` | agent | 根据用户需求设计六个主要情节场景 | - | `config/plot_design_cfg.json` |
| title_gen | `nodes/title_gen_node.py` | agent | 根据情节场景生成小说标题 | - | `config/title_gen_cfg.json` |
| outline_gen | `nodes/outline_gen_node.py` | agent | 根据标题和情节创作六部分大纲 | - | `config/outline_gen_cfg.json` |
| split_outline | `nodes/split_outline_node.py` | task | 从完整大纲提取各部分标题和要求 | - | - |
| chapter_creation | `nodes/chapter_creation_node.py` | looparray | 循环创作六个章节内容 | - | - |
| count_words | `nodes/count_words_node.py` | task | 统计所有章节的中文字符总数 | - | - |

**类型说明**: task(task节点) / agent(大模型) / condition(条件分支) / looparray(列表循环) / loopcond(条件循环)

## 子图清单
| 子图名 | 文件位置 | 功能描述 | 被调用节点 |
|-------|---------|------|---------|
| chapter_loop_graph | `graphs/loop_graph.py` | 循环创作六个章节 | chapter_creation |

## 技能使用
- 节点 `plot_design` 使用大语言模型技能
- 节点 `title_gen` 使用大语言模型技能
- 节点 `outline_gen` 使用大语言模型技能
- 子图中的单章节创作节点使用大语言模型技能

## 工作流程
1. **输入**: 用户小说创作需求（包括角色性格、背景信息等）
2. **情节设计**: 设计六个主要情节场景，每个场景包含时间、地点、人物、事件、结果
3. **标题生成**: 根据情节场景创作简洁有力的小说标题
4. **大纲生成**: 创作包含六个部分的大纲，每部分有标题和编写要求
5. **拆分大纲**: 提取大纲中各部分的标题和要求
6. **章节创作**: 循环创作六个章节内容（调用子图）
7. **统计字数**: 统计所有章节的中文字符总数
8. **输出**: 小说标题、情节场景、大纲、六个章节内容、总字数

## 配置文件说明
所有大模型配置文件位于 `config/` 目录：
- `plot_design_cfg.json`: 情节设计节点配置
- `title_gen_cfg.json`: 标题生成节点配置
- `outline_gen_cfg.json`: 大纲生成节点配置
- `chapter_creation_cfg.json`: 单章节创作节点配置（在子图中使用）

每个配置文件包含：
- `config`: 模型参数（model、temperature、max_completion_tokens等）
- `sp`: 系统提示词（System Prompt）
- `up`: 用户提示词模板（User Prompt，支持Jinja2模板）
- `tools`: 工具列表（本工作流无工具调用，均为空数组）