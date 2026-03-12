"""Templates API (placeholder for Phase 5)."""
from fastapi import APIRouter

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.get("")
async def list_templates():
    """List available templates (placeholder)."""
    return {"templates": []}
