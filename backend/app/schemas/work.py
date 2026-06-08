"""
作品 Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.work import WorkStatus

# Import here to avoid circular dependency
from app.schemas.team import TeamMemberResponse


# 作品基础 schema
class WorkBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    theme_id: Optional[int] = None
    agent_url: Optional[str] = Field(None, max_length=500)
    agent_editor_url: Optional[str] = Field(None, max_length=500)
    pdf_file: Optional[str] = None
    video_file: Optional[str] = None


# 作品创建 schema
class WorkCreate(WorkBase):
    pass


# 作品更新 schema
class WorkUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    theme_id: Optional[int] = None
    agent_url: Optional[str] = Field(None, max_length=500)
    agent_editor_url: Optional[str] = Field(None, max_length=500)
    status: Optional[WorkStatus] = None


# 作品响应 schema
class WorkResponse(BaseModel):
    id: int
    team_id: int
    name: str
    description: Optional[str] = None
    theme_id: Optional[int] = None
    agent_url: Optional[str] = None
    agent_editor_url: Optional[str] = None
    pdf_file: Optional[str] = None
    video_file: Optional[str] = None
    vote_count: int = 0
    score: Optional[float] = None
    status: WorkStatus
    created_at: datetime
    updated_at: datetime
    theme_name: Optional[str] = None

    class Config:
        from_attributes = True


# 作品详情响应（包含队伍信息）
class WorkDetailResponse(WorkResponse):
    team_name: str = ""
    team_members: List[TeamMemberResponse] = []

    class Config:
        from_attributes = True


# 评审 schema
class ReviewBase(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=100)
    comment: Optional[str] = None


# 评审创建 schema
class ReviewCreate(ReviewBase):
    work_id: int


# 评审更新 schema
class ReviewUpdate(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=100)
    comment: Optional[str] = None


# 评审响应 schema
class ReviewResponse(ReviewBase):
    id: int
    work_id: int
    user_id: int
    reviewer_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 投票请求 schema
class VoteRequest(BaseModel):
    work_id: int


# 版权协议签署 schema
class CopyrightAgreementCreate(BaseModel):
    work_id: Optional[int] = None
    signature_data: str = Field(..., description="签名数据（Base64编码的图片数据）")
    signature_name: Optional[str] = Field(None, max_length=100, description="签名人姓名")


class CopyrightAgreementResponse(BaseModel):
    id: int
    user_id: int
    work_id: Optional[int] = None
    signature_name: Optional[str] = None
    ip_address: Optional[str] = None
    agreement_content: str
    created_at: datetime

    class Config:
        from_attributes = True