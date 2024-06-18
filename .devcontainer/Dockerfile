FROM mcr.microsoft.com/devcontainers/base:jammy

RUN apt update && apt install -y \
    curl \
	pipx

RUN curl -LO https://github.com/talos-systems/talos/releases/latest/download/talosctl-linux-amd64 && \
	chmod +x talosctl-linux-amd64 && \
	mv talosctl-linux-amd64 /usr/local/bin/talosctl

USER vscode

RUN pipx install --include-deps ansible \
	&& pipx install ansible-lint \
	&& pipx install pre-commit
