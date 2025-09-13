from fastapi import APIRouter

router = APIRouter()

@router.get("/healthz")
def healthz():
    """Health check endpoint.
    
    Returns:
        Dictionary with status indicating service health
    """
    return {"status": "ok"}