FROM python:3.14-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

COPY .env.docker ./.env

RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev

COPY . .

CMD ["uv", "run", "python", "main.py"]