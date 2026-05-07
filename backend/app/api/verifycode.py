from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from app.api.routes.auth import _database_url
from app.api.levels import level
from app.api.levels.levelsdata import LEVEL_CONFIGS

router = APIRouter()


def _strip_leading_sql_noise(sql: str) -> str:
    """Remove BOM, whitespace, and line/block comments before the first real statement."""
    s = sql.strip().removeprefix("\ufeff")
    while True:
        t = s.lstrip()
        if not t:
            return ""
        if t.startswith("--"):
            nl = t.find("\n")
            if nl == -1:
                return ""
            s = t[nl + 1:]
            continue
        if t.startswith("/*"):
            end = t.find("*/")
            if end == -1:
                return t
            s = t[end + 2:]
            continue
        return t


def _is_select_like(sql: str) -> bool:
    head = _strip_leading_sql_noise(sql).lower()
    return head.startswith("select") or head.startswith("with")


class VerifyRequest(BaseModel):
    query: str
    level: int
    sublevel: str
    user_id: int | None = None


@router.post("/verifycode")
def verifycode(payload: VerifyRequest) -> dict[str, object]:
    sql = payload.query.strip()

    if not _strip_leading_sql_noise(sql):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty.",
        )

    # Levels 1-6 are read-only SELECT missions.
    # Levels 7+ can include CRUD / transactions / EXPLAIN / CREATE INDEX etc.
    if payload.level <= 6 and not _is_select_like(sql):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only SELECT (or WITH … SELECT) queries are allowed.",
        )

    if payload.level not in LEVEL_CONFIGS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Level {payload.level} is not configured.",
        )

    level_result = level.verify_sublevel(sql, payload.level, payload.sublevel)
    is_correct = level_result.get("is_correct")

    if payload.user_id is not None:
        conn = psycopg2.connect(_database_url())
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Check if record exists
                cursor.execute(
                    "SELECT * FROM levelscompleted WHERE user_id = %s AND level_id = %s",
                    (payload.user_id, payload.sublevel)
                )
                rows = cursor.fetchall()

                update_sql = None
                params = None

                if len(rows) > 0 and is_correct == True:
                    # Record exists + correct → mark completed
                    update_sql = "UPDATE levelscompleted SET query = %s, status = 'completed' WHERE user_id = %s AND level_id = %s"
                    params = (sql, payload.user_id, payload.sublevel)

                elif len(rows) > 0 and is_correct == False:
                    # Record exists + wrong → keep 'completed' if already completed, else 'pending'
                    new_status = 'completed' if rows[0].get("status") == 'completed' else 'pending'
                    update_sql = "UPDATE levelscompleted SET query = %s, status = %s WHERE user_id = %s AND level_id = %s"
                    params = (sql, new_status, payload.user_id, payload.sublevel)

                elif len(rows) == 0 and is_correct == True:
                    # No record + correct → insert as completed
                    update_sql = "INSERT INTO levelscompleted (user_id, level_id, query, status) VALUES (%s, %s, %s, 'completed')"
                    params = (payload.user_id, payload.sublevel, sql)

                elif len(rows) == 0 and is_correct == False:
                    # No record + wrong → insert as pending
                    update_sql = "INSERT INTO levelscompleted (user_id, level_id, query, status) VALUES (%s, %s, %s, 'pending')"
                    params = (payload.user_id, payload.sublevel, sql)

                wrote = False
                if update_sql and params:
                    cursor.execute(update_sql, params)
                    wrote = True

                if (
                    is_correct
                    and level.is_final_sublevel(payload.level, payload.sublevel)
                ):
                    main_level_id = str(payload.level)
                    cursor.execute(
                        "SELECT 1 FROM levelscompleted WHERE user_id = %s AND level_id = %s LIMIT 1",
                        (payload.user_id, main_level_id),
                    )
                    rollup_query = "-- level completed"
                    if cursor.fetchone() is not None:
                        cursor.execute(
                            "UPDATE levelscompleted SET query = %s, status = 'completed' "
                            "WHERE user_id = %s AND level_id = %s",
                            (rollup_query, payload.user_id, main_level_id),
                        )
                    else:
                        cursor.execute(
                            "INSERT INTO levelscompleted (user_id, level_id, query, status) "
                            "VALUES (%s, %s, %s, 'completed')",
                            (payload.user_id, main_level_id, rollup_query),
                        )
                    wrote = True

                if wrote:
                    conn.commit()

        except Exception as e:
            conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )
        finally:
            conn.close()

    if(is_correct):
        output = level_result.get("output", [])
    else:
        output = level_result.get("level_output", []),
    result = {
        "message": "Code verified" if is_correct else "Query did not match expected output.",
        "is_correct": is_correct or False,
        "error": level_result.get("error"),
        "output": output,
    }
    return result