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
# Create a directory "certs" in the container which we can use to mount a volume

RUN mkdir /certs

WORKDIR /app

ADD --chown=appuser:appuser ./requirements.txt /app/
# Copy the source directory into the container
# This is done separately to ensure that changes in the source directory
# don't invalidate the cache for the rest of the copied files
ADD --chown=appuser:appuser ./ /app/source/mqtt_sim
RUN chown -R appuser:appuser /certs

USER appuser

ENV OMNI_SCRIPT = ""
ENV SIM_CERT_PATH = ""
ENV SIM_KEY_PATH = ""
ENV CSV_PATH = ""

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

ENTRYPOINT "python3" $OMNI_SCRIPT --sim_cert_path $SIM_CERT_PATH --sim_key_path $SIM_KEY_PATH --csv_path $CSV_PATH & "python3" source/mqtt_sim/health_check.py