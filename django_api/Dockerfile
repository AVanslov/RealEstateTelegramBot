FROM python:3.10

WORKDIR /app

RUN pip install gunicorn==20.1.0

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

ADD entrypoint.sh .

ENTRYPOINT ["sh", "./entrypoint.sh"]