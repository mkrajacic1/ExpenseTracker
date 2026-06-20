import pytest

from expense_tracker.db import get_db


def test_list_transactions(client):
    response = client.get("/api/transactions")

    assert response.status_code == 200
    data = response.get_json()

    assert data["balance"] == 139960
    assert data["page"] == 1
    assert data["total_count"] == 3
    assert data["total_pages"] == 1
    assert len(data["transactions"]) == 3

    dates = [t["date"] for t in data["transactions"]]
    assert dates == ["2026-06-10", "2026-06-05", "2026-06-01"]

    first = data["transactions"][0]
    assert first["description"] == "Cinema tickets"
    assert first["amount"] == -1500
    assert first["category"] == "Entertainment"


def test_list_transactions_filters(client):
    response = client.get("/api/transactions?category=Groceries")
    data = response.get_json()
    assert data["total_count"] == 1
    assert data["transactions"][0]["description"] == "Weekly groceries"

    response = client.get("/api/transactions?from=2026-06-01&to=2026-06-30")
    data = response.get_json()
    assert data["total_count"] == 3

    response = client.get("/api/transactions?from=2026-06-01")
    data = response.get_json()
    assert data["total_count"] == 3

    response = client.get("/api/transactions?from=2026-13-01")
    data = response.get_json()
    assert data["total_count"] == 3


def test_list_transactions_page_clamp(client):
    response = client.get("/api/transactions?page=999")

    assert response.status_code == 200
    data = response.get_json()
    assert data["page"] == 1
    assert data["total_pages"] == 1


def test_create_transaction(client, app):
    body = {
        "description": "Test expense",
        "amount": 25.50,
        "type": "expense",
        "category": "Groceries",
        "date": "2026-06-08",
    }
    response = client.post("/api/transactions", json=body)

    assert response.status_code == 201
    assert response.headers["Location"] == "/api/transactions/4"
    data = response.get_json()
    assert data["amount"] == -2550

    with app.app_context():
        row = get_db().execute("SELECT amount FROM transactions WHERE id = ?", (data["id"],)).fetchone()
        assert row["amount"] == -2550


def test_create_transaction_income(client):
    body = {
        "description": "Test income",
        "amount": 100,
        "type": "income",
        "category": "Salary",
        "date": "2026-06-08",
    }
    response = client.post("/api/transactions", json=body)
    assert response.status_code == 201
    assert response.get_json()["amount"] == 10000


@pytest.mark.parametrize(("body", "error"), (
    ([], "Request body must be a JSON object"),
    ({"description": "  "}, "Description is required"),
    ({"description": "x" * 101}, "Description must be 100 characters or fewer"),
    ({"description": "Test", "category": "Nope"}, "Invalid category"),
    ({"description": "Test", "category": "Groceries", "date": "2026-06-1"}, "Date must be a valid YYYY-MM-DD date"),
    ({"description": "Test", "category": "Groceries", "date": "2026-02-30"}, "Date must be a valid YYYY-MM-DD date"),
    ({"description": "Test", "category": "Groceries", "date": "2026-06-08"}, "Amount must be a number"),
    ({"description": "Test", "category": "Groceries", "date": "2026-06-08", "amount": 0}, "Amount must be greater than zero"),
    ({"description": "Test", "category": "Groceries", "date": "2026-06-08", "amount": -5}, "Amount must be greater than zero"),
))
def test_create_transaction_invalid(client, body, error):
    response = client.post("/api/transactions", json=body)
    assert response.status_code == 400
    assert response.get_json()["error"] == error


def test_update_transaction(client, app):
    body = {
        "description": "Updated description",
        "amount": 30,
        "type": "expense",
        "category": "Transport",
        "date": "2026-06-09",
    }
    response = client.put("/api/transactions/1", json=body)

    assert response.status_code == 200
    assert response.get_json()["description"] == "Updated description"

    with app.app_context():
        row = get_db().execute("SELECT description, amount FROM transactions WHERE id = 1").fetchone()
        assert row["description"] == "Updated description"
        assert row["amount"] == -3000


def test_update_transaction_not_found(client):
    body = {
        "description": "Updated description",
        "amount": 30,
        "type": "expense",
        "category": "Transport",
        "date": "2026-06-09",
    }
    response = client.put("/api/transactions/999", json=body)
    assert response.status_code == 404


def test_update_transaction_invalid(client):
    body = {"description": "x", "category": "Groceries", "date": "2026-06-08"}
    response = client.put("/api/transactions/1", json=body)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Amount must be a number"


def test_delete_transaction(client, app):
    response = client.delete("/api/transactions/1")

    assert response.status_code == 204
    assert response.data == b""

    with app.app_context():
        row = get_db().execute("SELECT 1 FROM transactions WHERE id = 1").fetchone()
        assert row is None


def test_delete_transaction_not_found(client):
    response = client.delete("/api/transactions/999")
    assert response.status_code == 404


def test_summary(client):
    response = client.get("/api/summary?from=2026-06-01&to=2026-06-30")

    assert response.status_code == 200
    data = response.get_json()

    assert data["total_income"] == 150000
    assert data["total_expenses"] == 10040
    assert data["total_net"] == 139960

    categories = {c["category"]: c for c in data["categories"]}
    assert categories["Salary"] == {"category": "Salary", "income": 150000, "expenses": 0, "net": 150000}
    assert categories["Groceries"] == {"category": "Groceries", "income": 0, "expenses": 8540, "net": -8540}
    assert categories["Entertainment"] == {"category": "Entertainment", "income": 0, "expenses": 1500, "net": -1500}


def test_categories(client):
    response = client.get("/api/categories")

    assert response.status_code == 200
    assert response.get_json() == [
        "Entertainment", "Groceries", "Health", "Other", "Rent", "Salary",
        "Transport", "Utilities",
    ]
