FROM python:alpine
RUN apk update && apk add gcc libxml2-dev libxslt-dev libc-dev
RUN pip install wxpy bs4 lxml
ADD . /code
CMD python /code/bot.py
