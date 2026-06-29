from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class GlobalState(BaseModel):
    """全局状态定义"""
    user_requirement: str = Field(default="", description="用户的小说创作需求")
    plot_scenes: str = Field(default="", description="生成的六个主要情节场景")
    novel_title: str = Field(default="", description="小说标题")
    novel_outline: str = Field(default="", description="完整的小说大纲")
    outline_parts: Dict[str, str] = Field(default={}, description="拆分后的大纲各部分")
    chapters: List[str] = Field(default=[], description="创作的六个章节内容")
    total_word_count: int = Field(default=0, description="最终统计的总字数")


class GraphInput(BaseModel):
    """工作流的输入"""
    user_requirement: str = Field(..., description="用户的小说创作需求，包括角色性格、背景信息等")


class GraphOutput(BaseModel):
    """工作流的输出"""
    novel_title: str = Field(..., description="小说标题")
    plot_scenes: str = Field(..., description="主要情节场景")
    novel_outline: str = Field(..., description="完整的小说大纲")
    chapters: List[str] = Field(..., description="创作的六个章节内容")
    total_word_count: int = Field(..., description="最终统计的总字数")


class PlotInput(BaseModel):
    """情节设计节点输入"""
    user_requirement: str = Field(..., description="用户的小说创作需求")


class PlotOutput(BaseModel):
    """情节设计节点输出"""
    plot_scenes: str = Field(..., description="生成的六个主要情节场景")


class TitleInput(BaseModel):
    """标题生成节点输入"""
    plot_scenes: str = Field(..., description="主要情节场景")


class TitleOutput(BaseModel):
    """标题生成节点输出"""
    novel_title: str = Field(..., description="小说标题")


class OutlineInput(BaseModel):
    """大纲生成节点输入"""
    novel_title: str = Field(..., description="小说标题")
    plot_scenes: str = Field(..., description="主要情节场景")


class OutlineOutput(BaseModel):
    """大纲生成节点输出"""
    novel_outline: str = Field(..., description="完整的小说大纲")


class SplitOutlineInput(BaseModel):
    """拆分大纲节点输入"""
    novel_outline: str = Field(..., description="完整的小说大纲文本")


class SplitOutlineOutput(BaseModel):
    """拆分大纲节点输出"""
    part1_title: str = Field(default="", description="第一部分大纲标题")
    part1_requirement: str = Field(default="", description="第一部分编写要求")
    part2_title: str = Field(default="", description="第二部分大纲标题")
    part2_requirement: str = Field(default="", description="第二部分编写要求")
    part3_title: str = Field(default="", description="第三部分大纲标题")
    part3_requirement: str = Field(default="", description="第三部分编写要求")
    part4_title: str = Field(default="", description="第四部分大纲标题")
    part4_requirement: str = Field(default="", description="第四部分编写要求")
    part5_title: str = Field(default="", description="第五部分大纲标题")
    part5_requirement: str = Field(default="", description="第五部分编写要求")
    part6_title: str = Field(default="", description="第六部分大纲标题")
    part6_requirement: str = Field(default="", description="第六部分编写要求")


class ChapterCreationInput(BaseModel):
    """章节创作节点输入"""
    part_title: str = Field(..., description="当前章节的大纲标题")
    part_requirement: str = Field(..., description="当前章节的编写要求")
    full_outline: str = Field(..., description="完整的小说大纲")


class ChapterCreationOutput(BaseModel):
    """单个章节创作节点输出"""
    chapter_content: str = Field(..., description="创作的章节内容")


class AllChaptersOutput(BaseModel):
    """所有章节创作节点输出"""
    chapters: List[str] = Field(default=[], description="创作的六个章节内容列表")


class CountWordsInput(BaseModel):
    """统计字数节点输入"""
    chapter1: str = Field(default="", description="第一章内容")
    chapter2: str = Field(default="", description="第二章内容")
    chapter3: str = Field(default="", description="第三章内容")
    chapter4: str = Field(default="", description="第四章内容")
    chapter5: str = Field(default="", description="第五章内容")
    chapter6: str = Field(default="", description="第六章内容")


class CountWordsOutput(BaseModel):
    """统计字数节点输出"""
    total_word_count: int = Field(..., description="总字数统计")