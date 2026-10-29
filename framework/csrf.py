# CSRF Protection Layer for Larapak

import hmac
import secrets
import fnmatch
from .env import env

class CSRFException(Exception):
    """Raised when CSRF token verification fails."""
    pass


class CSRF:
    """Manages secure CSRF tokens and request validation."""

    SAFE_METHODS = ("GET", "HEAD", "OPTIONS")
    _exempt_routes = set()

    @classmethod
    def exempt(cls, path_pattern: str):
        """Explicitly exempt an endpoint or wildcard pattern from CSRF verification."""
        cls._exempt_routes.add(path_pattern)

    @classmethod
    def clear_exemptions(cls):
        """Clear all registered exemptions."""
        cls._exempt_routes.clear()

    @classmethod
    def is_exempt(cls, path: str) -> bool:
        """Check if a path matches explicit exemptions or env config."""
        env_exempt = env("CSRF_EXEMPT_ROUTES", "")
        if env_exempt:
            for pattern in env_exempt.split(","):
                pattern = pattern.strip()
                if pattern and fnmatch.fnmatch(path, pattern):
                    return True

        for pattern in cls._exempt_routes:
            if fnmatch.fnmatch(path, pattern):
                return True
        return False

    @classmethod
    def token(cls, session) -> str:
        """Retrieve existing CSRF token or generate a new session-bound token."""
        if session is None:
            return ""
        
        token = None
        if hasattr(session, "get"):
            token = session.get("_token")
        elif hasattr(session, "entuk"):
            token = session.entuk("_token")
            
        if not token:
            token = secrets.token_urlsafe(32)
            if hasattr(session, "set"):
                session.set("_token", token)
            elif hasattr(session, "pasang"):
                session.pasang("_token", token)
        return str(token)

    @classmethod
    def regenerate_token(cls, session) -> str:
        """Regenerate a new CSRF token for the session (e.g. after login)."""
        if session is None:
            return ""
        token = secrets.token_urlsafe(32)
        if hasattr(session, "set"):
            session.set("_token", token)
        elif hasattr(session, "pasang"):
            session.pasang("_token", token)
        return token

    @classmethod
    def verify(cls, req, session) -> bool:
        """
        Verify CSRF token for state-changing HTTP requests.
        Must be called with effective/spoofed HTTP method.
        Raises CSRFException if token is missing or invalid.
        """
        method = (req.method or "GET").upper()
        if method in cls.SAFE_METHODS:
            return True

        # Check explicit exemptions
        if cls.is_exempt(req.path):
            return True

        # Extract submitted token from request body or supported headers
        submitted_token = None
        if hasattr(req, "body") and isinstance(req.body, dict):
            submitted_token = req.body.get("_token")

        if not submitted_token and hasattr(req, "headers"):
            headers = req.headers
            submitted_token = (
                headers.get("X-CSRF-TOKEN")
                or headers.get("x-csrf-token")
                or headers.get("X-XSRF-TOKEN")
                or headers.get("x-xsrf-token")
            )

        if not submitted_token:
            raise CSRFException("Token CSRF tidak ditemukan pada request.")

        # Expected token from session
        expected_token = None
        if session:
            if hasattr(session, "get"):
                expected_token = session.get("_token")
            elif hasattr(session, "entuk"):
                expected_token = session.entuk("_token")

        if not expected_token:
            raise CSRFException("Sesi tidak memiliki token CSRF yang valid.")

        # Constant-time comparison
        if not hmac.compare_digest(str(submitted_token), str(expected_token)):
            raise CSRFException("Token CSRF tidak cocok atau tidak valid.")

        return True
