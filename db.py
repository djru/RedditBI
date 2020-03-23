import sqlite3
from constants import SQLITE_FILE
import time

# https://docs.python.org/3/library/sqlite3.html
# https://sqlitebrowser.org/

# https://stackoverflow.com/questions/48218065/programmingerror-sqlite-objects-created-in-a-thread-can-only-be-used-in-that-sa
cols = ('id', 'state', 'code', 'token', 'refresh_token', 'name', 'email', 'deleted_count', 'confirmed', 'updated')

def create_table():
    with sqlite3.connect(SQLITE_FILE) as conn:
        # https://sqlite.org/autoinc.html
        create_table_sql = """CREATE TABLE IF NOT EXISTS Users (
                                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                                   state TEXT NOT NULL,
                                   code TEXT NOT NULL,
                                   token TEXT,
                                   refresh_token TEXT,
                                   name TEXT UNIQUE,
                                   email TEXT UNIQUE,
                                   deleted_count INTEGER DEFAULT 0,
                                   confirmed TEXT,
                                   updated INTEGER
                                );"""
        create_nameindex_sql = """CREATE UNIQUE INDEX IF NOT EXISTS name 
                                ON Users (name);"""
        create_stateindex_sql = """CREATE UNIQUE INDEX IF NOT EXISTS state 
                                ON Users (state);"""
        create_codeindex_sql = """CREATE UNIQUE INDEX IF NOT EXISTS code 
                                        ON Users (code);"""
        c = conn.cursor()
        c.execute(create_table_sql)
        c.execute(create_nameindex_sql)
        c.execute(create_stateindex_sql)
        c.execute(create_codeindex_sql)
        conn.commit()

def create_user(state, code):
    with sqlite3.connect(SQLITE_FILE) as conn:
        insert_sql = f"INSERT INTO Users(state, code, updated) VALUES(?,?,?)"
        c = conn.cursor()
        c.execute(insert_sql, (state, code, str(int(time.time()))))
        conn.commit()
    return c.lastrowid

def get_user_by_state(state):
    with sqlite3.connect(SQLITE_FILE) as conn:
        select_sql = "SELECT * FROM Users WHERE state=?"
        c = conn.cursor()
        c.execute(select_sql, (state,))
        rows = c.fetchall()
        r = None
        for row in rows:
            r = dict(zip(cols, row))
        return r

def get_user_by_code(code):
    with sqlite3.connect(SQLITE_FILE) as conn:
        select_sql = "SELECT * FROM Users WHERE code=?"
        c = conn.cursor()
        c.execute(select_sql, (code,))
        rows = c.fetchall()
        r = None
        for row in rows:
            r = dict(zip(cols, row))
        return r

def get_user_by_id(id):
    with sqlite3.connect(SQLITE_FILE) as conn:
        select_sql = "SELECT * FROM Users WHERE id=?"
        c = conn.cursor()
        c.execute(select_sql, (id,))
        rows = c.fetchall()
        r = None
        for row in rows:
            r =  dict(zip(cols, row))
        return r

def delete_user_by_id(id):
    with sqlite3.connect(SQLITE_FILE) as conn:
        select_sql = "DELETE FROM Users WHERE id=?"
        c = conn.cursor()
        c.execute(select_sql, (id,))
        conn.commit()

def delete_user_by_name(name):
    with sqlite3.connect(SQLITE_FILE) as conn:
        select_sql = "DELETE FROM Users WHERE name=?"
        c = conn.cursor()
        c.execute(select_sql, (name,))
        conn.commit()

def get_user_by_name(name):
    with sqlite3.connect(SQLITE_FILE) as conn:
        select_sql = "SELECT * FROM Users WHERE name=?"
        c = conn.cursor()
        c.execute(select_sql, (name,))
        rows = c.fetchall()
        r = None
        for row in rows:
            r =  dict(zip(cols, row))
        return r

def get_all_users():
    with sqlite3.connect(SQLITE_FILE) as conn:
        select_sql = "SELECT * FROM Users"
        c = conn.cursor()
        c.execute(select_sql)
        rows = c.fetchall()
        r = []
        for row in rows:
            r.append(dict(zip(cols, row)))
        return r

def update_user(id, cols, vals):
    with sqlite3.connect(SQLITE_FILE) as conn:
        cols = (f'{c}=?' for c in cols)
        cols_str = ','.join(cols)
        update_sql = f"UPDATE Users SET {cols_str}, updated=? WHERE id=?"
        c = conn.cursor()
        c.execute(update_sql, vals + (str(int(time.time())), id,))
        conn.commit()
        return c.lastrowid

# create_table()

if __name__ == '__main__':
    create_table()