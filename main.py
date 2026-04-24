from fastapi import FastAPI
from server.db import get_connection
from server.models import PushRequest, PullRequest
from psycopg2.extras import Json

app = FastAPI()


@app.on_event("startup")
def startup():
    conn = get_connection()
    cur = conn.cursor()
    with open("server/schema.sql", "r") as f:
        cur.execute(f.read())
    conn.commit()
    cur.close()
    conn.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/sync/push")
def push(data: PushRequest):
    conn = get_connection()
    cur = conn.cursor()

    for item in data.changes:
        cur.execute("""
            INSERT INTO items (id, value, updated_at, site_id, vector_clock)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET
                value = CASE
                    WHEN EXCLUDED.updated_at > items.updated_at THEN EXCLUDED.value
                    WHEN EXCLUDED.updated_at = items.updated_at 
                         AND EXCLUDED.site_id > items.site_id THEN EXCLUDED.value
                    ELSE items.value
                END,
                updated_at = GREATEST(items.updated_at, EXCLUDED.updated_at),
                site_id = CASE
                    WHEN EXCLUDED.updated_at > items.updated_at THEN EXCLUDED.site_id
                    WHEN EXCLUDED.updated_at = items.updated_at 
                         AND EXCLUDED.site_id > items.site_id THEN EXCLUDED.site_id
                    ELSE items.site_id
                END,
                vector_clock = CASE
                    WHEN EXCLUDED.updated_at >= items.updated_at THEN EXCLUDED.vector_clock
                    ELSE items.vector_clock
                END;
        """, (
            item.id,
            item.value,
            item.updated_at,
            data.site_id,
            Json(item.vector_clock)
        ))

    conn.commit()
    cur.close()
    conn.close()

    return {"status": "merged"}


@app.post("/sync/pull")
def pull(req: PullRequest):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, value, updated_at, site_id, vector_clock
        FROM items
        WHERE updated_at > %s
        ORDER BY updated_at ASC;
    """, (req.since,))

    rows = cur.fetchall()

    results = []
    for row in rows:
        results.append({
            "id": row[0],
            "value": row[1],
            "updated_at": row[2],
            "site_id": row[3],
            "vector_clock": row[4]
        })

    cur.close()
    conn.close()

    return {"changes": results}
