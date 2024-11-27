FROM python:3.11

WORKDIR /app

# Adicionar dependências de sistema necessárias para compilação e para o Google Chrome e ChromeDriver
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libc-dev \
    libssl-dev \
    libffi-dev \
    libbz2-dev \
    liblzma-dev \
    libz-dev \
    wget \
    gnupg \
    unzip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Adicionar o repositório do Google Chrome e instalar o Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && \
    apt-get install -y --no-install-recommends google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Baixar e instalar o ChromeDriver
RUN CHROME_DRIVER_VERSION=$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver

# Configurar variáveis de ambiente para o Selenium
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PATH="/usr/local/bin:${PATH}"

# Instalar o Playwright
RUN pip install playwright==1.48.0
RUN playwright install
RUN playwright install-deps

# Instalar o Selenium
RUN pip install selenium webdriver-manager

COPY ./requirements.txt ./
RUN pip install  -r requirements.txt

COPY ./pc_zap_scrapper ./pc_zap_scrapper
COPY ./notebooks ./notebooks
COPY ./README.md ./
COPY ./LICENSE ./
COPY ./pyproject.toml ./

RUN pip install . --no-deps

ENV ZAPSCRAP_ACTION=venda
ENV ZAPSCRAP_TYPE=imoveis
ENV ZAPSCRAP_LOCALIZATION=mg+pocos-de-caldas
ENV ZAPSCRAP_MAX_PAGES=25

CMD zapscrap scrape -a "${ZAPSCRAP_ACTION}" -t "${ZAPSCRAP_TYPE}" -l "${ZAPSCRAP_LOCALIZATION}" -m "${ZAPSCRAP_MAX_PAGES}"