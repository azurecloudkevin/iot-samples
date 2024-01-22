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

ENV OMNI_SCRIPT = ""
ENV MQTT_HOST = ""
ENV MQTT_TOPIC = ""
ENV MQTT_CERT = ""
ENV MQTT_KEY = ""


ENTRYPOINT python $OMNI_SCRIPT --server $OMNI_HOST --username $OMNI_USER --password $OMNI_PASS --mqtt_host $MQTT_HOST --mqtt_topic $MQTT_TOPIC