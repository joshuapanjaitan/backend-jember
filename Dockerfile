FROM python:3.9-alpine

ENV PATH="/scripts:${PATH}"

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp

RUN mkdir /auth
EXPOSE 8000

COPY ./auth /auth
WORKDIR /auth
COPY ./scripts /scripts

RUN chmod +x /scripts/*

RUN adduser -D user
USER user

CMD ["entrypoint.sh"]