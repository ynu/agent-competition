"""
智能体中心 API 路由
"""
from collections import OrderedDict
from typing import Optional
import httpx
import os
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse
from app.core.config import settings

router = APIRouter(prefix="/agent-center", tags=["智能体中心"])


def sign_request(method: str, host: str, action: str, version: str, body: str) -> dict:
    """签名请求"""
    try:
        from volcengine.auth.SignerV4 import SignerV4
        from volcengine.auth.SignParam import SignParam
        from volcengine.Credentials import Credentials

        sign = SignerV4()
        param = SignParam()
        param.method = method
        param.host = host
        query = OrderedDict()
        query['Action'] = action
        query['Version'] = version
        query['X-Account-Id'] = settings.VOLCENGINE_ACCOUNT_ID
        param.query = query
        header = OrderedDict()
        header['Host'] = host
        header['Content-Type'] = 'application/json'
        param.header_list = header
        param.headers = header
        param.body = body
        cren = Credentials(settings.VOLCENGINE_AK, settings.VOLCENGINE_SK, settings.VOLCENGINE_SERVICE, settings.VOLCENGINE_REGION)
        sign.sign(param, cren)
        return param.headers
    except ImportError:
        raise ImportError("请安装 volcengine 包: pip install volcengine")


@router.get("/categories")
async def list_categories():
    """获取智能体分类列表"""
    if not settings.VOLCENGINE_AK or not settings.VOLCENGINE_SK:
        raise Exception("未配置火山引擎 API 密钥")

    host = settings.VOLCENGINE_HOST
    action = "ListAppCenterCategory"
    version = "2023-08-01"
    url = f"http://{host}?Action={action}&Version={version}&X-Account-Id={settings.VOLCENGINE_ACCOUNT_ID}"

    body = '{"ListOpt": {"PageNumber": 1, "PageSize": 100}, "Filter": {}}'

    headers = sign_request("POST", host, action, version, body)

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, content=body, timeout=30.0)
        response.raise_for_status()
        return response.json()


@router.get("")
async def list_agents(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(30, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="分类代码"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    sort: str = Query("latest", description="排序: latest-最新上架, popular-最受欢迎")
):
    """获取智能体列表"""
    if not settings.VOLCENGINE_AK or not settings.VOLCENGINE_SK:
        raise Exception("未配置火山引擎 API 密钥")

    host = settings.VOLCENGINE_HOST
    action = "ListAppCenter"
    version = "2023-08-01"
    url = f"http://{host}?Action={action}&Version={version}&X-Account-Id={settings.VOLCENGINE_ACCOUNT_ID}"

    # 构建过滤条件
    filter_dict = {}
    if category:
        filter_dict["CategoryCode"] = category

    # 构建排序 - 火山引擎API可能需要不同的字段
    # SubmitTimestamp 用于最新, FavoriteCount 或 UseCount 用于最受欢迎
    list_opt = {
        "PageNumber": page,
        "PageSize": page_size,
        "SortBy": "SubmitTimestamp" if sort == "latest" else "FavoriteCount",
        "SortOrder": "Descending"
    }

    body_dict = {
        "ListOpt": list_opt,
        "Filter": filter_dict
    }

    import json
    body = json.dumps(body_dict)

    headers = sign_request("POST", host, action, version, body)

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, content=body, timeout=30.0)
        response.raise_for_status()
        return response.json()


@router.get("/image/{image_path:path}")
async def get_agent_image(image_path: str):
    """获取智能体图片"""
    if not settings.VOLCENGINE_AK or not settings.VOLCENGINE_SK:
        raise HTTPException(status_code=500, detail="未配置火山引擎 API 密钥")

    host = settings.VOLCENGINE_HOST
    action = "GetImageUploadUrl"
    version = "2023-08-01"
    url = f"http://{host}?Action={action}&Version={version}&X-Account-Id={settings.VOLCENGINE_ACCOUNT_ID}"

    body_dict = {
        "FileName": image_path.split("/")[-1],
        "Type": "AgentIcon"
    }

    import json
    body = json.dumps(body_dict)

    headers = sign_request("POST", host, action, version, body)

    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.post(url, headers=headers, content=body, timeout=30.0)
        response.raise_for_status()
        data = response.json()

        # 获取预签名URL
        upload_url = data.get("Result", {}).get("UploadUrl", "")
        if not upload_url:
            raise HTTPException(status_code=404, detail="图片不存在")

        # 代理获取图片
        img_response = await client.get(upload_url, timeout=30.0)
        return img_response.content