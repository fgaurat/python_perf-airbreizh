import sqlite3

from todoapp.todo import Todo


class TodoDAO:

    def __init__(self, db_file):
        self.db_file = db_file
        self._con = sqlite3.connect(db_file)

    def creer_table(self):
        self._con.execute("""
            CREATE TABLE IF NOT EXISTS todos_tbl (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                title     TEXT,
                completed INTEGER
            )
        """)
        self._con.commit()

    def save(self, todo: Todo):
        cur = self._con.cursor()
        cur.execute(f"""
            INSERT INTO todos_tbl (title,completed)
            VALUES ('{todo.title}',{todo.completed})
        """)
        self._con.commit()

    def find_all(self):
        cur = self._con.cursor()
        res = cur.execute("SELECT id,title,completed FROM todos_tbl")
        for t in res.fetchall():
            yield Todo(*t)

    def __del__(self):
        self._con.close()
