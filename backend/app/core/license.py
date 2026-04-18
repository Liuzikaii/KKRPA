"""
License Key generation and validation system.
Format: KKRPA-{TYPE}-{PAYLOAD}-{CHECKSUM}
  TYPE: CE (Community), EE (Enterprise)
  PAYLOAD: 8 random hex chars
  CHECKSUM: HMAC-SHA256 truncated to 8 hex chars
"""
import hashlib
import hmac
import secrets
import os
import json
from typing import Optional
from app.config import settings, get_data_dir

# Secret used for HMAC signing — hardcoded for offline validation
_LICENSE_SECRET = b"KKRPA-2024-License-Validation-Key"


def generate_license_key(edition: str = "community") -> str:
    """Generate a valid license key for the given edition."""
    type_code = "EE" if edition == "enterprise" else "CE"
    payload = secrets.token_hex(4).upper()  # 8 hex chars
    raw = f"KKRPA-{type_code}-{payload}"
    checksum = hmac.new(_LICENSE_SECRET, raw.encode(), hashlib.sha256).hexdigest()[:8].upper()
    return f"{raw}-{checksum}"


def validate_license_key(key: str) -> Optional[dict]:
    """
    Validate a license key. Returns edition info or None if invalid.

    Valid format: KKRPA-{CE|EE}-{8 hex}-{8 hex checksum}
    """
    if not key:
        return None

    parts = key.strip().upper().split("-")
    if len(parts) != 4:
        return None

    prefix, type_code, payload, checksum = parts

    if prefix != "KKRPA":
        return None
    if type_code not in ("CE", "EE"):
        return None
    if len(payload) != 8 or len(checksum) != 8:
        return None

    # Verify HMAC checksum
    raw = f"KKRPA-{type_code}-{payload}"
    expected = hmac.new(_LICENSE_SECRET, raw.encode(), hashlib.sha256).hexdigest()[:8].upper()

    if not hmac.compare_digest(checksum, expected):
        return None

    edition = "enterprise" if type_code == "EE" else "community"
    return {
        "valid": True,
        "edition": edition,
        "key": key.upper(),
        "type_code": type_code,
    }


def save_license(key: str, edition: str):
    """Save activated license to local file."""
    data_dir = get_data_dir()
    license_file = os.path.join(data_dir, "license.json")
    data = {"key": key, "edition": edition}
    with open(license_file, "w") as f:
        json.dump(data, f)


def load_license() -> Optional[dict]:
    """Load saved license from local file."""
    data_dir = get_data_dir()
    license_file = os.path.join(data_dir, "license.json")
    if not os.path.exists(license_file):
        return None
    try:
        with open(license_file, "r") as f:
            data = json.load(f)
        # Re-validate the saved key
        result = validate_license_key(data.get("key", ""))
        return result
    except Exception:
        return None


def get_current_edition() -> str:
    """Get the current activated edition."""
    license_info = load_license()
    if license_info and license_info.get("valid"):
        return license_info["edition"]
    return "community"
