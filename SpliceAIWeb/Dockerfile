FROM python:3.7-slim

RUN apt-get update \
  && apt-get install -y \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /

RUN pip install --no-cache-dir -U pip \
  && pip install --no-cache-dir -r /requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 5001
CMD ["gunicorn", "-b 0.0.0.0:5001", "-t 1200", "-w 4", "spliceai_web.app:app"]
