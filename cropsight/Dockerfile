# Use a slim base image to redu
FROM python:3.10

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y default-mysql-client
RUN pip install --upgrade pip
RUN pip install -r requirements/production.txt

# Set the working directory inside the container
# Install system dependencies (minimal to reduce build si
# Copy only the requirements file first (lever
# Expose Django's default port
EXPOSE 8000

# Start the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]

