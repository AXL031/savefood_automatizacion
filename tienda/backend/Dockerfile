FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY checkout ./checkout
RUN useradd --uid 10001 --create-home tienda && mkdir /datos && chown tienda:tienda /datos
USER tienda
EXPOSE 8001
CMD ["uvicorn", "checkout.principal:app", "--host", "0.0.0.0", "--port", "8001", "--no-access-log"]
