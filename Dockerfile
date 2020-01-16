FROM mdillon/postgis

RUN apt update
RUN apt install python3-pip -y

RUN mkdir /app
COPY requirements.txt /app/requirements.txt
COPY src/syncer.py /app/syncer.py

ENV CONFIG_FILE /app/config.yaml
COPY defaults/config.yaml /app/config.yaml

ENV WATCH /app/data
RUN mkdir /app/data

WORKDIR /app

RUN pip3 install -r requirements.txt
ENTRYPOINT python3 syncer.py config.yaml
