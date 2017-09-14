#!/usr/bin/env python3
"""library-card-chaos — tiny SQLite library CLI (DBMS lab era)."""

from __future__ import print_function
import sqlite3, sys, os
from datetime import datetime, timedelta

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library.db")
LOAN_DAYS = 14


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
 print("(no books)")
 return
 for r in rows:
 flag = "IN" if r[3] else "OUT"
 print("[%s] #%d %s — %s" % (flag, r[0], r[1], r[2]))


def issue(book_id, borrower):
 c = conn()
 row = c.execute("SELECT available FROM books WHERE id=?", (book_id,)).fetchone()
 if not row:
 print("book not found")
 c.close()
 return
 if not row[0]:
 print("already issued — chaos reigns")
 c.close()
 return
 now = datetime.now()
 due = now + timedelta(days=LOAN_DAYS)
 c.execute(
 "INSERT INTO loans(book_id, borrower, issued_on, due_on) VALUES (?,?,?,?)",
 (book_id, borrower, now.isoformat(timespec="seconds"), due.isoformat(timespec="seconds")),
 )
 c.execute("UPDATE books SET available=0 WHERE id=?", (book_id,))
 c.commit()
 c.close()
 print("issued to %s; due %s" % (borrower, due.date()))


def return_book(book_id):
 c = conn()
 loan = c.execute(
 "SELECT id, due_on FROM loans WHERE book_id=? AND returned=0",
 (book_id,),
 ).fetchone()
 if not loan:
 print("no active loan")
 c.close()
 return
 due = datetime.fromisoformat(loan[1])
 late = datetime.now() > due
 c.execute("UPDATE loans SET returned=1 WHERE id=?", (loan[0],))
 c.execute("UPDATE books SET available=1 WHERE id=?", (book_id,))
 c.commit()
 c.close()
 if late:
 print("returned LATE. the librarian has noted this. forever.")
 else:
 print("returned on time. rare. beautiful.")


def main(argv):
 if len(argv) < 1:
 print("usage: init | add TITLE AUTHOR | list | issue ID BORROWER | return ID")
 return 1
 cmd = argv[0]
 if cmd == "init":
 init_db()
 elif cmd == "add" and len(argv) >= 3:
 add_book(argv[1], " ".join(argv[2:]))
 elif cmd == "list":
 list_books()
 elif cmd == "issue" and len(argv) >= 3:
 issue(int(argv[1]), argv[2])
 elif cmd == "return" and len(argv) >= 2:
 return_book(int(argv[1]))
 else:
 print("unknown command")
 return 1
 return 0


if __name__ == "__main__":
 sys.exit(main(sys.argv[1:]))
