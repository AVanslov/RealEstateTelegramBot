FROM python:3.10

WORKDIR /bot

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . /bot

CMD ["python", "./bot/main.py"]