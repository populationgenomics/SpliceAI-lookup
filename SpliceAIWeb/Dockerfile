FROM python:3.7-slim-buster

# Set up gcsfuse: https://cloud.google.com/run/docs/tutorials/network-filesystems-fuse
RUN apt-get update && \
    apt-get install -y curl tini lsb-release gnupg && \
    gcsFuseRepo=gcsfuse-`lsb_release -c -s` && \
    echo "deb http://packages.cloud.google.com/apt $gcsFuseRepo main" | tee /etc/apt/sources.list.d/gcsfuse.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && \
    apt-get install -y gcsfuse && \
    apt-get clean

COPY requirements.txt /

RUN pip install --no-cache-dir -U pip \
  && pip install --no-cache-dir -r /requirements.txt

COPY . /app
WORKDIR /app

RUN chmod +x /app/gcsfuse_run.sh

EXPOSE 8080

# Use tini to manage zombie processes and signal forwarding
# https://github.com/krallin/tini
ENTRYPOINT ["/usr/bin/tini", "--"] 

# Pass the startup script as arguments to Tini
CMD ["/app/gcsfuse_run.sh"]