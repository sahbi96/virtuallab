FROM python:3.9.1-alpine
RUN apk add --update --no-cache \
    g++ gcc libxslt-dev musl-dev python3-dev \
    libffi-dev openssl-dev jpeg-dev zlib-dev postgresql-dev
RUN mkdir /home/Backend
WORKDIR /home/Backend
COPY ./ ./

RUN apk add --update unrar 
RUN pip install --upgrade pip
RUN apk add gcc musl-dev python3-dev libffi-dev openssl-dev cargo
RUN pip install -r requirements.txt

EXPOSE 8000

CMD python manage.py runserver 0.0.0.0:8000
