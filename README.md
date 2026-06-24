# Expense Tracker

A full-stack personal expense tracking application.

## Description

Expense Tracker is built with **Python**, **Flask** and **SQLite** on the backend,
and HTML/CSS/JavaScript on the frontend.

The app features a REST API for creating, accessing, updating and deleting transactions
on the user's account, as well as an expense summary by category for a selected period.

Backend has 100% test coverage (`pytest` + `coverage`).

Containerized using **Docker**.

## API endpoints

| Method   | Endpoint                 | Description                                                                                |
| -------- | ------------------------ | ------------------------------------------------------------------------------------------ |
| `GET`    | `/api/transactions`      | Paginated transaction list and total balance. Parameters: `page`, `category`, `from`, `to` |
| `POST`   | `/api/transactions`      | Create a transaction. Returns `201` with a `Location` header; `400` on validation errors   |
| `PUT`    | `/api/transactions/<id>` | Replace a transaction. Returns `200`, or `404` if it doesn't exist                         |
| `DELETE` | `/api/transactions/<id>` | Delete a transaction. Returns `204`, or `404`                                              |
| `GET`    | `/api/summary`           | Income, expenses and net amount per category for a date range (`from`, `to`)               |
| `GET`    | `/api/categories`        | List of valid category names                                                               |

## Installation and setup

#### Requirements

- **git**
- **Docker**

#### Clone the repository

```bash
git clone https://github.com/mkrajacic1/ExpenseTracker
```

#### Run the app container using Docker Compose

Inside the repository run:

```bash
cd ExpenseTracker
docker compose up -d
```

Once running, open http://localhost:5000

On first start, the container runs entrypoint.sh, which seeds the database
with a few example transactions via seed.py, but only if databse was empty.

## Testing and development

#### Requirements

- **Python >=3.12**

#### Create and activate venv

Inside the repository, create a virtual environment and activate it

```bash
python -m venv .venv
. .venv/bin/activate
```

#### Install the project package with dev option

```bash
python -m pip install -e ".[dev]"
```

#### Run tests and see coverage report

```bash
coverage run -m pytest
coverage report
```
