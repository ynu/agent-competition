"""
内容管理 API 路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_active_user_optional, require_role
from app.models.user import User, UserRole
from app.models.content import Content, ContentType, ContentContentType
from app.models.setting import Log
from app.schemas.content import (
    ContentCreate, ContentUpdate, ContentResponse, ContentTreeResponse
)
from app.schemas.common import PageResponse
import markdown
import os
from jinja2 import Template

router = APIRouter(prefix="/contents", tags=["内容管理"])


def add_log(db: Session, user_id: int, action: str, resource: str = None,
            resource_id: int = None, details: str = None):
    """添加日志"""
    log = Log(user_id=user_id, action=action, resource=resource,
              resource_id=resource_id, details=details)
    db.add(log)
    db.commit()


@router.get("", response_model=PageResponse)
async def get_contents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[ContentType] = None,
    parent_id: Optional[int] = None,
    is_published: Optional[bool] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user_optional)
):
    """获取内容列表"""
    query = db.query(Content)

    if type:
        query = query.filter(Content.type == type)

    if parent_id is not None:
        query = query.filter(Content.parent_id == parent_id)

    if keyword:
        query = query.filter(
            Content.title.ilike(f"%{keyword}%") |
            Content.slug.ilike(f"%{keyword}%") |
            Content.summary.ilike(f"%{keyword}%")
        )

    # 如果 is_published 显式传递了值（包括 false），使用该值过滤
    # 如果没有传递，则：
    #   - 已登录用户（reviewer/admin）可以看到所有内容
    #   - 未登录用户只能看到已发布的内容
    if is_published is not None:
        query = query.filter(Content.is_published == is_published)
    elif current_user and current_user.role in [UserRole.REVIEWER, UserRole.ADMIN, UserRole.USER]:
        # 已登录用户可以看到全部内容（包括草稿）
        pass
    else:
        query = query.filter(Content.is_published == True)

    total = query.count()
    contents = query.order_by(Content.order, Content.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[ContentResponse.model_validate(c) for c in contents]
    )


@router.get("/tree", response_model=List[ContentTreeResponse])
async def get_content_tree(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user_optional)
):
    """获取内容树"""
    # 只获取顶级栏目
    contents = db.query(Content).filter(Content.parent_id == None).order_by(Content.order).all()

    def build_tree(content: Content) -> ContentTreeResponse:
        children = [build_tree(c) for c in content.children]
        response = ContentTreeResponse.model_validate(content)
        response.children = children
        return response

    return [build_tree(c) for c in contents]


@router.get("/articles", response_model=PageResponse)
async def get_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user_optional)
):
    """获取新闻/文章列表"""
    query = db.query(Content).filter(
        Content.type == ContentType.ARTICLE,
        Content.is_published == True
    )

    if keyword:
        query = query.filter(
            Content.title.ilike(f"%{keyword}%") |
            Content.summary.ilike(f"%{keyword}%")
        )

    total = query.count()
    articles = query.order_by(Content.order, Content.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[ContentResponse.model_validate(a) for a in articles]
    )


@router.get("/articles/latest", response_model=List[ContentResponse])
async def get_latest_articles(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user_optional)
):
    """获取最新文章列表"""
    articles = db.query(Content).filter(
        Content.type == ContentType.ARTICLE,
        Content.is_published == True
    ).order_by(Content.order, Content.created_at.desc()).limit(limit).all()

    return [ContentResponse.model_validate(a) for a in articles]


@router.get("/materials", response_model=PageResponse)
async def get_materials(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user_optional)
):
    """获取课程资料列表"""
    query = db.query(Content).filter(
        Content.type == ContentType.PAGE,
        Content.is_published == True
    )

    if keyword:
        query = query.filter(
            Content.title.ilike(f"%{keyword}%") |
            Content.summary.ilike(f"%{keyword}%")
        )

    total = query.count()
    materials = query.order_by(Content.order, Content.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[ContentResponse.model_validate(m) for m in materials]
    )


@router.get("/slug/{slug}", response_model=ContentResponse)
async def get_content_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user_optional)
):
    """通过 slug 获取内容"""
    content = db.query(Content).filter(Content.slug == slug).first()
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")

    # 未登录用户只能查看已发布内容
    if not content.is_published:
        raise HTTPException(status_code=403, detail="内容未发布")

    return ContentResponse.model_validate(content)


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user_optional)
):
    """获取内容详情"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")

    # 增加浏览次数
    content.view_count = (content.view_count or 0) + 1
    db.commit()

    return ContentResponse.model_validate(content)


@router.post("", response_model=ContentResponse)
async def create_content(
    content_data: ContentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建内容"""
    # 如果没有提供 slug，自动生成
    slug = content_data.slug
    if not slug:
        if content_data.type == ContentType.ARTICLE:
            # 文章自动生成 slug
            slug = f"article-{content_data.title}"
        elif content_data.type == ContentType.PAGE:
            # 课程资料自动生成 slug
            slug = f"page-{content_data.title}"
        else:
            # 栏目必须有 slug
            raise HTTPException(status_code=400, detail="栏目必须提供 slug")

    # 检查 slug 是否已存在
    if db.query(Content).filter(Content.slug == slug).first():
        raise HTTPException(status_code=400, detail="slug 已存在")

    content = Content(
        title=content_data.title,
        slug=slug,
        type=content_data.type,
        content=content_data.content,
        content_format=content_data.content_format,
        parent_id=content_data.parent_id,
        order=content_data.order,
        is_published=content_data.is_published,
        summary=content_data.summary,
        author=content_data.author,
        cover_image=content_data.cover_image
    )
    db.add(content)
    db.commit()
    db.refresh(content)

    add_log(db, current_user.id, "create", "content", content.id, f"创建内容: {content.title}")

    return ContentResponse.model_validate(content)


@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: int,
    content_data: ContentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新内容"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")

    # 检查 slug 是否冲突
    if content_data.slug and content_data.slug != content.slug:
        if db.query(Content).filter(Content.slug == content_data.slug).first():
            raise HTTPException(status_code=400, detail="slug 已存在")

    update_data = content_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(content, key, value)

    db.commit()
    db.refresh(content)

    add_log(db, current_user.id, "update", "content", content.id, f"更新内容: {content.title}")

    return ContentResponse.model_validate(content)


@router.delete("/{content_id}")
async def delete_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除内容"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")

    title = content.title
    db.delete(content)
    db.commit()

    add_log(db, current_user.id, "delete", "content", content_id, f"删除内容: {title}")

    return {"message": "删除成功"}


@router.post("/generate-static")
async def generate_static_page(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.REVIEWER))
):
    """生成静态页面"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")

    # 转换内容
    html_content = content.content
    if content.content_format == ContentContentType.MARKDOWN and content.content:
        html_content = markdown.markdown(content.content)

    # 简单模板
    template_str = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{{ title }}</title>
        <style>
            body { font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #333; }
            .content { line-height: 1.6; }
        </style>
    </head>
    <body>
        <h1>{{ title }}</h1>
        <div class="content">{{ content | safe }}</div>
    </body>
    </html>
    """
    template = Template(template_str)
    html = template.render(title=content.title, content=html_content)

    # 保存静态文件
    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    os.makedirs(static_dir, exist_ok=True)

    filepath = os.path.join(static_dir, f"{content.slug}.html")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    add_log(db, current_user.id, "generate_static", "content", content.id,
            f"生成静态页面: {content.slug}.html")

    return {"message": "静态页面生成成功", "path": f"/static/{content.slug}.html"}


# ============== 内容排序 ==============

@router.put("/reorder")
async def reorder_contents(
    body: dict = Body(..., description="内容ID列表，按新顺序排列"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.REVIEWER))
):
    """批量更新内容排序"""
    content_ids = body.get("content_ids", [])

    for i, content_id in enumerate(content_ids):
        content = db.query(Content).filter(Content.id == content_id).first()
        if content:
            content.order = i

    db.commit()
    return {"message": "排序已更新"}