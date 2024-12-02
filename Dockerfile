FROM python:3.11

COPY requirements.txt /opt
RUN pip install --no-cache-dir -r /opt/requirements.txt

COPY entrypoint.sh /entrypoint.sh
COPY src /app/src

ENV PYTHONPATH /app

WORKDIR /app

USER nobody

ENTRYPOINT [ "/entrypoint.sh" ]
