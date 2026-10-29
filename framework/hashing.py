# Password Hashing and Verification for Larapak
# Supports Argon2id (if argon2-cffi is installed) and PBKDF2-SHA256 (standard library)

import os
import hmac
import base64
import hashlib
import secrets

try:
    from argon2 import PasswordHasher, Type
    from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
    _ARGON2_AVAILABLE = True
    _argon2_hasher = PasswordHasher(
        time_cost=2,
        memory_cost=65536,
        parallelism=1,
        hash_len=32,
        type=Type.ID
    )
except ImportError:
    _ARGON2_AVAILABLE = False
    _argon2_hasher = None

# Default PBKDF2 parameters (OWASP recommended baseline)
_PBKDF2_ITERATIONS = 100_000
_SALT_BYTES = 16


class Hash:
    """Password hashing and verification utility for Larapak."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain text password using Argon2id or PBKDF2-SHA256."""
        if not isinstance(password, str):
            raise TypeError("Password harus bertipe string.")
        
        if _ARGON2_AVAILABLE and _argon2_hasher is not None:
            return _argon2_hasher.hash(password)
        
        # Fallback to standard library PBKDF2-SHA256
        salt = secrets.token_bytes(_SALT_BYTES)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            _PBKDF2_ITERATIONS
        )
        salt_b64 = base64.b64encode(salt).decode("ascii")
        hash_b64 = base64.b64encode(digest).decode("ascii")
        return f"$pbkdf2-sha256$i={_PBKDF2_ITERATIONS},l=32${salt_b64}${hash_b64}"

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against an encoded hash.
        Supports Argon2id, PBKDF2-SHA256, and safe legacy plain-text comparison for migration.
        """
        if not isinstance(password, str) or not isinstance(hashed_password, str):
            return False

        if hashed_password.startswith("$argon2"):
            if not _ARGON2_AVAILABLE or _argon2_hasher is None:
                # Argon2 hash found but library not installed
                return False
            try:
                return _argon2_hasher.verify(hashed_password, password)
            except (VerifyMismatchError, VerificationError, InvalidHashError):
                return False
            except Exception:
                return False

        if hashed_password.startswith("$pbkdf2-sha256$"):
            try:
                parts = hashed_password.split("$")
                # ['', 'pbkdf2-sha256', 'i=100000,l=32', salt_b64, hash_b64]
                if len(parts) != 5:
                    return False
                
                params = parts[2].split(",")
                iterations = _PBKDF2_ITERATIONS
                for p in params:
                    if p.startswith("i="):
                        iterations = int(p.split("=")[1])
                
                salt = base64.b64decode(parts[3].encode("ascii"))
                stored_digest = base64.b64decode(parts[4].encode("ascii"))
                
                computed_digest = hashlib.pbkdf2_hmac(
                    "sha256",
                    password.encode("utf-8"),
                    salt,
                    iterations
                )
                return hmac.compare_digest(stored_digest, computed_digest)
            except Exception:
                return False

        # Legacy plain-text detection for backward-compatible migration
        # Constant-time comparison to prevent timing side-channel
        try:
            return hmac.compare_digest(password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False

    @staticmethod
    def needs_rehash(hashed_password: str) -> bool:
        """
        Check if a stored password needs to be re-hashed:
        - If it is plain-text
        - If it is PBKDF2 but Argon2 has become available
        - If PBKDF2 iteration count is outdated
        """
        if not isinstance(hashed_password, str):
            return True

        if not Hash.is_hashed(hashed_password):
            return True

        if _ARGON2_AVAILABLE and not hashed_password.startswith("$argon2"):
            return True

        if hashed_password.startswith("$pbkdf2-sha256$"):
            try:
                parts = hashed_password.split("$")
                if len(parts) == 5:
                    params = parts[2].split(",")
                    for p in params:
                        if p.startswith("i="):
                            iters = int(p.split("=")[1])
                            if iters < _PBKDF2_ITERATIONS:
                                return True
            except Exception:
                return True

        return False

    @staticmethod
    def is_hashed(value: str) -> bool:
        """Check if a string represents a supported secure hash."""
        if not isinstance(value, str):
            return False
        return value.startswith("$argon2") or value.startswith("$pbkdf2-sha256$")


# Standalone function helpers matching standard framework conventions
hash_password = Hash.hash_password
verify_password = Hash.verify_password
needs_rehash = Hash.needs_rehash
is_hashed = Hash.is_hashed
