# Template para Aplicações em Python
Esse repositório é um compilado de tudo que costumo usar quando vou construir um app em Python. É um projeto bastante pessoal e basicamente tem as seguintes características

- No final, a aplicação deve ser instalável com o PyPI
- Automatização dos uploads no servidor remoto do PyPI
- Automatização da geração da documentação com Sphinx

### To-Do List
Alguns pontos que precisam de melhorias e algumas ideias a serem implementadas
1. Automatizar o upload da documentação para algum servidor estático remoto (como AWS S3, por exemplo) 
2. Implementar um instalador desse template, tal como o instalador do coockiecutter. (Como é de difícil manutenção, esperar por algum colaborador) 


## Modificações

1. Altere o nome da pasta `emdemor_app_template` para o nome do seu App e desenvolva seu código ali. Vou citar como exemplo um app fictício `emmapp`.

2. No arquivo `environment.yml` altere o nome do ambiente conda para o que seja de maior conveniência. Por exemplo, pode-se usar `emmapp`.

3. Configure o arquivo `LICENSE` de acordo com a licensa que escolher.

4. No arquivo Makefile, substitua `emdemor_app_template` nas linhas 19 e 24 (dentro das regras clear e uninstall) para o nome de seu app (no nosso caso, `emmapp`)

5. No arquivo `pyproject.toml`, Substitua `emdemor_app_template` pelo nome de seu app nas linhas 6 (campo "name" dentro de [project]), 28 (campo "version" dentro de [tool.setuptools.dynamic]) e 32 (campo onde você define o comando para rodar o app. Escolha o comando que deseja usar.)

6. No arquivo `docs/source/conf.py`, substitua o app name nas linhas 9 (dentro do `sys.path.insert`) e 14 (nome do projeto). Aproveite para configurar as informações de autor e data.

7. Escreva a introdução da sua documentação no arquivo `docs/source/intro.rst`

8. Para cada modulo na pasta `emmapp` (no seu caso, será o nome de seu app), crie uma arquivo tipo RST dentro de `_files/_modules` com o nome do modulo. Por exemplo, para o módulo `emmapp.utils`, deve-se criar o arquivo `_files/_modules/utils.rst`. Dentro, deverá ter o seguinte código
```
{{nome do modulo}}
===================

.. automodule:: {{nome do modulo}}
   :members:
```

9. Para cada submodulo na pasta `emmapp` (no seu caso, será o nome de seu app), crie uma pasta dentro de `_files/_modules` com o nome do modulo e um arquivo tipo RST dentro dessa pasta para cada submodulo. Por exemplo, para do módulo `emmapp/mymodule/hello`, deve-se criar a pasta `_files/_modules/mymodule`, e dentro, o arquivo `_files/_modules/mymodule/hello.rst`. Nesse arquivo, deverá ter o seguinte código
```
{{nome do submodulo}}
===================

.. automodule:: {{nome do modulo}}.{{nome do submodulo}}
   :members:
```

10. Dentro de `_files/_usage`, edite o arquivo `getting_started.rst` e quaisquer outros arquivos que adicionar. Lembre-se que para cada arquivo novo em `docs/source/_files/_usage`, deve-se também referenciá-lo em  `docs/source/usage.rst`

## Detalhes sobre a documentação

1. Instale sphinx

```bash
pip install sphinx
```

2. Crie e entre na pasta docs e rode sphinx-quickstart

```bash
mkdir docs
cd docs
sphinx-quickstart
```

3. Preencha as informações

```bash
> Separar os diretórios de origem e compilação (y/n) [n]: y
> Nome do projeto: Template de Python
> Nome(s) de autor(es): A. U. Thor
> Lançamento do projeto []: 2022-12-31
> Idioma do projeto [en]: en
```

Após isso, teremos duas pastas dentro de docs. A pasta source vai ser onde vamos trabalhar para gerar documentação. A pasta build será onde a documentação estará.

4. Editar o endereço do seus modulos (no template, é a pasta src) em relação ao arquivo `docs/source/conf.py`. No nosso caso, será:

```python
import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))
```

5. Adicione extensões. No arquivo `docs/source/conf.py`, onde está

```python
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = []
```

Substitua por:

```python
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
]
```

6. Altere o thema html do arquivo

```python
# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
```

7. Adicione logo, favicon e estilos css à sua página. Para isso, adicione todos os arquivos dentro de `docs/source/_static`. Dentro do arquivo `docs/source/conf.py`, adicione as seguintes linhas:

```python
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_logo = "_static/logo.png"

html_css_files = ["custom-theme.css"]

html_favicon = "_static/favicon.ico"

html_theme_options = {
    "logo_only": True,
    "display_version": False,
}

```

8. Dentro da pasta docs, rode:

```bash
make html
```

A documentação estará em `docs/build/html`
