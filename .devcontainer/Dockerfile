FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

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

# python tooling
RUN pip install --no-cache-dir pre-commit

# project dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
