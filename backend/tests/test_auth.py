import base64
import json
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.auth_service import AuthService


def _fake_id_token(sub: str = "firebase_uid_123") -> str:
    """Build a structurally valid JWT (NOT cryptographically signed) for tests."""
    def b64url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

    header = b64url(json.dumps({"alg": "RS256", "kid": "test-key"}).encode("ascii"))
    payload = b64url(json.dumps({
        "sub": sub,
        "aud": "rudra-ff130",
        "iss": "https://securetoken.google.com/rudra-ff130",
        "exp": 9999999999,
    }).encode("ascii"))
    return f"{header}.{payload}.fake-signature"


def test_dev_mode_accepts_demo_tokens():
    """Legacy demo tokens (Bearer user_<id>) work when AUTH_DEV_MODE=true."""
    svc = AuthService(dev_mode=True)
    assert svc.resolve_user_id("Bearer user_student") == "user_student"
    assert svc.resolve_user_id("Bearer user_anything") == "user_anything"
    assert svc.resolve_user_id("user_plain") == "user_plain"
    # No header resolves to guest in dev mode
    assert svc.resolve_user_id(None) == "user_guest"


def test_prod_mode_rejects_demo_tokens():
    """When AUTH_DEV_MODE=false only real (verifiable) Firebase tokens pass."""
    svc = AuthService(dev_mode=False)
    assert svc.resolve_user_id("Bearer user_student") is None
    assert svc.resolve_user_id(None) is None


def test_dev_mode_fallback_extracts_uid_from_unverified_jwt():
    """
    A Firebase-shaped JWT is accepted in dev mode even when offline:
    verification is attempted first, and the uid is extracted from the payload
    as a dev-mode fallback.
    """
    svc = AuthService(dev_mode=True)
    uid = svc.resolve_user_id(f"Bearer {_fake_id_token('firebase_uid_123')}")
    assert uid == "user_firebase_uid_123"


def test_prod_mode_rejects_unverifiable_jwt():
    """Unverifiable JWTs are rejected outright in production mode (no fallback)."""
    svc = AuthService(dev_mode=False)
    assert svc.resolve_user_id(f"Bearer {_fake_id_token('firebase_uid_123')}") is None


def test_decode_unverified_uid_is_defensive():
    """Garbage JWT payloads must not crash uid extraction."""
    assert AuthService._decode_unverified_uid("not.a.jwt") is None
    assert AuthService._decode_unverified_uid("eyJ.%%%.zzz") is None
