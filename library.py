#!/usr/bin/env python3
"""library-card-chaos — tiny SQLite library CLI (DBMS lab era)."""

from __future__ import print_function
import sqlite3, sys, os
from datetime import datetime, timedelta

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library.db")


def conn():
 return sqlite3.connect(DB)


def init_db():
 c = conn()
 c.execute(
 """CREATE TABLE IF NOT EXISTS books (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 title TEXT NOT NULL,
 author TEXT NOT NULL,
 available INTEGER DEFAULT 1
 )"""
 )
 c.execute(
 """CREATE TABLE IF NOT EXISTS loans (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 book_id INTEGER,
 borrower TEXT,
 issued_on TEXT,
 due_on TEXT,
 returned INTEGER DEFAULT 0,
 FOREIGN KEY(book_id) REFERENCES books(id)
 )"""
 )
 c.commit()
 c.close()
 print("db ready:", DB)


def add_book(title, author):
 c = conn()
 c.execute("INSERT INTO books(title, author) VALUES (?, ?)", (title, author))
 c.commit()
 print("added book id", c.execute("SELECT last_insert_rowid()").fetchone()[0])
 c.close()


def list_books():
 c = conn()
 rows = c.execute("SELECT id, title, author, available FROM books").fetchall()
 c.close()
 if not rows:
 print("(no books — empty shelves, empty soul)")
 return
 for r in rows:
 flag = "IN" if r[3] else "OUT"
 print("[%s] #%d %s — %s" % (flag, r[0], r[1], r[2]))


def main(argv):
 if len(argv) < 1:
 print("usage: init | add TITLE AUTHOR | list")
 return 1
 cmd = argv[0]
 if cmd == "init":
 init_db()
 elif cmd == "add" and len(argv) >= 3:
 add_book(argv[1], " ".join(argv[2:]))
 elif cmd == "list":
 list_books()
 else:
 print("unknown command")
 return 1
 return 0


if __name__ == "__main__":
 sys.exit(main(sys.argv[1:]))
