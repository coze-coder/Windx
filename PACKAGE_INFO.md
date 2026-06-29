# 扣子工作流打包文件说明

## 📦 打包文件信息

**文件名**: `coze_workflow_package.tar.gz`
**大小**: 30KB
**创建时间**: 2025年6月29日 17:17

## 📋 打包内容清单

### 核心工作流文件（共29个必需文件）

#### 1. 主图编排文件（3个）
```
src/graphs/
├── graph.py              # 主图编排逻辑
├── loop_graph.py         # 子图编排逻辑（章节循环）
└── state.py              # 状态定义（GlobalState、Input/Output）
```

#### 2. 节点实现文件（12个）
```
src/graphs/nodes/
├── plot_design_node.py           # 情节设计节点
├── title_gen_node.py             # 标题生成节点
├── style_input_node.py           # 风格输入节点
├── image_prompt_gen_node.py      # 图片提示词生成节点
├── outline_gen_node.py           # 大纲生成节点
├── split_outline_node.py         # 大纲拆分节点
├── chapter_creation_node.py      # 章节创作节点（调用子图）
├── count_words_node.py           # 字数统计节点
├── chapter_outline_gen_node.py   # ✨ 章节大纲生成节点（新增）
├── outline_check_node.py         # ✨ 大纲一致性检查节点（新增）
├── content_check_node.py         # ✨ 内容一致性检查节点（新增）
└── __init__.py                   # 初始化文件
```

#### 3. 大模型配置文件（8个）
```
config/
├── plot_design_cfg.json          # 3.9KB - 情节设计配置
├── title_gen_cfg.json            # 3.3KB - 标题生成配置
├── image_prompt_gen_cfg.json     # 3.5KB - 图片提示词生成配置
├── outline_gen_cfg.json          # 4.2KB - 大纲生成配置
├── chapter_creation_cfg.json     # 3.8KB - 章节创作配置
├── chapter_outline_gen_cfg.json  # 4.2KB - ✨ 章节大纲生成配置（新增）
├── outline_check_cfg.json        # 4.6KB - ✨ 大纲检查配置（新增）
└── content_check_cfg.json        # 5.5KB - ✨ 内容检查配置（新增）
```

每个配置文件包含：
- `config`: 模型参数（model、temperature、max_completion_tokens等）
- `sp`: 系统提示词（包含Anthropic Thinking Protocol）
- `up`: 用户提示词模板（支持Jinja2模板）
- `tools`: 工具列表（本工作流均为空数组）

#### 4. 项目配置文件（3个）
```
├── src/main.py           # 主入口文件
├── .coze                 # 扣子平台配置（入口点、构建脚本等）
├── pyproject.toml        # Python项目配置（依赖管理）
```

#### 5. 文档文件（3个）
```
├── AGENTS.md                     # 项目结构索引文档
├── coze_workflow_manifest.json   # 工作流清单文件
├── coze_import_guide.md          # 扣子导入指南
```

## 🚀 使用方法

### Step 1: 解压文件
```bash
tar -xzf coze_workflow_package.tar.gz
cd coze_workflow_package
```

### Step 2: 导入到扣子平台

#### 方式A：自动导入（推荐）
1. 登录扣子工作流平台：https://work.coze.cn
2. 点击"新建工作流" → "从代码导入"
3. 上传 `coze_workflow_manifest.json` 文件
4. 系统会自动解析并生成可视化画布

#### 方式B：手动配置
参考 `coze_import_guide.md` 文件中的详细步骤

### Step 3: 配置大模型
在扣子平台配置DeepSeek模型：
- Provider: DeepSeek
- Model: deepseek-v3-2-251201
- API Key: 在扣子平台配置或使用内置服务

### Step 4: 测试运行
输入测试参数：
```json
{
  "user_requirement": "写一个科幻小说...",
  "target_word_count": 9000,
  "image_style": "冷色调现代科技风格"
}
```

## 📊 工作流特性

### 核心功能（8个）
1. ✅ 情节设计（六个连续场景）
2. ✅ 标题生成（简洁有力）
3. ✅ 图片风格确认（用户指定）
4. ✅ 图片提示词生成（支持多个模型）
5. ✅ 大纲生成（字数限制150万字）
6. ✅ 大纲拆分（六个部分）
7. ✅ 章节创作（循环创作 + 用户交互）
8. ✅ 字数统计（中文字符）

### 新增功能（上下文检查）
1. ✅ 章节大纲生成（场景划分、人物安排、情节推进）
2. ✅ 大纲一致性检查（主题、人物、情节、设定、风格）
3. ✅ 内容一致性检查（设定、对话、剧情、场景、道具、上下文连贯）

### 技术特性
- ✅ 使用DeepSeek模型（deepseek-v3-2-251201）
- ✅ 包含Anthropic Thinking Protocol
- ✅ 支持用户交互确认（每章创作后）
- ✅ 支持字数验证（不超过150万字）
- ✅ 支持图片生成（固定3:4比例）
- ✅ 支持上下文检查（跨章节一致性）

## ⚠️ 注意事项

1. **大模型配置**: 需要在扣子平台配置DeepSeek API Key或使用内置模型服务
2. **循环限制**: chapter_creation节点的recursion_limit设置为50次
3. **用户交互**: 子图中包含用户交互节点，需要在扣子平台配置交互功能
4. **配置文件**: 所有Agent节点都需要对应的配置文件（已包含在打包文件中）

## 📞 技术支持

如遇问题，请查看：
1. `coze_import_guide.md` - 详细导入步骤
2. `AGENTS.md` - 项目结构和技术细节
3. `coze_workflow_manifest.json` - 工作流配置清单

## 🎯 预期结果

成功导入后，扣子平台应该显示：
- 8个主节点 + 子图内部节点
- 清晰的节点连接关系
- 完整的输入输出参数配置
- 正确的Agent节点模型配置

---

**打包时间**: 2025年6月29日 17:17
**文件大小**: 30KB
**包含文件**: 29个核心文件 + 3个文档文件