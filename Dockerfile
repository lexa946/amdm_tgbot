FROM python:3.11-slim

COPY app ./app
COPY requirements.txt requirements.txt
COPY *.py ./

RUN python -m pip install --upgrade pip && pip install -r requirements.txt

CMD ["python3", "main.py"]