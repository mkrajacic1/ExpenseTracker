FROM python:3.14-slim

WORKDIR /app

COPY . .

RUN chmod +x /app/entrypoint.sh

RUN pip install --no-cache-dir -e .

RUN useradd app
USER app

ENTRYPOINT ["/app/entrypoint.sh"]