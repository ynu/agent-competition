"""
Passkey (通行密钥) 模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserPasskey(Base):
    """用户 Passkey 表"""
    __tablename__ = "user_passkeys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    credential_id = Column(String(255), unique=True, nullable=False, comment="公钥凭证ID")
    public_key = Column(Text, nullable=False, comment="公钥")
    counter = Column(Integer, default=0, comment="签名计数器（防重放）")
    device_name = Column(String(255), nullable=True, comment="设备名称")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

    # 关系
    user = relationship("User", backref="passkeys")

    def __repr__(self):
        return f"<UserPasskey {self.credential_id[:20]}...>"