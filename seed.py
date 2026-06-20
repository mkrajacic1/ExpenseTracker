from datetime import date

from expense_tracker import create_app
from expense_tracker.db import get_db


def insert_seed(conn, description, amount_euros, category, date_str):
    conn.execute(
        "INSERT INTO transactions (description, amount, category, date) VALUES (?, ?, ?, ?)",
        (description, round(amount_euros * 100), category, date_str),
    )


def main():
    app = create_app()
    with app.app_context():
        conn = get_db()
        count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        if count > 0:
            print("Database already has data, skipping seed.")
            return

        today = date.today()

        insert_seed(conn, "Monthly salary", 1500.00, "Salary", today.isoformat())
        insert_seed(conn, "Monthly rent", -700.00, "Rent", today.isoformat())
        insert_seed(conn, "Weekly groceries", -85.40, "Groceries", today.isoformat())

        conn.commit()
        conn.close()
        print(f"Seeded database at {today.isoformat()}")


if __name__ == "__main__":
    main()