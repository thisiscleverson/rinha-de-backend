FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 5000

CMD ["python", "api/run.py"]