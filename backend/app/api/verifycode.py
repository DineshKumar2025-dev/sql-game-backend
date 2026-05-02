from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.levels import level
from app.api.levels.levelsdata import LEVEL_CONFIGS

router = APIRouter()


class VerifyRequest(BaseModel):
    query: str
    level: int
    sublevel: int


@router.post("/verifycode")
def verifycode(payload: VerifyRequest) -> dict[str, object]:
    sql = payload.query.strip()
    if not sql:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty.",
        )

    if not sql.lower().startswith("select"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only SELECT queries are allowed.",
        )

    if payload.level not in LEVEL_CONFIGS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Level {payload.level} is not configured.",
        )

    level_result = level.verify_sublevel(sql, payload.level, payload.sublevel)

    result = {
        "message": "Code verified" if level_result.get("is_correct") else "Query did not match expected output.",
        "is_correct": level_result.get("is_correct", False),
        "error": level_result.get("error"),
        "output": level_result.get("output", []),
        "level_output": level_result.get("level_output", []),
    }
    return result
