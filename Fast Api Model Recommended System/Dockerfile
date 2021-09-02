FROM python:3.8

RUN apt-get update && \
    apt-get install -y openjdk-11-jre-headless && \
    apt-get clean;

WORKDIR /app

COPY ./requirements.txt  /app

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

EXPOSE 6200

COPY ./  /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6200"]
