from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_user_optional
from app.models.user import User
from app.models.document import DocumentPack
from app.schemas.document import DocumentPackResponse
from app.schemas.common import APIResponse

router = APIRouter(prefix="/documents", tags=["Bộ tài liệu & Ebook (Document Packs)"])


@router.get("", response_model=APIResponse[List[DocumentPackResponse]])
async def get_document_packs(
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách các bộ tài liệu Aptitude Test tiếng Việt.
    Tự động tính toán quyền truy cập (can_access) dựa trên gói học của người dùng.
    """
    stmt = select(DocumentPack).where(DocumentPack.is_active == True)
    docs = (await db.execute(stmt)).scalars().all()

    has_paid_access = user is not None and (user.has_active_subscription or user.role.value == "ADMIN")

    result = []
    for doc in docs:
        can_access = (not doc.is_premium) or has_paid_access
        download_url = doc.download_url if can_access else None
        
        result.append(DocumentPackResponse(
            id=doc.id,
            title=doc.title,
            desc=doc.desc,
            tag=doc.tag,
            level=doc.level,
            pages=doc.pages,
            is_premium=doc.is_premium,
            can_access=can_access,
            download_url=download_url
        ))
    return APIResponse(data=result)


@router.get("/{doc_id}/download-link", response_model=APIResponse[dict])
async def get_document_download_url(
    doc_id: str,
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Lấy link tải tài liệu bản quyền. Kiểm tra xác thực quyền sở hữu trước khi cấp quyền tải."""
    doc = await db.get(DocumentPack, doc_id)
    if not doc or not doc.is_active:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu.")

    has_paid_access = user is not None and (user.has_active_subscription or user.role.value == "ADMIN")
    if doc.is_premium and not has_paid_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài liệu này thuộc quyền lợi Gói trả phí (Gói 7 Ngày hoặc 30 Ngày). Vui lòng nâng cấp để mở khóa."
        )

    # In production, this can return a signed S3 / Cloud Storage URL with 15-minute expiration
    return APIResponse(
        message="Xác thực quyền tải thành công",
        data={
            "document_id": doc.id,
            "title": doc.title,
            "download_url": doc.download_url or f"/static/docs/{doc.id}.pdf"
        }
    )

