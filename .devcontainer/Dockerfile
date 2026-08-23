FROM mcr.microsoft.com/devcontainers/python:1-3.13-bookworm

RUN find /etc/apt/sources.list.d -type f -exec grep -l "yarnpkg" {} \; | xargs -r rm -f

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        texlive-latex-base \
        texlive-latex-recommended \
        texlive-latex-extra \
        texlive-fonts-recommended \
        texlive-science \
        latexmk \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# install uv globally via its official installer
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/