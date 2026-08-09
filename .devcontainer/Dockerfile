FROM mcr.microsoft.com/devcontainers/base:noble

ARG OP_CLI_VERSION=2.35.0
ARG OP_CLI_SHA256=4457ade59850b852c64c77164235b34dd0b984ef7826eb0ccd32f1fd78a2ceb7

RUN apt-get update \
    && apt-get install -y --no-install-recommends bubblewrap unzip \
    && curl --fail --show-error --location \
      "https://cache.agilebits.com/dist/1P/op2/pkg/v${OP_CLI_VERSION}/op_linux_amd64_v${OP_CLI_VERSION}.zip" \
      --output /tmp/op.zip \
    && printf '%s  %s\n' "$OP_CLI_SHA256" /tmp/op.zip | sha256sum --check --strict \
    && unzip -q /tmp/op.zip -d /tmp/op \
    && install -m 0755 /tmp/op/op /usr/local/bin/op \
    && rm -rf /var/lib/apt/lists/* /tmp/op /tmp/op.zip
