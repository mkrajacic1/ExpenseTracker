import re
from datetime import date

from expense_tracker.db import get_db


DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

PAGE_SIZE = 10


def parse_date(date_str):
    if not DATE_PATTERN.match(date_str):
        return None
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        return None


def build_date_filter(date_from, date_to):
    conditions = []
    params = []
    if parse_date(date_from):
        conditions.append("date >= ?")
        params.append(date_from)
    if parse_date(date_to):
        conditions.append("date <= ?")
        params.append(date_to)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    return where, params


def list_transactions(page, category, date_from, date_to):
    per_page = PAGE_SIZE

    where, params = build_date_filter(date_from, date_to)
    if category:
        where += " AND category = ?" if where else " WHERE category = ?"
        params.append(category)

    db = get_db()
    balance = db.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions").fetchone()[0]
    total_count = db.execute(f"SELECT COUNT(*) FROM transactions{where}", params).fetchone()[0]
    total_pages = max((total_count + per_page - 1) // per_page, 1)
    if page > total_pages:
        page = total_pages

    rows = db.execute(
        f"SELECT id, description, amount, category, date FROM transactions{where}"
        " ORDER BY date DESC, id DESC LIMIT ? OFFSET ?",
        [*params, per_page, (page - 1) * per_page],
    ).fetchall()

    transactions = [
        {"id": row["id"], "description": row["description"], "amount": row["amount"],
         "category": row["category"], "date": row["date"]}
        for row in rows
    ]

    return {
        "balance": balance,
        "transactions": transactions,
        "page": page,
        "total_count": total_count,
        "total_pages": total_pages,
    }


def validate_transaction(data):
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object"

    description = data.get("description", "").strip()
    if not description:
        return None, "Description is required"
    if len(description) > 100:
        return None, "Description must be 100 characters or fewer"

    category = data.get("category", "")
    exists = get_db().execute("SELECT 1 FROM categories WHERE name = ?", (category,)).fetchone()
    if not exists:
        return None, "Invalid category"

    date_str = data.get("date", "")
    transaction_date = parse_date(date_str)
    if transaction_date is None:
        return None, "Date must be a valid YYYY-MM-DD date"

    try:
        amount_euros = float(data.get("amount"))
    except (TypeError, ValueError):
        return None, "Amount must be a number"
    if amount_euros <= 0:
        return None, "Amount must be greater than zero"

    amount_cents = round(amount_euros * 100)
    if data.get("type") == "expense":
        amount_cents = -amount_cents

    return (amount_cents, description, category, transaction_date.isoformat()), None


def create_transaction(fields):
    amount, description, category, date_str = fields
    db = get_db()
    with db:
        cursor = db.execute(
            "INSERT INTO transactions (description, amount, category, date) VALUES (?, ?, ?, ?)",
            (description, amount, category, date_str),
        )

    return {"id": cursor.lastrowid, "description": description, "amount": amount,
            "category": category, "date": date_str}


def update_transaction(transaction_id, fields):
    amount, description, category, date_str = fields
    db = get_db()
    with db:
        cursor = db.execute(
            "UPDATE transactions SET description = ?, amount = ?, category = ?, date = ? WHERE id = ?",
            (description, amount, category, date_str, transaction_id),
        )
    if not cursor.rowcount:
        return None

    return {"id": transaction_id, "description": description, "amount": amount,
            "category": category, "date": date_str}


def delete_transaction(transaction_id):
    db = get_db()
    with db:
        cursor = db.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))

    return bool(cursor.rowcount)


def get_summary(date_from, date_to):
    where, params = build_date_filter(date_from, date_to)

    rows = get_db().execute(
        "SELECT category,"
        "SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS income,"
        "SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END) AS expenses,"
        "SUM(amount) AS net"
        f" FROM transactions{where}"
        "GROUP BY category ORDER BY net",
        params,
    ).fetchall()

    categories = [
        {
            "category": row["category"], 
            "income": row["income"],
            "expenses": row["expenses"], 
            "net": row["net"]
        }
        for row in rows
    ]

    return {
        "from": date_from,
        "to": date_to,
        "categories": categories,
        "total_income": sum(category["income"] for category in categories),
        "total_expenses": sum(category["expenses"] for category in categories),
        "total_net": sum(category["net"] for category in categories),
    }
