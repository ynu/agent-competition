"""
OTP 加密工具模块
使用 Fernet 对称加密存储 OTP Secret
"""
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from app.core.config import get_otp_encryption_key

# 缓存 Fernet 实例，避免每次调用生成不同密钥
_fernet_cache: Fernet | None = None


def _get_fernet() -> Fernet:
    """获取 Fernet 实例"""
    global _fernet_cache
    if _fernet_cache is not None:
        return _fernet_cache

    key = get_otp_encryption_key()
    # 如果是有效的 Fernet 密钥（44字符 base64），直接使用
    if len(key) == 44:
        try:
            _fernet_cache = Fernet(key.encode())
            return _fernet_cache
        except Exception:
            pass

    # 从密码派生出 Fernet 密钥
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"otp_secret_salt",  # 生产环境应使用随机盐并存储
        iterations=480000,
    )
    derived_key = base64.urlsafe_b64encode(kdf.derive(key.encode()))
    _fernet_cache = Fernet(derived_key)
    return _fernet_cache


def encrypt_otp_secret(secret: str) -> str:
    """加密 OTP Secret"""
    fernet = _get_fernet()
    return fernet.encrypt(secret.encode()).decode()


def decrypt_otp_secret(encrypted: str) -> str:
    """解密 OTP Secret"""
    fernet = _get_fernet()
    return fernet.decrypt(encrypted.encode()).decode()