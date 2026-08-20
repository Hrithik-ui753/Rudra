import uuid
import base64
import json
import time
import datetime
from typing import Dict, Any, List, Optional

import httpx

from config import settings
from models.schemas import UserProfile, HistoryRow
from utils.logger import logger

# Firebase public signing certificates (no service account required to verify ID tokens)
_FIREBASE_CERTS_URL = "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
_FIREBASE_CERTS_TTL_SECONDS = 3600

_certs_cache: Dict[str, Any] = {"certs": None, "fetched_at": 0.0}


class AuthService:
    """
    Authentication & User Session Management Service.

    Resolves the authenticated user id from the Authorization header:

    * Production mode (AUTH_DEV_MODE=false): the Bearer token MUST be a real
      Firebase ID token (JWT). It is verified against Firebase public signing
      certificates (signature, audience, issuer, expiry). Fabricated or expired
      tokens are rejected (resolution returns None).
    * Dev mode (AUTH_DEV_MODE=true, default): legacy demo tokens such as
      "Bearer user_student" or "Bearer user_<any-id>" are accepted so the demo
      and test-suite work without Firebase credentials. Real Firebase ID tokens
      are still verified when presented.
    """

    def __init__(self, dev_mode: Optional[bool] = None):
        # In-memory storage for users and chat history
        self.dev_mode = settings.AUTH_DEV_MODE if dev_mode is None else dev_mode
        self._users: Dict[str, UserProfile] = {}
        self._tokens: Dict[str, str] = {}  # token -> user_id
        self._history: Dict[str, List[HistoryRow]] = {}  # user_id -> history rows

        # Pre-seed default demo users
        self._seed_default_users()

    def _seed_default_users(self):
        student = UserProfile(
            id="user_student",
            name="Varun Goud",
            email="student@campus.edu",
            role="student",
            branch="CIVIL",
            department="CIVIL",
            roll_no="1602-26-732-001",
            year="1st Year",
            section="A"
        )
        faculty = UserProfile(
            id="user_faculty",
            name="Dr. B.Sridhar",
            email="faculty@campus.edu",
            role="faculty",
            branch="CIVIL",
            department="CIVIL",
            roll_no="FAC-2325",
            year="N/A",
            section="N/A"
        )
        self._users[student.id] = student
        self._users[faculty.id] = faculty
        self._tokens["Bearer user_student"] = student.id
        self._tokens["Bearer user_faculty"] = faculty.id

    def resolve_user_id(self, auth_header: Optional[str]) -> Optional[str]:
        """
        Resolve a verified user id from the Authorization header.

        Returns None when the presented credentials cannot be verified; callers
        that require authentication should respond with HTTP 401. Read-only
        endpoints may fall back to the "user_guest" id instead.
        """
        if not auth_header:
            return "user_guest" if self.dev_mode else None

        token = auth_header.strip()
        if token.lower().startswith("bearer "):
            token_val = token[7:].strip()
        else:
            token_val = token

        if not token_val:
            return "user_guest" if self.dev_mode else None

        # Firebase ID tokens are JWTs and always start with "eyJ"
        if token_val.startswith("eyJ"):
            uid = self._verify_firebase_id_token(token_val)
            if uid:
                return f"user_{uid}"
            # Dev-mode fallback: extract the uid from the (unverified) payload so
            # the local demo keeps working even without network access to Google.
            if self.dev_mode:
                unverified_uid = self._decode_unverified_uid(token_val)
                if unverified_uid:
                    return f"user_{unverified_uid}"
            logger.warning("[AUTH] Rejected unverifiable Firebase ID token.")
            return None

        # Non-JWT tokens are only accepted in dev mode
        if not self.dev_mode:
            logger.warning("[AUTH] Rejected non-JWT token in production mode.")
            return None

        if token_val in self._users:
            return token_val
        elif token_val.startswith("user_"):
            return token_val
        elif f"Bearer {token_val}" in self._tokens:
            return self._tokens[f"Bearer {token_val}"]
        return f"user_{token_val}"

    def extract_user_id_from_header(self, auth_header: Optional[str]) -> str:
        """
        Backward-compatible resolver used by public/read endpoints.
        Unverifiable credentials fall back to the guest id.
        """
        return self.resolve_user_id(auth_header) or "user_guest"

    # ------------------------------------------------------------------
    # Firebase ID token verification
    # ------------------------------------------------------------------

    def _verify_firebase_id_token(self, token: str) -> Optional[str]:
        """
        Verify a Firebase ID token (JWT) against Firebase public certificates.
        Validates signature, audience, issuer and expiry.
        """
        try:
            from google.auth import jwt as google_jwt
        except ImportError:
            logger.error("[AUTH] google-auth is not installed; cannot verify Firebase ID tokens.")
            return None

        project_id = settings.FIREBASE_PROJECT_ID
        certs = self._get_firebase_certs()
        if not certs:
            logger.warning("[AUTH] Could not fetch Firebase signing certificates.")
            return None

        try:
            decoded = google_jwt.decode(
                token,
                certs=certs,
                audience=project_id,
                issuer=f"https://securetoken.google.com/{project_id}",
                algorithms=["RS256"],
            )
            uid = decoded.get("sub")
            return uid if uid else None
        except Exception as e:
            logger.warning(f"[AUTH] Firebase ID token verification failed: {e}")
            return None

    def _get_firebase_certs(self) -> Optional[Dict[str, str]]:
        """Fetch and cache Firebase public signing certificates (TTL 1 hour)."""
        now = time.time()
        if _certs_cache["certs"] and (now - _certs_cache["fetched_at"]) < _FIREBASE_CERTS_TTL_SECONDS:
            return _certs_cache["certs"]

        try:
            resp = httpx.get(_FIREBASE_CERTS_URL, timeout=10)
            resp.raise_for_status()
            certs = resp.json()
            _certs_cache["certs"] = certs
            _certs_cache["fetched_at"] = now
            return certs
        except Exception as e:
            logger.warning(f"[AUTH] Failed to fetch Firebase signing certificates: {e}")
            return None

    @staticmethod
    def _decode_unverified_uid(token: str) -> Optional[str]:
        """Best-effort uid extraction from a JWT payload WITHOUT signature verification.
        Only used in dev mode so the demo survives offline operation."""
        try:
            payload = token.split(".")[1]
            payload += "=" * (-len(payload) % 4)
            data = json.loads(base64.urlsafe_b64decode(payload))
            return data.get("sub")
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Profile & history
    # ------------------------------------------------------------------

    def get_or_create_profile(self, user_id: str, default_name: str = "Campus User") -> UserProfile:
        """Get existing user profile or create a default guest profile."""
        if user_id in self._users:
            return self._users[user_id]

        new_profile = UserProfile(
            id=user_id,
            name=default_name,
            email=f"{user_id}@campus.edu",
            role="student",
            branch="CIVIL",
            department="CIVIL",
            roll_no="1602-26-732-001",
            year="1st Year",
            section="A"
        )
        self._users[user_id] = new_profile
        return new_profile

    def update_profile(self, user_id: str, patch_data: Dict[str, Any]) -> UserProfile:
        """Update existing user profile fields."""
        profile = self.get_or_create_profile(user_id)

        updated_dict = profile.model_dump()
        for k, v in patch_data.items():
            if v is not None and k in updated_dict:
                updated_dict[k] = v

        # Normalize department/branch sync
        if patch_data.get("branch") and not patch_data.get("department"):
            updated_dict["department"] = patch_data["branch"]
        elif patch_data.get("department") and not patch_data.get("branch"):
            updated_dict["branch"] = patch_data["department"]

        updated_profile = UserProfile(**updated_dict)
        self._users[user_id] = updated_profile
        logger.info(f"Updated profile for user '{user_id}': {updated_profile.name}")
        return updated_profile

    def add_history_message(
        self,
        user_id: str,
        session_id: str,
        sender: str,
        message: str,
        agent_name: Optional[str] = None,
        suggested_followups: Optional[List[str]] = None
    ) -> HistoryRow:
        """Record a chat message in the user's conversation history."""
        row = HistoryRow(
            id=str(uuid.uuid4()),
            session_id=session_id,
            sender=sender,
            message=message,
            created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            agent_name=agent_name,
            suggested_followups=suggested_followups or []
        )
        if user_id not in self._history:
            self._history[user_id] = []
        self._history[user_id].append(row)
        return row

    def get_user_history(self, user_id: str) -> List[HistoryRow]:
        """Retrieve conversation history for a given user."""
        return self._history.get(user_id, [])
