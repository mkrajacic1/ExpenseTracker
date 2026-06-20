import os
import tempfile

import pytest

from expense_tracker import create_app
from expense_tracker.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), "data.sql"), encoding="utf-8") as f:
    _data_sql = f.read()


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        "TESTING": True,
        "DATABASE": db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()
