import os
import psycopg2
from psycopg2.extras import RealDictCursor, Json

def connect_to_db():
    """Establish a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        host="hpchat.epicapp.com",
        database="hpchat_dev",
        user=os.environ["HPCHAT_PG_USER"],
        password=os.environ["HPCHAT_PG_PASS"]
    )
    return conn

def create_sermons_table():
    """Create the sermons table if it does not exist."""
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sermons (
                    file_name TEXT PRIMARY KEY,
                    url_slug TEXT NOT NULL,
                    title TEXT NOT NULL,
                    biblical_references JSONB,
                    file_path TEXT NOT NULL,
                    transcript JSONB,
                    speaker_name TEXT NOT NULL,
                    one_sentence_summary TEXT,
                    announcements JSONB
                );
                """
            )
            conn.commit()
    finally:
        conn.close()

def listall():
    """List all sermons in the table."""
    conn = connect_to_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM sermons;")
            return cursor.fetchall()
    finally:
        conn.close()

def upsert(sermon):
    """Insert or update a sermon based on the file_name."""
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sermons (file_name, url_slug, title, biblical_references, file_path, transcript, speaker_name, one_sentence_summary, announcements)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (file_name) DO UPDATE SET
                    url_slug = EXCLUDED.url_slug,
                    title = EXCLUDED.title,
                    biblical_references = EXCLUDED.biblical_references,
                    file_path = EXCLUDED.file_path,
                    transcript = EXCLUDED.transcript,
                    speaker_name = EXCLUDED.speaker_name,
                    one_sentence_summary = EXCLUDED.one_sentence_summary,
                    announcements = EXCLUDED.announcements;
                """,
                (
                    sermon["file_name"],
                    sermon["url_slug"],
                    sermon["title"],
                    Json(sermon.get("biblical_references")),
                    sermon["file_path"],
                    Json(sermon.get("transcript")),
                    sermon["speaker_name"],
                    sermon.get("one_sentence_summary"),
                    Json(sermon.get("announcements"))
                )
            )
            conn.commit()
    finally:
        conn.close()

def get(file_name=None, url_slug=None):
    """Fetch a sermon by file_name."""
    conn = connect_to_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if file_name:
                cursor.execute("SELECT * FROM sermons WHERE file_name = %s;", (file_name,))
            elif url_slug:
                cursor.execute("SELECT * FROM sermons WHERE url_slug = %s;", (url_slug,))
            return cursor.fetchone()
    finally:
        conn.close()

# Ensure the sermons table is created
#create_sermons_table()

# Example usage:
# sermons = listall()
# print(sermons)
# upsert({
#     "file_name": "sermon1.mp3",
#     "url_slug": "sermon-on-faith",
#     "title": "Sermon on Faith",
#     "biblical_references": {"verses": ["John 3:16"]},
#     "file_path": "/sermons/sermon1.mp3",
#     "transcript": {"content": "Full transcript here..."},
#     "speaker_name": "Pastor John",
#     "one_sentence_summary": "A sermon about faith and belief.",
#     "announcements": {"event": "Sunday service"}
# })
# sermon = get("sermon-on-faith")
# print(sermon)
