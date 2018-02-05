# SQL Shelf

SQLite-backed library CLI: add books, issue/return loans, list availability, and show items due soon.

## Setup

```bash
python3 library.py init
python3 library.py add "Operating Systems" "Galvin"
python3 library.py add "Database System Concepts" "Silberschatz"
python3 library.py list
```

## Loans

```bash
python3 library.py issue 1 alice --days 14
python3 library.py due --within 7
python3 library.py return 1
```

Database file defaults to `./library.db` (gitignored). Override with `SQL_SHELF_DB`.

## License

MIT
