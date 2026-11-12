"""Import transactions from the original Flask ExpenseTracker database.

Run from backend/: python scripts/import_legacy_sqlite.py your-account@example.com
"""
import argparse
import sqlite3
from datetime import date
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import User, Expense

DEFAULT_SOURCE = Path(__file__).resolve().parents[1] / "legacy_data" / "legacy_expenses.db"

def main():
    parser = argparse.ArgumentParser(description="Import the old Flask ExpenseTracker transactions into your Pennywise account.")
    parser.add_argument("email", help="Email address of the account you created in Pennywise")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE), help="Path to the old database.db file")
    args = parser.parse_args()
    source = Path(args.source)
    if not source.exists(): raise SystemExit(f"Legacy database not found: {source}")
    old = sqlite3.connect(source)
    old.row_factory = sqlite3.Row
    rows = old.execute("SELECT title, amount, category, transaction_type, date, description FROM transactions ORDER BY id").fetchall()
    old.close()
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == args.email.lower()).first()
        if not user: raise SystemExit("Account not found. Register in Pennywise first, then run this script again.")
        imported = skipped = 0
        for row in rows:
            spent_on = date.fromisoformat(row["date"])
            kind = "income" if row["transaction_type"].lower() == "income" else "expense"
            exists = db.query(Expense).filter(Expense.user_id == user.id, Expense.title == row["title"], Expense.amount == row["amount"], Expense.spent_on == spent_on, Expense.transaction_type == kind).first()
            if exists:
                skipped += 1
                continue
            db.add(Expense(title=row["title"], amount=row["amount"], category=row["category"], transaction_type=kind, spent_on=spent_on, description=row["description"] or None, user_id=user.id))
            imported += 1
        db.commit()
        print(f"Import complete for {user.email}: {imported} imported, {skipped} already present.")
    finally:
        db.close()

if __name__ == "__main__": main()
