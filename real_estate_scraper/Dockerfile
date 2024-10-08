FROM python:3.10

WORKDIR /real_estate_scraper

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["python3", "main.py"]
