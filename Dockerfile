FROM python:alpine
RUN apk update && apk add gcc libxml2-dev libxslt-dev libc-dev
RUN pip install wxpy bs4 lxml flask gunicorn
ADD . /code
WORKDIR /code
EXPOSE 8000
CMD gunicorn main:app -b 0.0.0.0
