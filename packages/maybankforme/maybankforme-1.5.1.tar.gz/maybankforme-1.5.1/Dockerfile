FROM python:3.12-alpine

LABEL org.opencontainers.image.source=https://github.com/zhrif/maybankforme
LABEL org.opencontainers.image.description="helper python script to process maybank cc statement file to something more ingestable"

WORKDIR /app

RUN apk add --no-cache git

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY .git /app/.git
COPY src /app/src
COPY pyproject.toml /app/
RUN pip install -e .

ENTRYPOINT [ "maybankforme" ]