FROM python:3.11-slim

RUN mkdir -p /app/src/services/etl
RUN touch /app/src/__init__.py
RUN touch /app/src/services/__init__.py
RUN apt-get update && apt-get install -y openjdk-17-jdk cron

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:${PATH}"

RUN apt-get update && apt-get install -y python3

WORKDIR /app

COPY main.py /app
COPY transform.py /app/src/services/etl/
COPY load.py /app/src/services/etl/
COPY utils.py /app/src/services/etl/
COPY .env /app/src/services/etl/
COPY requirements.txt /app/src/services/etl/
COPY cronjob /app/src/services/etl/

WORKDIR /app/src/services/etl
RUN pip3 install --no-cache-dir -r requirements.txt
COPY cronjob /etc/cron.d/cronjob
RUN chmod 0644 /etc/cron.d/cronjob

RUN crontab /etc/cron.d/cronjob


RUN touch /var/log/cron.log

CMD cron && tail -f /var/log/cron.log
