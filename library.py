#!/usr/bin/env python3
"""sql-shelf — SQLite library CLI (books + loans)."""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from datetime import date, timedelta

DB = os.environ.get("SQL_SHELF_DB", os.path.join(os.path.dirname(__file__), "library.db"))


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS books (
              id INTEGER PRIMARY KEY,
              title TEXT NOT NULL,
              author TEXT NOT NULL,
              available INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS loans (
              id INTEGER PRIMARY KEY,
              book_id INTEGER NOT NULL REFERENCES books(id),
              borrower TEXT NOT NULL,
              loaned_on TEXT NOT NULL,
              due_on TEXT NOT NULL,
              returned_on TEXT
            );
            """
        )
    print(f"initialized {DB}")


def add_book(title: str, author: str) -> None:
    with connect() as conn:
        conn.execute("INSERT INTO books(title, author) VALUES (?, ?)", (title, author))
    print(f"added: {title!r} by {author}")


def list_books() -> None:
    with connect() as conn:
        rows = conn.execute("SELECT id, title, author, available FROM books ORDER BY id").fetchall()
    if not rows:
        print("(no books)")
        return
    for r in rows:
        flag = "yes" if r["available"] else "no"
        print(f"{r['id']:>3}  avail={flag:<3}  {r['title']} — {r['author']}")


def issue(book_id: int, borrower: str, days: int) -> None:
    with connect() as conn:
        book = conn.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
        if not book:
            raise SystemExit(f"book {book_id} not found")
        if not book["available"]:
            raise SystemExit(f"book {book_id} already on loan")
        today = date.today()
        due = today + timedelta(days=days)
        conn.execute(
            "INSERT INTO loans(book_id, borrower, loaned_on, due_on) VALUES (?,?,?,?)",
            (book_id, borrower, today.isoformat(), due.isoformat()),
        )
        conn.execute("UPDATE books SET available=0 WHERE id=?", (book_id,))
    print(f"issued book {book_id} to {borrower}, due {due.isoformat()}")


def return_book(book_id: int) -> None:
    with connect() as conn:
        loan = conn.execute(
            "SELECT id FROM loans WHERE book_id=? AND returned_on IS NULL ORDER BY id DESC LIMIT 1",
            (book_id,),
        ).fetchone()
        if not loan:
            raise SystemExit(f"no open loan for book {book_id}")
        conn.execute(
            "UPDATE loans SET returned_on=? WHERE id=?",
            (date.today().isoformat(), loan["id"]),
        )
        conn.execute("UPDATE books SET available=1 WHERE id=?", (book_id,))
    print(f"returned book {book_id}")


def due_soon(within_days: int) -> None:
    today = date.today()
    limit = today + timedelta(days=within_days)
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT l.id, b.title, l.borrower, l.due_on
            FROM loans l JOIN books b ON b.id = l.book_id
            WHERE l.returned_on IS NULL AND l.due_on <= ?
            ORDER BY l.due_on
            """,
            (limit.isoformat(),),
        ).fetchall()
    if not rows:
        print("(none due soon)")
        return
    for r in rows:
        print(f"loan#{r['id']}  due {r['due_on']}  {r['title']} → {r['borrower']}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="library.py")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init")
    a = sub.add_parser("add")
    a.add_argument("title")
    a.add_argument("author")
    sub.add_parser("list")
    i = sub.add_parser("issue")
    i.add_argument("book_id", type=int)
    i.add_argument("borrower")
    i.add_argument("--days", type=int, default=14)
    r = sub.add_parser("return")
    r.add_argument("book_id", type=int)
    d = sub.add_parser("due")
    d.add_argument("--within", type=int, default=7)

    args = p.parse_args(argv)
    if args.cmd == "init":
        init_db()
    elif args.cmd == "add":
        add_book(args.title, args.author)
    elif args.cmd == "list":
        list_books()
    elif args.cmd == "issue":
        issue(args.book_id, args.borrower, args.days)
    elif args.cmd == "return":
        return_book(args.book_id)
    elif args.cmd == "due":
        due_soon(args.within)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
