from flask import Blueprint, render_template, request, url_for

from .db import get_db
from . import services


bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/api/categories")
def api_categories():
    rows = get_db().execute("SELECT name FROM categories ORDER BY name").fetchall()

    return [row["name"] for row in rows]


@bp.route("/api/transactions")
def api_list_transactions():
    page = max(1, request.args.get("page", default=1, type=int))
    category = request.args.get("category", default="")
    date_from = request.args.get("from", default="")
    date_to = request.args.get("to", default="")

    return services.list_transactions(page, category, date_from, date_to)


@bp.route("/api/transactions", methods=["POST"])
def api_create_transaction():
    fields, error = services.validate_transaction(request.get_json(silent=True))
    if error:
        return {"error": error}, 400
    transaction = services.create_transaction(fields)
    location = url_for("main.api_update_transaction", transaction_id=transaction["id"])

    return transaction, 201, {"Location": location}


@bp.route("/api/transactions/<int:transaction_id>", methods=["PUT"])
def api_update_transaction(transaction_id):
    fields, error = services.validate_transaction(request.get_json(silent=True))
    if error:
        return {"error": error}, 400
    transaction = services.update_transaction(transaction_id, fields)
    if transaction is None:
        return {"error": "Transaction not found"}, 404
    
    return transaction


@bp.route("/api/transactions/<int:transaction_id>", methods=["DELETE"])
def api_delete_transaction(transaction_id):
    if not services.delete_transaction(transaction_id):
        return {"error": "Transaction not found"}, 404
    
    return "", 204


@bp.route("/api/summary")
def api_summary():
    date_from = request.args.get("from", default="")
    date_to = request.args.get("to", default="")
    return services.get_summary(date_from, date_to)

