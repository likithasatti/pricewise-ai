import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Header, HTTPException, Response, status
from app.models.schemas import UserSearchHistoryDTO
from app.database import (
    db_find_user_history,
    db_save_user_history,
    db_delete_user_history
)
from app.services.auth_service import verify_token_and_get_uid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/history", tags=["Search History"])


@router.get("", response_model=List[UserSearchHistoryDTO])
def get_user_history(
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """Returns search history exclusively for the authenticated user."""
    uid = verify_token_and_get_uid(authorization)
    records = db_find_user_history(uid)
    dtos = []
    for r in records:
        created = None
        if r.get("created_at"):
            try:
                created = datetime.fromisoformat(r["created_at"])
            except Exception:
                pass

        dtos.append(UserSearchHistoryDTO(
            id=r.get("id"),
            userId=r.get("user_id"),
            query=r.get("query"),
            resultCount=r.get("result_count", 0),
            topProductName=r.get("top_product_name"),
            topProductPrice=r.get("top_product_price"),
            topProductStore=r.get("top_product_store"),
            topProductImage=r.get("top_product_image"),
            topProductId=r.get("top_product_id"),
            createdAt=created
        ))
    return dtos


@router.post("", response_model=UserSearchHistoryDTO, status_code=status.HTTP_201_CREATED)
def record_search(
    request: UserSearchHistoryDTO,
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """Manually records a search entry for the authenticated user."""
    uid = verify_token_and_get_uid(authorization)
    now = datetime.now()

    hid = db_save_user_history({
        "id": request.id,
        "user_id": uid,
        "query": request.query.strip() if request.query else "",
        "result_count": request.resultCount or 0,
        "top_product_name": request.topProductName,
        "top_product_price": request.topProductPrice,
        "top_product_store": request.topProductStore,
        "top_product_image": request.topProductImage,
        "top_product_id": request.topProductId,
        "created_at": now.isoformat()
    })

    request.id = hid
    request.userId = uid
    request.createdAt = now
    return request


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_user_history(
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """Deletes all history records for only the authenticated user."""
    uid = verify_token_and_get_uid(authorization)
    db_delete_user_history(uid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
