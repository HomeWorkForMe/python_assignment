FROM python:3.10.0-alpine
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
ENV FLASK_APP=app/app.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000