FROM python:3

LABEL org.opencontainers.image.source=https://github.com/zhrif/maybankforme
LABEL org.opencontainers.image.description="helper python script to process maybank cc statement file to something more ingestable"

WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
RUN pip install -e .

ENTRYPOINT [ "maybankforme" ]