import logging
from typing import List, Optional
from fastapi import APIRouter, Header, HTTPException, Response, status
from app.models.schemas import TrackedProductDTO, TrackingRequestDTO
from app.services.price_tracking import price_tracking_service
from app.services.auth_service import verify_token_and_get_uid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tracking", tags=["Price Tracking"])


@router.post("", response_model=TrackedProductDTO, status_code=status.HTTP_200_OK)
def track_product(
    request: TrackingRequestDTO,
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """Starts or updates price tracking for a store product."""
    uid = verify_token_and_get_uid(authorization)
    return price_tracking_service.track_product(request, uid)


@router.get("", response_model=List[TrackedProductDTO])
def get_tracked_products(
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """Retrieves all active tracked products for the authenticated user."""
    uid = verify_token_and_get_uid(authorization)
    return price_tracking_service.get_tracked_products(uid)


@router.get("/{tracking_id}", response_model=TrackedProductDTO)
def get_tracked_product(
    tracking_id: int,
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """Retrieves a single tracked product by ID for the authenticated user."""
    uid = verify_token_and_get_uid(authorization)
    return price_tracking_service.get_tracked_product(tracking_id, uid)


@router.delete("/{tracking_id}", status_code=status.HTTP_204_NO_CONTENT)
def stop_tracking(
    tracking_id: int,
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """Deactivates price tracking for the specified item."""
    uid = verify_token_and_get_uid(authorization)
    price_tracking_service.stop_tracking(tracking_id, uid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{tracking_id}/check-now", response_model=TrackedProductDTO)
def check_price_now(
    tracking_id: int,
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """Triggers an immediate on-demand price check for a tracked item."""
    uid = verify_token_and_get_uid(authorization)
    return price_tracking_service.check_price_now(tracking_id, uid)
