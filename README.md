# Zap Scrapper - Imoveis em Poços de Caldas

Scrapper para obter dados de imóveis na cidade de Poços de Caldas, MG. O aplicativo roda o scrapper, formata os dados e faz o load numa base de dados privada do PostgreSQL.

---

## A. Usando docker

1. Defina as seguintes variáveis de ambiente:

```
# PostgreSQL connection information
PSQL_USERNAME=username
PSQL_PASSWORD=p4$$w0rd
PSQL_NAME=dbname
PSQL_HOST=host.com
PSQL_PORT=5432

# Scraping parameters
ZAPSCRAP_ACTION=venda
ZAPSCRAP_TYPE=imoveis
ZAPSCRAP_LOCALIZATION=mg+lavras
ZAPSCRAP_MAX_PAGES=15
```

Você pode exportar uma a uma ou então as coloque em um arquivo `.env` e então rode:

```bash
export $(grep -v '^#' .env | xargs)
```

2. Rode

```bash
docker run \
    -e PSQL_USERNAME -e PSQL_PASSWORD -e PSQL_NAME -e PSQL_HOST -e PSQL_PORT \
    -e ZAPSCRAP_ACTION -e ZAPSCRAP_TYPE -e ZAPSCRAP_LOCALIZATION -e ZAPSCRAP_MAX_PAGES \
    -i emdemor/zapscrap:latest
```

---

## B. Instalação

### 1. Clone o repositório

```bash
git clone git@github.com:emdemor/pc_zap_scrapper.git
cd pc_zap_scrapper
```

### 2. Instale dependências de sistema necessárias para compilação e para o Google Chrome e ChromeDriver

```
sudo apt-get update && apt-get install -y --no-install-recommends \
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
```

### 3. Adicione o repositório do Google Chrome e instale o Chrome

```bash
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && \
    apt-get install -y --no-install-recommends google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*
```

### 4. Baixe e instale o ChromeDriver

```bash
CHROME_DRIVER_VERSION=$(wget -qO- https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver
```

### 5. Instale o playwright

```bash
pip install playwright==1.48.0
playwright install
playwright install-deps
```

### 6. Instale a aplicação

De dentro da raiz do projeto, rode:

```bash
pip install .
```

### 7. execute

```bash
zapscrap scrape -a $ZAPSCRAP_ACTION -t $ZAPSCRAP_TYPE -l $ZAPSCRAP_LOCALIZATION -m $ZAPSCRAP_MAX_PAGES
```
