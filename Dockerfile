FROM python:3.12.4

COPY src/ ./
COPY requirements.txt .

RUN pip install -r requirements.txt

ENTRYPOINT ["python3.12", "main.py"]