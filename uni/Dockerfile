# SPDX-License-Identifier: CC-BY-4.0
# © 2025 HES-SO / HEG Geneva / Deep Mining Lab / FairOnChain / Open Price ETH

FROM python:3.11-slim-bullseye

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libssl-dev \
    pkg-config \
    cron \
    git \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
 && /root/.cargo/bin/cargo install --root /usr/local cryo_cli
ENV PATH="/usr/local/bin:${PATH}"

RUN groupadd -g 1000 debian && \
    useradd -m -u 1000 -g debian debian

RUN mkdir -p /app/uni/logs /app/uni \
  && mkdir -p /home/debian/.ssh \
  && ssh-keyscan github.com > /home/debian/.ssh/known_hosts \
  && chmod 700 /home/debian/.ssh \
  && chmod 600 /home/debian/.ssh/known_hosts \
  && chown -R debian:debian /app /home/debian/.ssh

USER debian

RUN git config --global user.name "UNI Bot" \
 && git config --global user.email "uni_bot@heg.ch"

WORKDIR /app

COPY --chown=debian:debian uni/requirements.txt uni/requirements.txt
COPY --chown=debian:debian uni/scripts uni/scripts
COPY --chown=debian:debian uni/data uni/data
COPY --chown=debian:debian .git .git
COPY --chown=debian:debian .gitignore ./

RUN pip install --no-cache-dir -r uni/requirements.txt \
  && chmod +x uni/scripts/*.sh

COPY --chown=debian:debian uni/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
