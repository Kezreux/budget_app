import sqlite3
from pathlib import Path
from datetime import date

DB_NAME = "budget.db"

class BudgetDB:
    def __init__(self, db_path: Path | str = DB_NAME):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()

    def _create_table(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                t_date DATE NOT NULL,
                t_type TEXT NOT NULL CHECK(t_type IN ('income', 'expense')),
                amount REAL NOT NULL,
                description TEXT
            )
            """
        )
        self.conn.commit()

    def add_transaction(self, t_date: date, t_type: str, amount: float, description: str = "") -> None:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO transactions (t_date, t_type, amount, description) VALUES (?, ?, ?, ?)",
            (t_date.isoformat(), t_type, amount, description),
        )
        self.conn.commit()

    def get_month_transactions(self, year: int, month: int):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT t_date, t_type, amount, description FROM transactions WHERE strftime('%Y', t_date) = ? AND strftime('%m', t_date) = ? ORDER BY t_date",
            (str(year), f"{month:02}"),
        )
        return cur.fetchall()

    def get_month_summary(self, year: int, month: int):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT t_type, SUM(amount) FROM transactions WHERE strftime('%Y', t_date) = ? AND strftime('%m', t_date) = ? GROUP BY t_type",
            (str(year), f"{month:02}"),
        )
        totals = {"income": 0.0, "expense": 0.0}
        for t_type, amount in cur.fetchall():
            totals[t_type] = amount or 0.0
        return totals

    def close(self) -> None:
        if self.conn:
            self.conn.close()

