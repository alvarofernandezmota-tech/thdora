import sqlite3

DB_PATH = "data/thdora.db"


def run():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("PRAGMA table_info(appointments)")
    cols = [row[1] for row in cur.fetchall()]
    if "user_id" not in cols:
        cur.execute("ALTER TABLE appointments ADD COLUMN user_id INTEGER DEFAULT 1")
        cur.execute("UPDATE appointments SET user_id = 1 WHERE user_id IS NULL")
        con.commit()
        print("Migracion completada.")
    else:
        print("user_id ya existe, nada que hacer.")
    con.close()


if __name__ == "__main__":
    run()
