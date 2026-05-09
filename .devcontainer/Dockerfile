FROM mcr.microsoft.com/devcontainers/base:noble

RUN apt-get update \
    && apt-get install -y --no-install-recommends bubblewrap \
    && rm -rf /var/lib/apt/lists/*
