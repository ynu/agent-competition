"""
认证 API 路由
"""
import secrets
import string
import httpx
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    verify_password, get_password_hash, create_access_token, get_current_user
)
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.setting import Log
from app.schemas.user import (
    LoginRequest, UnifiedAuthLoginRequest, TokenResponse, UserResponse
)
from urllib.parse import quote

router = APIRouter(prefix="/auth", tags=["认证"])


def generate_strong_password(length: int = 16) -> str:
    """生成随机强密码"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        # 确保包含各类字符
        if (any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in "!@#$%^&*" for c in password)):
            return password


def get_frontend_url_from_referer(request: Request, db: Session = None) -> str:
    """从请求头 Referer 中提取前端 base_url

    如果 referer 的 host 与 CAS server 的 host 相同，则返回 None
    """
    referer = request.headers.get("referer")
    if referer:
        from urllib.parse import urlparse
        parsed = urlparse(referer)
        referer_host = parsed.netloc

        # 获取 CAS server host
        if db is not None:
            cas_config = get_cas_config(db)
            if cas_config.get("cas_base_url"):
                cas_parsed = urlparse(cas_config["cas_base_url"])
                # 如果 referer 来自 CAS server，使用配置中的 base_url
                if referer_host == cas_parsed.netloc:
                    return None

        return f"{parsed.scheme}://{parsed.netloc}"
    return None


def get_base_url(db: Session) -> str:
    """获取应用基础URL"""
    from app.models.setting import Setting
    setting = db.query(Setting).filter(Setting.key == "base_url").first()
    return setting.value if setting and setting.value else settings.BASE_URL


def get_cas_config(db: Session) -> dict:
    """获取CAS配置"""
    from app.models.setting import Setting

    cas_enabled = db.query(Setting).filter(Setting.key == "cas_enabled").first()
    cas_base_url = db.query(Setting).filter(Setting.key == "cas_base_url").first()

    default_cas_base = "https://ids.ynu.edu.cn/authserver"

    return {
        "enabled": cas_enabled.value.lower() == "true" if cas_enabled else True,
        "cas_base_url": cas_base_url.value if cas_base_url else default_cas_base,
        "cas_validate_url": f"{cas_base_url.value if cas_base_url else default_cas_base}/validate",
        "cas_service_validate_url": f"{cas_base_url.value if cas_base_url else default_cas_base}/serviceValidate",
        "cas_login_url": f"{cas_base_url.value if cas_base_url else default_cas_base}/login",
        "cas_logout_url": f"{cas_base_url.value if cas_base_url else default_cas_base}/logout",
    }


def add_log(db: Session, user_id: Optional[int], action: str, resource: str = None,
            resource_id: Optional[int] = None, details: str = None, ip_address: str = None):
    """添加日志"""
    log = Log(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address
    )
    db.add(log)
    db.commit()


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """用户名密码登录"""
    user = db.query(User).filter(User.username == login_data.username).first()

    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    # 创建 token - 必须使用字符串
    access_token = create_access_token(data={"sub": str(user.id)})

    # 记录登录日志
    add_log(
        db, user.id, "login", "auth",
        details=f"用户 {user.username} 登录成功",
        ip_address=request.client.host if request.client else None
    )

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """登出"""
    add_log(
        db, current_user.id, "logout", "auth",
        details=f"用户 {current_user.username} 登出",
        ip_address=request.client.host if request.client else None
    )

    # 如果是CAS登录用户，需要跳转到CAS的logout页面来清除CAS session
    if current_user.auth_source == "cas":
        cas_config = get_cas_config(db)
        frontend_url = get_base_url(db)
        cas_logout_url = f"{cas_config['cas_logout_url']}?service={quote(frontend_url + '/login', safe='')}"

        # 返回HTML页面，让用户点击链接登出（解决第三方Cookie阻止问题）
        # 如果直接重定向，CAS的Set-Cookie会被浏览器阻止
        from fastapi.responses import HTMLResponse
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>正在退出...</title>
            <style>
                * {{ box-sizing: border-box; }}
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                       display: flex; justify-content: center; align-items: center;
                       min-height: 100vh; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
                .container {{ text-align: center; padding: 40px 50px; background: white;
                            border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                            max-width: 420px; width: 90%; }}
                .icon {{ width: 60px; height: 60px; margin-bottom: 20px; }}
                h2 {{ color: #1f2937; margin: 0 0 10px 0; font-size: 24px; }}
                p {{ color: #6b7280; margin: 0 0 30px 0; font-size: 15px; line-height: 1.5; }}
                .btn {{ display: block; width: 100%; padding: 14px; background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
                       color: white; text-decoration: none; border-radius: 10px;
                       font-weight: 600; font-size: 16px; transition: transform 0.2s, box-shadow 0.2s;
                       box-shadow: 0 4px 15px rgba(220, 38, 38, 0.4); }}
                .btn:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(220, 38, 38, 0.5); }}
                .hint {{ margin-top: 20px; font-size: 12px; color: #9ca3af; }}
                .auto-redirect {{ margin-top: 25px; font-size: 13px; color: #9ca3af; }}
            </style>
        </head>
        <body>
            <div class="container">
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                    <polyline points="16 17 21 12 16 7"/>
                    <line x1="21" y1="12" x2="9" y2="12"/>
                </svg>
                <h2>退出统一身份认证</h2>
                <p>您正在退出系统，请点击下方按钮完成统一身份认证(CASTGC)的清除</p>
                <a href="{cas_logout_url}" class="btn">确认退出 (CAS Logout)</a>
                <p class="hint">清除统一身份认证的登录状态(TGC)</p>
            </div>
            <script>
                // 点击按钮后自动跳转
                # document.querySelector('.btn').addEventListener('click', function() {{
                #     // 2秒后自动跳转到登录页
                #     setTimeout(function() {{
                #         window.location.href = "{frontend_url}/login";
                #     }}, 2000);
                # }});
                // 如果5秒后没有点击，自动跳转
                # setTimeout(function() {{
                #     window.location.href = "{frontend_url}/login";
                # }}, 5000);
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    return {"message": "登出成功"}


# ============== 统一身份认证 (CAS 2.0) ==============

@router.get("/cas/login")
async def cas_login(
    request: Request,
    db: Session = Depends(get_db),
    service: str = Query(None, description="跳转URL")
):
    """CAS 2.0 登录入口 - 跳转到统一身份认证页面"""
    cas_config = get_cas_config(db)

    if not cas_config["enabled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="统一身份认证未启用"
        )

    # 优先从 Referer 请求头获取前端 URL，否则从配置获取
    frontend_url = get_base_url(db)
    if not service:
        service = f"{frontend_url}/login"

    # 构建回调URL（必须是可公开访问的地址）
    callback_url = f"{frontend_url}/api/auth/cas/callback"

    # 构建CAS登录URL
    login_url = f"{cas_config['cas_login_url']}?service={quote(callback_url, safe='')}"

    response = RedirectResponse(url=login_url)
    # 保存原始跳转URL到cookie
    response.set_cookie(key="cas_redirect", value=service, httponly=True, max_age=300)
    return response


@router.get("/cas/callback")
async def cas_callback(
    request: Request,
    ticket: str = Query(None, description="CAS服务票据"),
    service: str = Query(None, description="服务URL"),
    db: Session = Depends(get_db)
):
    """CAS 2.0 回调处理 - 验证票据并获取用户信息"""
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="服务票据无效"
        )

    cas_config = get_cas_config(db)

    if not cas_config["enabled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="统一身份认证未启用"
        )

    # 优先从 Referer 请求头获取前端 URL，否则从配置获取
    frontend_url = get_base_url(db)

    # 构建回调URL（必须与cas/login中传递的service一致）
    callback_url = f"{frontend_url}/api/auth/cas/callback"

    # 验证票据 - 调用CAS的serviceValidate端点
    from urllib.parse import urlencode
    validate_url = f"{cas_config['cas_service_validate_url']}?service={quote(callback_url, safe='')}&ticket={ticket}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(validate_url, timeout=10.0)

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CAS验证失败"
                )

            # 解析CAS返回的XML响应
            import xml.etree.ElementTree as ET
            xml_content = response.text

            # CAS 2.0 返回格式:
            # <cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
            #   <cas:authenticationSuccess>
            #     <cas:user>username</cas:user>
            #     <cas:attributes>
            #       <cas:cn>姓名</cas:cn>
            #       <cas:email>email</cas:email>
            #     </cas:attributes>
            #   </cas:authenticationSuccess>
            # </cas:serviceResponse>

            root = ET.fromstring(xml_content)

            # 查找authenticationSuccess
            ns = {'cas': 'http://www.yale.edu/tp/cas'}
            success = root.find('.//cas:authenticationSuccess', ns)

            if success is None:
                # 验证失败
                failure = root.find('.//cas:authenticationFailure', ns)
                if failure is not None:
                    failure_code = failure.get('code', '')
                    failure_detail = f"{failure_code}: {failure.text}" if failure_code else failure.text
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"CAS验证失败 [{validate_url}]: {failure_detail}"
                    )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="CAS验证失败"
                )

            # 获取用户名
            user_element = success.find('cas:user', ns)
            if user_element is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="无法获取用户信息"
                )

            username = user_element.text

            # 获取用户属性
            attributes = success.find('cas:attributes', ns)
            nickname = username
            email = None

            if attributes is not None:
                cn = attributes.find('cas:cn', ns)
                if cn is not None and cn.text:
                    nickname = cn.text

                user_email = attributes.find('cas:email', ns)
                if user_email is not None and user_email.text:
                    email = user_email.text

        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CAS请求失败: {str(e)}"
            )
        except ET.ParseError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"解析CAS响应失败: {str(e)}"
            )

    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法获取用户信息"
        )

    # 查找或创建用户
    user = db.query(User).filter(User.username == username).first()

    if not user:
        # 自动创建用户
        password = generate_strong_password()
        user = User(
            username=username,
            nickname=nickname,
            email=email,
            hashed_password=get_password_hash(password),
            auth_source="cas",
            role=UserRole.USER
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    # 创建 token
    jwt_token = create_access_token(data={"sub": str(user.id)})

    # 记录登录日志
    add_log(
        db, user.id, "login", "auth",
        details=f"CAS统一身份认证登录: {user.username}",
        ip_address=request.client.host if request.client else None
    )

    # 跳转回前端，并携带token
    redirect_to = f"{frontend_url}/login?token={jwt_token}"

    return RedirectResponse(url=redirect_to)


@router.get("/cas/logout")
async def cas_logout(
    request: Request,
    db: Session = Depends(get_db)
):
    """CAS 登出"""
    cas_config = get_cas_config(db)
    # 优先从 Referer 请求头获取前端 URL，否则从配置获取
    frontend_url = get_base_url(db)

    # 跳转到CAS登出
    logout_url = f"{cas_config['cas_logout_url']}?service={frontend_url}"

    return RedirectResponse(url=logout_url)


@router.get("/cas/userinfo")
async def get_cas_userinfo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取CAS用户信息（需要已登录）"""
    # 如果用户是通过CAS登录的，尝试从CAS获取最新信息
    if current_user.auth_source != "cas":
        return {
            "username": current_user.username,
            "nickname": current_user.nickname,
            "email": current_user.email,
            "auth_source": current_user.auth_source
        }

    cas_config = get_cas_config(db)

    # 注意：CAS的access_token需要前端保存并传递
    # 这里暂时返回本地用户信息
    return {
        "username": current_user.username,
        "nickname": current_user.nickname,
        "email": current_user.email,
        "auth_source": current_user.auth_source
    }