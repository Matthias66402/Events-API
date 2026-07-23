FROM python:3.12-slim

WORKDIR /app

run pip freeze > requirements.txt

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "app.py"]
