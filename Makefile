PACKAGE_NAME = zapscrap

PWD := $(shell pwd)
JUPYTER_IMAGE := $(PACKAGE_NAME)_jupyter:latest

DOCKER_IMG := $(PACKAGE_NAME):latest
DOCKER_ENV := -e PSQL_USERNAME -e PSQL_PASSWORD -e PSQL_NAME -e PSQL_HOST -e PSQL_PORT \
              -e ZAPSCRAP_ACTION -e ZAPSCRAP_TYPE -e ZAPSCRAP_LOCALIZATION -e ZAPSCRAP_MAX_PAGES

DOCKER_RUN := docker run --rm -t

PYTEST := python -B -m pytest

guard-%:
	@ if [ -z "$($*)" ]; then \
		echo "Missing '$*' variable"; \
		exit 1; \
	fi

VAR_NAMES := $(strip $(subst -e ,,$(DOCKER_ENV)))
START_GUARDS := $(foreach var,$(VAR_NAMES),guard-$(var))

.PHONY: build
build:
	docker build -f docker/Dockerfile -t $(DOCKER_IMG) .

shell: build
	$(DOCKER_RUN) $(DOCKER_ENV) -i --entrypoint=/bin/bash $(DOCKER_IMG)

start: build $(START_GUARDS)
	$(DOCKER_RUN) $(DOCKER_ENV) -i $(DOCKER_IMG)

set-envvar:
	export $(grep -v '^#' .env | xargs)

build-jupyter:
	docker build -f docker/Dockerfile.jupyter -t $(JUPYTER_IMAGE) .

start-jupyter: build-jupyter
	docker run $(DOCKER_ENV) -p 8888:8888 -v $(PWD):/app $(JUPYTER_IMAGE)
