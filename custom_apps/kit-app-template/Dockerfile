# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

RUN adduser -u 5678 --disabled-password --gecos "" appuser

WORKDIR /app

COPY --chown=appuser:appuser ./_build/ _build/
COPY --chown=appuser:appuser ./tools/ tools/
COPY --chown=appuser:appuser ./requirements.txt .
# Copy the source directory into the container
# This is done separately to ensure that changes in the source directory
# don't invalidate the cache for the rest of the copied files
COPY --chown=appuser:appuser ./source/ /app/source/

USER appuser

ENV OMNI_USER = ""
ENV OMNI_PASS = ""
ENV OMNI_HOST = ""
ENV OMNI_BASE = "/Projects/OVPOC/Stages"
ENV OMNI_SCRIPT = "source/ingest_app_mqtt/run_app.py"
ENV MQTT_HOST = "localhost"
ENV MQTT_TOPIC = "alice-springs-solution/data/opc-ua-connector/opc-ua-connector-0/thermostat"
ENV MQTT_CERT = "C:\\Workspaces\\iot-samples\\source\\ingest_app_mqtt\\client2-authn-ID.key"
ENV MQTT_KEY = "C:\\Workspaces\\iot-samples\\source\\ingest_app_mqtt\\client2-authn-ID.key"


ENTRYPOINT python $OMNI_SCRIPT --server $OMNI_HOST --username $OMNI_USER --password $OMNI_PASS --mqtt_host $MQTT_HOST --mqtt_topic $MQTT_TOPIC