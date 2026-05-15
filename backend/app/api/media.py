"""
媒体文件管理 API 路由
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.core.config import settings
from app.models.user import User
from datetime import datetime
import os
import shutil
from pathlib import Path

router = APIRouter(prefix="/media", tags=["媒体管理"])


class DirInfo(BaseModel):
    name: str
    path: str
    children: List["DirInfo"] = []


class FileInfo(BaseModel):
    name: str
    path: str
    size: int
    is_dir: bool
    modified: str
    extension: Optional[str] = None


class CreateDirRequest(BaseModel):
    name: str
    parent: Optional[str] = ""


class MoveRequest(BaseModel):
    from_path: str
    to_path: str


def get_media_dir() -> Path:
    """获取媒体目录路径"""
    media_dir = Path(settings.MEDIA_DIR)
    media_dir.mkdir(parents=True, exist_ok=True)
    return media_dir


def safe_path(base: Path, target: str) -> Path:
    """安全的路径解析，防止目录遍历"""
    if target:
        # 清理路径
        target = target.strip("/")
        full_path = (base / target).resolve()
        # 确保在 base 目录下
        if not str(full_path).startswith(str(base.resolve())):
            raise HTTPException(status_code=400, detail="无效的路径")
        return full_path
    return base


def get_dir_tree(path: Path, base_path: Optional[Path] = None) -> List[DirInfo]:
    """获取目录树"""
    if base_path is None:
        base_path = path

    result = []
    try:
        for item in sorted(path.iterdir()):
            if item.is_dir() and not item.name.startswith('.'):
                relative_path = str(item.relative_to(base_path)) if base_path != item else ""
                dir_info = DirInfo(
                    name=item.name,
                    path=relative_path,
                    children=get_dir_tree(item, base_path)
                )
                result.append(dir_info)
    except PermissionError:
        pass

    return result

    return result


def get_file_info(path: Path, base_path: Path) -> FileInfo:
    """获取文件信息"""
    stat = path.stat()
    relative_path = str(path.relative_to(base_path))
    extension = path.suffix.lstrip('.').lower() if path.is_file() else None

    return FileInfo(
        name=path.name,
        path=relative_path,
        size=stat.st_size,
        is_dir=path.is_dir(),
        modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
        extension=extension
    )


@router.get("/dirs")
async def get_directories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取媒体目录树"""
    media_dir = get_media_dir()
    tree = get_dir_tree(media_dir)
    return {"items": tree}


@router.post("/dirs")
async def create_directory(
    data: CreateDirRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建目录"""
    require_role(current_user, "admin")

    media_dir = get_media_dir()
    parent_path = media_dir if not data.parent else safe_path(media_dir, data.parent)
    new_dir = parent_path / data.name

    if new_dir.exists():
        raise HTTPException(status_code=400, detail="目录已存在")

    if not data.name or "/" in data.name or "\\" in data.name:
        raise HTTPException(status_code=400, detail="无效的目录名")

    new_dir.mkdir(parents=True, exist_ok=True)
    return {"message": "目录创建成功", "path": str(new_dir.relative_to(media_dir))}


@router.delete("/dirs")
async def delete_directory(
    path: str = Query(..., description="目录路径"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除目录"""
    require_role(current_user, "admin")

    media_dir = get_media_dir()
    target_path = safe_path(media_dir, path)

    if target_path == media_dir:
        raise HTTPException(status_code=400, detail="不能删除根目录")

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="目录不存在")

    shutil.rmtree(target_path)
    return {"message": "目录删除成功"}


@router.get("/files")
async def list_files(
    path: Optional[str] = Query(None, description="目录路径"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取文件列表"""
    media_dir = get_media_dir()
    current_path = media_dir if not path else safe_path(media_dir, path)

    if not current_path.exists():
        raise HTTPException(status_code=404, detail="目录不存在")

    items = []
    try:
        for item in sorted(current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            if item.name.startswith('.'):
                continue
            items.append(get_file_info(item, media_dir))
    except PermissionError:
        raise HTTPException(status_code=403, detail="无权限访问该目录")

    is_root = current_path.resolve() == media_dir.resolve()
    return {
        "path": path or "",
        "items": items,
        "parent": None if is_root else str(current_path.parent.relative_to(media_dir.resolve()))
    }


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    path: Optional[str] = Form(None, description="目标目录"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """上传文件"""
    media_dir = get_media_dir()
    target_dir = media_dir if not path else safe_path(media_dir, path)

    # 检查文件大小
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"文件大小超过限制 ({settings.MAX_FILE_SIZE // (1024*1024)}MB)")

    # 检查扩展名
    ext = os.path.splitext(file.filename)[1].lstrip('.').lower()
    if ext not in settings.MEDIA_ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext}")

    # 保存文件
    target_path = target_dir / file.filename
    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    relative_path = str(target_path.relative_to(media_dir))
    return {
        "message": "上传成功",
        "path": relative_path,
        "url": f"/media/preview/{relative_path}"
    }


@router.delete("/{path:path}")
async def delete_file(
    path: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除文件"""
    require_role(current_user, "admin")

    media_dir = get_media_dir()
    target_path = safe_path(media_dir, path)

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    if target_path.is_dir():
        shutil.rmtree(target_path)
    else:
        target_path.unlink()

    return {"message": "删除成功"}


@router.post("/move")
async def move_file(
    data: MoveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """移动或重命名文件"""
    require_role(current_user, "admin")

    media_dir = get_media_dir()
    from_path = safe_path(media_dir, data.from_path)
    to_path = safe_path(media_dir, data.to_path)

    if not from_path.exists():
        raise HTTPException(status_code=404, detail="源文件不存在")

    if to_path.exists():
        raise HTTPException(status_code=400, detail="目标位置已存在文件")

    # 确保目标目录存在
    to_path.parent.mkdir(parents=True, exist_ok=True)

    shutil.move(str(from_path), str(to_path))
    return {"message": "移动成功", "path": data.to_path}


@router.get("/preview/{path:path}")
async def preview_file(
    path: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """预览文件"""
    media_dir = get_media_dir()
    file_path = safe_path(media_dir, path)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    if file_path.is_dir():
        raise HTTPException(status_code=400, detail="不能预览目录")

    # 根据文件类型返回不同响应
    ext = file_path.suffix.lstrip('.').lower()
    content_type_map = {
        "pdf": "application/pdf",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "svg": "image/svg+xml",
        "webp": "image/webp",
        "mp4": "video/mp4",
        "webm": "video/webm",
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
    }

    content_type = content_type_map.get(ext, "application/octet-stream")
    return FileResponse(file_path, media_type=content_type, filename=file_path.name)


@router.get("/download/{path:path}")
async def download_file(
    path: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """下载文件"""
    media_dir = get_media_dir()
    file_path = safe_path(media_dir, path)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(file_path, filename=file_path.name, media_type="application/octet-stream")