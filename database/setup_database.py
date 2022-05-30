import sqlite3

DB_NAME = "database.db"
DB_PATH = "database/database.db"  # Relative path from the project root directory


def create_db_sqlite():
    conn = sqlite3.connect(DB_NAME)
    conn.commit()

    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE events (
            id int,
            type text,
            repo_id int,
            repo_name text,
            created_at integer,
            unique(id))        
        """)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_db_sqlite()
