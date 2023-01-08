# Zap Scrapper - Imoveis em Poços de Caldas

Scrapper para obter dados de imóveis na cidade de Poços de Caldas, MG. O aplicativo roda o scrapper, formata os dados e faz o load numa base de dados privada do PostgreSQL.

---

## 1. Instalação
A instalação é dada através do `pip`:
```bash
$ pip install pc_zap_scrapper 
```
---

## 2. Configurando a conexão com o banco
Na etapa de load do banco de dados, é necessário fornecer as credenciais do banco de dados. Serão necessárias as informações:
* `DB_USERNAME`
* `DB_PASSWORD`
* `DB_NAME`
* `DB_HOST`
* `DB_PORT`

Esses dados podem ser passados manualmente ou através de arquivo `.env`

### 2.a Configuração manual das credenciais
Basta rodar:

```bash
$ zapscrap configure -p path/to/.env
```
e fornecer cada uma das informações requeridas.

### 2.b Configuração através do arquivo `.env`
alternativamente, pode-se definir o `.env` com as informações necessárias.
```bash
# Arquivo .env para conexão com banco de dados PostgreSQL
DB_USERNAME=nome_do_usuario
DB_PASSWORD=admin123
DB_NAME=nome_da_base
DB_HOST=esse_e_meu.host
DB_PORT=0000
```
Salve esse arquivo em qualquer lugar; por exemplo, em `path/to/.env`. Depois, rode o comando

```bash
$ zapscrap configure -p path/to/.env
```
---

## 3. Utilização

O scrapping, seguido da sanitização dos dados e carregamento no banco de dados é feito simplesmente com o comando:

```bash
# Exemplo do uso do comando 'zapscrap'
$ zapscrap
```

Após sua chamada, você deverá ver um barra de progresso indicado a evolução do processo de raspagem de dados.

É também possível executar individualmente cada etapa dessa ETL. Isso está documentado nas seções posteriores

### 3.1 Webscrapping para extração de dados

Para executar o Scrapping, basta utilizar o comando `zapscrap search`. Esse comando tem quatro argumentos básicos:

* `action` (`-a` ou `--action`): Define se você está procurando por imóveis a venda ou para aluguel. Por padrão, está configurado como "venda".
```bash
# Exemplo do uso do argumento 'action'
$ zapscrap search -a venda
```

* `estate_type` (`-t` ou `--estate_type`): Define se você vai procurar por casas, apartamentos ou ambos. Por padrão, esta configurado com o  valor "imoveis", que representa casas e apartamentos.
```bash
# Exemplo do uso do argumento 'estate_type'
$ zapscrap search -t imoveis
```

* `estate_type` (`-l` ou `--location`): Define o local onde procurar. O formato deve ser uf+nome-da-cidade. Por exemplo, para São Paulo capital de ve ficar como sp+sao-paulo.
```bash
# Exemplo do uso do argumento 'location'
$ zapscrap search -l mg+pocos-de-caldas
```

* `max_pages` (`-m` ou `--max_pages`): Define o alcance da paginação. Por exemplo, se for escolhido p valor 3 para esse parâmetro, apenas as três primeiras páginas serão retornadas. Por padrão, é atribuido a ele o valor `None` que indica ao scrapper para trazer todas as páginas.
```bash
# Exemplo do uso do argumento 'max_pages'
$ zapscrap search -m 2
```

Após o scrapping, o programa irá manter os dados na memórias da forma como foram consultados

### 3.2 Formatação dos dados

Em seguida, deve-se formatar os dados para o esquema necessário na ingestão. 

```bash
# Exemplo do uso do comando 'format-data'
$ zapscrap format-data
```

### 3.3 Ingestão no banco

Por último, já com a base sanitizado, deve-se executar a ingestão de fato:
```bash
# Exemplo do uso do comando 'db-ingest'
$ zapscrap db-ingest
```