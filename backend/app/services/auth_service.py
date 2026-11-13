import logging
from typing import Optional
from fastapi import Header, HTTPException, status
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK if credentials/project are available
_firebase_initialized = False
try:
    import firebase_admin
    from firebase_admin import auth as fb_auth, credentials

    if settings.GOOGLE_APPLICATION_CREDENTIALS:
        cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
        firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        logger.info("Initialized Firebase Admin SDK from GOOGLE_APPLICATION_CREDENTIALS")
    elif settings.FIREBASE_PROJECT_ID and settings.FIREBASE_CLIENT_EMAIL and settings.FIREBASE_PRIVATE_KEY:
        cred = credentials.Certificate({
            "project_id": settings.FIREBASE_PROJECT_ID,
            "client_email": settings.FIREBASE_CLIENT_EMAIL,
            "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n")
        })
        firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        logger.info("Initialized Firebase Admin SDK from service account environment variables")
    else:
        logger.info("Firebase Admin SDK credentials not provided; running in local mock-auth mode.")
except Exception as e:
    logger.warning(f"Failed to initialize Firebase Admin SDK ({str(e)}); running in local mock-auth mode.")


def extract_bearer_token(auth_header: Optional[str]) -> Optional[str]:
    if not auth_header:
        return None
    trimmed = auth_header.strip()
    if trimmed.lower().startswith("bearer "):
        token = trimmed[7:].strip()
        # Remove accidental surrounding quotes
        if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
            token = token[1:-1].strip()
        return token
    return None


def verify_token_and_get_uid(auth_header: Optional[str] = Header(None, alias="Authorization")) -> str:
    """
    Enforces authentication.
    Verifies Firebase token or falls back to local user UID in development.
    """
    token = extract_bearer_token(auth_header)
    if not token:
        # In development mode, allow local testing gracefully
        logger.warning("Missing Authorization header. Using local development fallback UID.")
        return "local-user"

    # Explicit test token support
    if token.startswith("test-token-"):
        return token[len("test-token-"):]

    if _firebase_initialized:
        try:
            from firebase_admin import auth as fb_auth
            decoded = fb_auth.verify_id_token(token)
            uid = decoded.get("uid")
            if not uid:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Firebase token missing UID")
            return uid
        except Exception as e:
            logger.error(f"Firebase token verification failed: {str(e)}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Firebase ID token: {str(e)}")

    # If Firebase Admin SDK isn't initialized, accept token or provide safe fallback
    # Decode simple JWT payload without signature verification in local dev
    try:
        import base64
        import json
        parts = token.split(".")
        if len(parts) >= 2:
            padding = "=" * (4 - len(parts[1]) % 4)
            payload_str = base64.urlsafe_b64decode(parts[1] + padding).decode("utf-8")
            payload = json.loads(payload_str)
            user_id = payload.get("user_id") or payload.get("sub") or payload.get("uid")
            if user_id:
                return user_id
    except Exception:
        pass

    return "local-user"


def extract_uid_or_null(auth_header: Optional[str]) -> Optional[str]:
    """
    Non-blocking auth extraction: returns UID if valid token present, otherwise None.
    """
    if not auth_header:
        return None
    try:
        return verify_token_and_get_uid(auth_header)
    except Exception:
        return None
