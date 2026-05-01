from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.levels import level

router = APIRouter()


class VerifyRequest(BaseModel):
    query: str
    level: int
    sublevel: int


LEVEL_HANDLERS = {
    1: level.verify_sublevel,
}


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
    func = LEVEL_HANDLERS.get(payload.level)
    if func is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Level {payload.level} handler not registered.",
        )

    level_result = func(sql, payload.sublevel)
    result = {
        "message": "Code verified" if level_result.get("is_correct") else "Query did not match expected output.",
        "is_correct": level_result.get("is_correct", False),
        "error": level_result.get("error"),
        "output": level_result.get("output", []),
        "level1_output": level_result.get("level1_output", []),
    }
    return result