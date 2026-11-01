FROM node:22-slim

ENV HOME=/home/node
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends git python3 python3-pip ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g --no-fund --no-audit opencode-ai@1.19.5 @mariozechner/pi-coding-agent@0.73.1

ADD https://github.com/charmbracelet/crush/releases/download/v0.99.0/crush_0.99.0_Linux_x86_64.tar.gz /tmp/crush.tar.gz
RUN set -eux; \
    echo "ec20f001028dfb7b6427225f0cf5215081275c8f09f45001a8535847cc4fd6ea  /tmp/crush.tar.gz" | sha256sum -c -; \
    mkdir -p /tmp/crush; \
    tar -xzf /tmp/crush.tar.gz -C /tmp/crush; \
    find /tmp/crush -type f -name 'crush' -exec install -m 0755 {} /usr/local/bin/crush \; ; \
    rm -rf /tmp/crush /tmp/crush.tar.gz; \
    crush --version

RUN pip3 install --break-system-packages --no-cache-dir pydantic requests blessed python-dotenv

COPY configs/opencode.jsonc /tmp/opencode.jsonc
COPY configs/crush.json /tmp/crush.json

RUN set -eux; \
    mkdir -p /home/node/.config/opencode /home/node/.config/crush; \
    cp /tmp/opencode.jsonc /home/node/.config/opencode/opencode.jsonc; \
    cp /tmp/crush.json /home/node/.config/crush/crush.json; \
    rm -f /tmp/opencode.jsonc /tmp/crush.json; \
    chown -R node:node /home/node

USER node
WORKDIR /workdir
