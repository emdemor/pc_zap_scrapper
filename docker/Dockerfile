FROM python:3.11

WORKDIR /app

# Adicionar dependências de sistema necessárias para compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libc-dev \
    libssl-dev \
    libffi-dev \
    libbz2-dev \
    liblzma-dev \
    libz-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PIP_DISABLE_PIP_VERSION_CHECK=on

COPY ./requirements.txt ./requirements.txt 
RUN pip install -r requirements.txt

COPY ./pc_zap_scrapper ./pc_zap_scrapper
COPY ./README.md ./README.md
COPY ./LICENSE ./LICENSE
COPY ./pyproject.toml ./pyproject.toml 
RUN pip install . --no-deps

RUN chmod -R a+x .