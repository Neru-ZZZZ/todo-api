FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn sqlalchemy
COPY ./app .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]