from fastapi import APIRouter, Query

from app.api.levels import level as level_mod

router = APIRouter()


@router.get("/level_sublevel")
def get_level_sublevel(
    level: int = Query(..., ge=1),
    user_id: int = Query(...),
) -> dict[str, object]:
    row = level_mod.level_sublevel(level, user_id)
    if row is None:
        return {"level_id": None}
    return {"level_id": row.get("level_id")}
