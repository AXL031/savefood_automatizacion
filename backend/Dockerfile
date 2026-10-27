FROM python:3.12-slim

WORKDIR /code
COPY backend/ .
COPY foodsave-ml/ /code/foodsave-ml/
RUN --mount=type=cache,target=/root/.cache/pip pip install --timeout 120 --retries 5 '.[ml]'
RUN groupadd --system foodsave && useradd --system --gid foodsave --home-dir /code foodsave \
    && mkdir -p /code/model_artifacts /code/telegram_secrets \
    && chown -R foodsave:foodsave /code
USER foodsave
CMD ["uvicorn", "app.principal:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
