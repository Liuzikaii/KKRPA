"""
License API routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.license import (
    validate_license_key, save_license, load_license,
    generate_license_key, get_current_edition,
)
from app.config import settings

router = APIRouter(prefix="/api/license", tags=["License"])


class ActivateRequest(BaseModel):
    license_key: str


class LicenseResponse(BaseModel):
    activated: bool
    edition: str
    message: str


class GenerateRequest(BaseModel):
    edition: str = "community"


@router.post("/activate", response_model=LicenseResponse)
async def activate_license(data: ActivateRequest):
    """Activate a license key."""
    result = validate_license_key(data.license_key)
    if not result:
        raise HTTPException(status_code=400, detail="无效的激活码")

    # Save license
    save_license(result["key"], result["edition"])

    # Update runtime settings
    settings.LICENSE_KEY = result["key"]
    settings.EDITION = result["edition"]

    edition_label = "企业版" if result["edition"] == "enterprise" else "社区版"
    return LicenseResponse(
        activated=True,
        edition=result["edition"],
        message=f"激活成功！当前版本: {edition_label}",
    )


@router.get("/status", response_model=LicenseResponse)
async def get_license_status():
    """Get current license status."""
    license_info = load_license()
    if license_info and license_info.get("valid"):
        edition_label = "企业版" if license_info["edition"] == "enterprise" else "社区版"
        return LicenseResponse(
            activated=True,
            edition=license_info["edition"],
            message=f"已激活 - {edition_label}",
        )
    return LicenseResponse(
        activated=False,
        edition="community",
        message="未激活 - 社区版（免费）",
    )


@router.post("/generate")
async def generate_key(data: GenerateRequest):
    """Generate a license key (for development/testing only)."""
    key = generate_license_key(data.edition)
    return {"license_key": key, "edition": data.edition}
