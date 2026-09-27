FROM python:3.12-slim

WORKDIR /code
COPY . .
RUN pip install --no-cache-dir .
RUN groupadd --system foodsave && useradd --system --gid foodsave --home-dir /code foodsave \
    && chown -R foodsave:foodsave /code
USER foodsave
CMD ["uvicorn", "app.principal:app", "--host", "0.0.0.0", "--port", "8000"]
