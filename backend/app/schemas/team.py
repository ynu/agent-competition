"""
队伍 Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.team import TeamStatus


# 队伍成员基础 schema
class TeamMemberBase(BaseModel):
    student_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)


# 队伍成员创建 schema
class TeamMemberCreate(TeamMemberBase):
    is_leader: bool = False


# 队伍成员响应 schema
class TeamMemberResponse(TeamMemberBase):
    id: int
    team_id: int
    user_id: Optional[int] = None
    is_leader: bool
    created_at: datetime

    class Config:
        from_attributes = True


# 队伍基础 schema
class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


# 队伍创建 schema
class TeamCreate(TeamBase):
    members: List[TeamMemberCreate] = Field(..., min_length=1, max_length=5)


# 队伍更新 schema
class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    status: Optional[TeamStatus] = None
    members: Optional[List[TeamMemberCreate]] = Field(None, description="队员列表（更新时会替换所有非队长队员）")


# 队伍响应 schema
class TeamResponse(TeamBase):
    id: int
    leader_id: int
    status: TeamStatus
    created_at: datetime
    updated_at: datetime
    members: List[TeamMemberResponse] = []

    class Config:
        from_attributes = True


# 队伍审核 schema
class TeamAuditRequest(BaseModel):
    status: TeamStatus = Field(..., description="审核状态")


# 加入队伍请求
class JoinTeamRequest(BaseModel):
    student_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)