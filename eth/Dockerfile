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

# Installer Rust et Cargo (requis pour cryo)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Installer cryo
RUN cargo install cryo_cli

# Créer le répertoire de l'application
WORKDIR /app
RUN mkdir -p /app/eth/logs
RUN mkdir -p /app/eth

# Set the workdir
# WORKDIR /home/debian

# Copier les fichiers nécessaires
COPY eth/requirements.txt eth/requirements.txt
COPY eth/README.md eth/README.md
COPY eth/scripts eth/scripts
COPY eth/data eth/data
COPY .git .git
COPY .gitignore ./

# Rendre les scripts exécutables
RUN chmod +x eth/scripts/*.sh

# Installer les dépendances Python
RUN pip install --no-cache-dir -r eth/requirements.txt

# Point d'entrée personnalisé
COPY eth/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# # Create a custom user with UID 1234 and GID 1234
# RUN groupadd -g 1000 debian && \
#     useradd -m -u 1000 -g debian debian
# # Switch to the custom user
# USER debian

ENTRYPOINT ["docker-entrypoint.sh"]