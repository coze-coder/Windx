# 扣子工作流导入指南

## 📋 导入准备清单

### 必需文件（共29个文件）

#### 1. 核心工作流文件（3个）
- ✅ `src/graphs/graph.py` - 主图编排
- ✅ `src/graphs/loop_graph.py` - 子图（章节循环）
- ✅ `src/graphs/state.py` - 状态定义

#### 2. 节点文件（12个）
```
src/graphs/nodes/
├── plot_design_node.py          ✅ 情节设计
├── title_gen_node.py             ✅ 标题生成
├── style_input_node.py           ✅ 风格输入
├── image_prompt_gen_node.py      ✅ 图片提示词生成
├── outline_gen_node.py           ✅ 大纲生成
├── split_outline_node.py         ✅ 大纲拆分
├── chapter_creation_node.py      ✅ 章节创作
├── count_words_node.py           ✅ 字数统计
├── chapter_outline_gen_node.py   ✅ 章节大纲生成（新增）
├── outline_check_node.py         ✅ 大纲一致性检查（新增）
├── content_check_node.py         ✅ 内容一致性检查（新增）
└── __init__.py                   ✅ 初始化文件
```

#### 3. 配置文件（8个）
```
config/
├── plot_design_cfg.json          ✅ 3.9KB
├── title_gen_cfg.json            ✅ 3.3KB
├── image_prompt_gen_cfg.json     ✅ 3.5KB
├── outline_gen_cfg.json          ✅ 4.2KB
├── chapter_creation_cfg.json     ✅ 3.8KB
├── chapter_outline_gen_cfg.json  ✅ 4.2KB（新增）
├── outline_check_cfg.json        ✅ 4.6KB（新增）
└── content_check_cfg.json        ✅ 5.5KB（新增）
```

#### 4. 项目配置文件（3个）
- ✅ `src/main.py` - 主入口
- ✅ `.coze` - 扣子平台配置
- ✅ `pyproject.toml` - 依赖管理

#### 5. 工具文件（2个）
- ✅ `coze_workflow_manifest.json` - 工作流清单（本文件）
- ✅ `AGENTS.md` - 项目文档

## 🚀 导入步骤

### 方式1：自动导入（推荐）

1. **登录扣子工作流平台**
   - 访问：https://work.coze.cn
   - 登录你的账号

2. **创建新工作流**
   - 点击"新建工作流"
   - 选择"从代码导入"
   - 上传 `coze_workflow_manifest.json` 文件

3. **上传项目文件**
   - 将所有必需文件打包成ZIP
   - 上传到扣子平台
   - 系统会自动解析并生成可视化画布

### 方式2：手动配置

如果自动导入失败，可以手动配置：

#### Step 1: 创建工作流
- 工作流名称：万字小说创作工作流（含上下文检查）
- 工作流描述：根据用户需求自动创作完整的万字小说，支持上下文一致性检查

#### Step 2: 添加输入参数
```json
{
  "user_requirement": {
    "type": "string",
    "required": true,
    "description": "用户的小说创作需求"
  },
  "target_word_count": {
    "type": "integer",
    "required": true,
    "max": 1500000,
    "description": "目标总字数"
  },
  "image_style": {
    "type": "string",
    "required": false,
    "description": "图片风格"
  }
}
```

#### Step 3: 添加输出参数
```json
{
  "novel_title": "string",
  "plot_scenes": "string",
  "image_prompt": "string",
  "novel_outline": "string",
  "chapters": "array",
  "total_word_count": "integer"
}
```

#### Step 4: 添加节点
按照 `coze_workflow_manifest.json` 中的节点清单逐一添加：

**主图节点（8个）：**
1. plot_design（Agent节点）
2. title_gen（Agent节点）
3. style_input（Task节点）
4. image_prompt_gen（Agent节点）
5. outline_gen（Agent节点）
6. split_outline（Task节点）
7. chapter_creation（Loop节点）
8. count_words（Task节点）

**子图节点（在chapter_creation内部）：**
1. generate_outline（包装节点）
2. check_outline（包装节点）
3. create_chapter（包装节点）
4. check_content（包装节点）
5. user_interaction（交互节点）
6. move_next（条件节点）

#### Step 5: 配置连接关系
按照manifest中的workflow_flow和subgraph_flow配置节点连接

#### Step 6: 配置Agent节点
为每个Agent节点配置：
- 大模型：DeepSeek（deepseek-v3-2-251201）
- 系统提示词：复制对应config文件中的sp内容
- 用户提示词模板：复制对应config文件中的up内容
- Temperature：
  - 创作类节点：0.7-0.9
  - 检查类节点：0.3

## ⚙️ 配置要点

### 大模型配置
所有Agent节点使用DeepSeek模型，需要：
- ✅ 在扣子平台配置DeepSeek API Key
- ✅ 或使用扣子内置的模型服务
- ✅ 系统提示词包含Anthropic Thinking Protocol

### 循环配置
chapter_creation节点需要配置：
- ✅ 类型：looparray
- ✅ 循环次数：固定6次（六个章节）
- ✅ 子图：chapter_loop_graph
- ✅ 递归限制：50次（防止超限）

### 用户交互配置
user_interaction节点需要：
- ✅ 类型：交互节点
- ✅ 输出字段：user_feedback、needs_revision
- ✅ 条件判断：根据反馈决定重新创作或继续

## 📊 预期效果

导入成功后，扣子平台应该显示：
- ✅ 可视化工作流画布
- ✅ 8个主节点 + 子图内部节点
- ✅ 节点连接关系清晰
- ✅ 输入输出参数完整
- ✅ Agent节点配置正确

## 🔍 验证清单

导入后请检查：
1. ✅ 节点数量：8个主节点 + 7个子图节点
2. ✅ 连接关系：线性流程 + 循环逻辑
3. ✅ 输入参数：3个（user_requirement、target_word_count、image_style）
4. ✅ 输出参数：6个（novel_title、plot_scenes、image_prompt、novel_outline、chapters、total_word_count）
5. ✅ Agent配置：DeepSeek模型 + 提示词配置
6. ✅ 循环配置：子图正确，递归限制50次

## 📞 常见问题

### Q1: 导入失败怎么办？
**A:** 检查文件完整性，确保所有29个必需文件都已上传

### Q2: Agent节点无法识别？
**A:** 检查节点函数签名是否符合规范（必须使用Runtime[Context]）

### Q3: 循环逻辑不正确？
**A:** 确认chapter_creation节点的类型设置为looparray，子图配置正确

### Q4: 大模型配置错误？
**A:** 复制config文件中的完整配置内容到扣子平台的模型配置页面

## 🎯 下一步

导入成功后：
1. 在扣子平台测试工作流
2. 调整参数优化效果
3. 添加更多自定义功能
4. 发布为可复用的模板

---

需要帮助？请查看 `AGENTS.md` 了解更多技术细节。