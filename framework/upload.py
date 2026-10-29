# File Upload Handling and Sanitization for Larapak

import os
import re
import secrets
import mimetypes

class PayloadTooLargeError(Exception):
    """Raised when an uploaded payload or file exceeds maximum allowed size."""
    pass


class UploadedFile:
    """Represents an uploaded file with security controls and safe storage methods."""

    def __init__(self, client_filename: str, content: bytes, content_type: str = None, temp_path: str = None):
        self.client_filename = client_filename or "unnamed_file"
        self.content = content if content is not None else b""
        self.size = len(self.content)
        self.content_type = content_type or mimetypes.guess_type(self.client_filename)[0] or "application/octet-stream"
        self.temp_path = temp_path
        
        # Sanitize filename immediately to prevent path traversal
        self.filename = self._sanitize_filename(self.client_filename)

    def _sanitize_filename(self, filename: str) -> str:
        """Strip directory components, null bytes, and dangerous characters."""
        # Strip path components
        base = os.path.basename(filename.replace("\\", "/"))
        # Remove null bytes
        base = base.replace("\0", "")
        # Replace dangerous or traversal characters
        sanitized = re.sub(r'[^a-zA-Z0-9_.\-]', '_', base)
        # Ensure it is not empty, does not start with a dot, and is not too long
        sanitized = sanitized.lstrip(".")
        if not sanitized:
            sanitized = f"upload_{secrets.token_hex(8)}"
        if len(sanitized) > 200:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:190] + ext
        return sanitized

    def save(self, destination_dir: str, custom_filename: str = None, overwrite: bool = False) -> str:
        """
        Safely save the uploaded file into destination_dir.
        Enforces path containment checks to completely block path traversal.
        """
        destination_dir = os.path.abspath(destination_dir)
        os.makedirs(destination_dir, exist_ok=True)

        if custom_filename and (".." in custom_filename or custom_filename.startswith("/") or custom_filename.startswith("\\")):
            raise ValueError(f"Path traversal terdeteksi: '{custom_filename}' tidak valid.")

        target_name = self._sanitize_filename(custom_filename) if custom_filename else self.filename
        target_path = os.path.abspath(os.path.join(destination_dir, target_name))

        # Strict containment verification
        if not target_path.startswith(destination_dir + os.sep) and target_path != destination_dir:
            raise ValueError(f"Path traversal terdeteksi: '{target_path}' berada di luar direktori tujuan.")

        # Avoid accidental overwrite if not explicitly allowed
        if not overwrite and os.path.exists(target_path):
            base, ext = os.path.splitext(target_name)
            counter = 1
            while os.path.exists(target_path):
                target_name = f"{base}_{counter}{ext}"
                target_path = os.path.abspath(os.path.join(destination_dir, target_name))
                counter += 1

        with open(target_path, "wb") as f:
            f.write(self.content)

        return target_path

    def cleanup(self):
        """Remove any underlying temporary file."""
        if self.temp_path and os.path.exists(self.temp_path):
            try:
                os.remove(self.temp_path)
            except OSError:
                pass

    def __repr__(self):
        return f"<UploadedFile filename='{self.filename}' size={self.size} bytes content_type='{self.content_type}'>"
