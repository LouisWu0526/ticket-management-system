"""图片上传：保存到本地 uploads 目录，由 StaticFiles 挂载提供访问。"""
import uuid

from fastapi import APIRouter, Depends, UploadFile, HTTPException, status

from ..config import settings
from ..deps import get_current_user
from ..models import User
from ..schemas import UploadResponse

router = APIRouter(prefix="/uploads", tags=["文件上传"])


@router.post("", response_model=UploadResponse)
async def upload_image(file: UploadFile, current_user: User = Depends(get_current_user)):
    filename = file.filename or ""
    ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""
    if ext not in settings.ALLOWED_IMAGE_EXT:
        raise HTTPException(
            status_code=400,
            detail=f"仅支持图片格式：{', '.join(settings.ALLOWED_IMAGE_EXT)}",
        )

    data = await file.read()
    max_size = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(data) > max_size:
        raise HTTPException(status_code=400, detail=f"图片大小不能超过 {settings.MAX_UPLOAD_MB}MB")
    if not data:
        raise HTTPException(status_code=400, detail="上传文件为空")

    saved_name = f"{uuid.uuid4().hex}{ext}"
    with open(f"{settings.UPLOAD_DIR}/{saved_name}", "wb") as f:
        f.write(data)

    return UploadResponse(url=f"/uploads/{saved_name}", filename=saved_name)
