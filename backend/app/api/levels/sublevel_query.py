from fastapi import APIRouter, Query

from app.api.levels import level as level_mod

router = APIRouter()


@router.get("/sublevel_query")
def get_sublevel_query(
    level: str = Query(..., min_length=1),
    user_id: int = Query(...),
) -> dict[str, object]:
    """Return the saved query for a sublevel key (e.g. l11), same id verifycode stores in level_id."""
    query_text = level_mod.sublevel_query(level.strip(), user_id)
    if query_text is None:
        return {"query": None}
    return {"query": query_text}
