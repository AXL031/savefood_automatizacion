FROM python:3.12-slim

WORKDIR /code
COPY backend/ .
COPY foodsave-ml/ /code/foodsave-ml/
RUN pip install --no-cache-dir '.[ml]'
RUN groupadd --system foodsave && useradd --system --gid foodsave --home-dir /code foodsave \
    && mkdir -p /code/model_artifacts \
    && chown -R foodsave:foodsave /code
USER foodsave
CMD ["uvicorn", "app.principal:app", "--host", "0.0.0.0", "--port", "8000"]
