import sqlite3

DB_PATH = "database/database.db"  # Relative path from the project root directory


def create_db_sqlite():
    """
    Create a new sqlite database with a single 'events' table.
    :return:
    """
    conn = sqlite3.connect(DB_PATH)
    conn.commit()

    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS events (
            id int,
            type text,
            repo_id int,
            repo_name text,
            created_at integer,
            unique(id))        
        """)
    conn.commit()
    conn.close()
