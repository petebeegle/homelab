# Runner image for the dev-smoke check: the official Playwright image (Chromium and
# its OS libraries preinstalled) plus the GitHub Actions runner, kubectl, the Flux
# CLI and Python. The Playwright tag must match tests/browser/package.json
# (tools/development/tests/test_runner_image.py enforces it).
FROM mcr.microsoft.com/playwright:v1.65.1-noble

# Versions are pinned and every download is checksum-verified. kubectl matches the
# dev cluster's Kubernetes version and flux matches the dev cluster's Flux version.
ARG RUNNER_VERSION=2.338.2
ARG RUNNER_SHA256=baebf204307bac6193480852732f0aba2ae97b6c5597c244f4d5558390147c40
ARG KUBECTL_VERSION=v1.35.0
ARG KUBECTL_SHA256=a2e984a18a0c063279d692533031c1eff93a262afcc0afdc517375432d060989
ARG FLUX_VERSION=2.9.6
ARG FLUX_SHA256=b4d22673e9246cbd628881f1a9ef3b090085dced291e42d804555cee8e8d42c5

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl git jq python3 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL -o /usr/local/bin/kubectl "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
    && echo "${KUBECTL_SHA256}  /usr/local/bin/kubectl" | sha256sum -c - \
    && chmod 0755 /usr/local/bin/kubectl

RUN curl -fsSL -o /tmp/flux.tgz "https://github.com/fluxcd/flux2/releases/download/v${FLUX_VERSION}/flux_${FLUX_VERSION}_linux_amd64.tar.gz" \
    && echo "${FLUX_SHA256}  /tmp/flux.tgz" | sha256sum -c - \
    && tar -xzf /tmp/flux.tgz -C /usr/local/bin flux \
    && rm /tmp/flux.tgz

# ARC expects the runner at /home/runner and starts /home/runner/run.sh. UID 1001 is
# taken by the base image's pwuser, so the runner user is 1002 (pod securityContext must match).
RUN useradd --create-home --uid 1002 --shell /bin/bash runner \
    && curl -fsSL -o /tmp/runner.tgz "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz" \
    && echo "${RUNNER_SHA256}  /tmp/runner.tgz" | sha256sum -c - \
    && tar -xzf /tmp/runner.tgz -C /home/runner \
    && rm /tmp/runner.tgz \
    && /home/runner/bin/installdependencies.sh \
    && chown -R runner:runner /home/runner

USER runner
WORKDIR /home/runner
