FROM python:3.10

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y default-mysql-client
RUN pip install --upgrade pip
RUN pip install -r requirements/production.txt

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
