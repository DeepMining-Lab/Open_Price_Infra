# Image de base avec Python et dépendances nécessaires
FROM python:3.11-slim-bullseye

# Dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libssl-dev \
    pkg-config \
    cron \
    git \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Installer cryo
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
 && /root/.cargo/bin/cargo install --root /usr/local cryo_cli
ENV PATH="/usr/local/bin:${PATH}"


# Create a custom user with UID 1234 and GID 1234
RUN groupadd -g 1000 debian && \
    useradd -m -u 1000 -g debian debian


 RUN mkdir -p /app/eth/logs /app/eth \
  && mkdir -p /home/debian/.ssh \
  && ssh-keyscan github.com > /home/debian/.ssh/known_hosts \
  && chmod 700 /home/debian/.ssh \
  && chmod 600 /home/debian/.ssh/known_hosts \
  && chown -R debian:debian /app /home/debian/.ssh


# # Switch to the custom user
USER debian

# Configurer l'identité Git du bot
RUN git config --global user.name "ETH Bot" \
 && git config --global user.email "eth_bot@heg.ch"

# Set the workdir
WORKDIR /app

COPY --chown=debian:debian eth/requirements.txt eth/requirements.txt
COPY --chown=debian:debian eth/README.md eth/README.md
COPY --chown=debian:debian eth/scripts eth/scripts
COPY --chown=debian:debian eth/data eth/data
COPY --chown=debian:debian .git .git
COPY --chown=debian:debian .gitignore ./

RUN pip install --no-cache-dir -r eth/requirements.txt \
  && chmod +x eth/scripts/*.sh

# Point d'entrée personnalisé
COPY --chown=debian:debian eth/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh


ENTRYPOINT ["docker-entrypoint.sh"]