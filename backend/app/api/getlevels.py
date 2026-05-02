import psycopg2
from fastapi import APIRouter, HTTPException, status
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

from app.api.routes.auth import _database_url

router = APIRouter()


class LevelRow(BaseModel):
    id: int
    title: str
    topic: str
    main_level: int


@router.get("/getlevels", response_model=list[LevelRow])
def get_levels() -> list[dict[str, object]]:
    """Return roadmap rows: sub-levels where main_level = 0, ordered by id."""
    sql = """
        SELECT id, title, topic, main_level
        FROM levels
        WHERE main_level = 0
        ORDER BY id ASC
    """
    try:
        connection = psycopg2.connect(_database_url())
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not connect to database: {exc}",
        ) from exc

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
    except psycopg2.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {exc}",
        ) from exc
    finally:
        connection.close()

    return [dict(r) for r in rows]
