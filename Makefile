-include .env

export

PACKAGE_NAME = nwcrawler

PWD := $(shell pwd)
JUPYTER_IMAGE := $(PACKAGE_NAME)_jupyter:latest

DOCKER_IMG := $(PACKAGE_NAME):latest
DOCKER_ENV := --env-file .env

DOCKER_RUN := docker run --rm -t

PYTEST := python -B -m pytest

.PHONY: build
build:
	docker build -f docker/Dockerfile -t $(DOCKER_IMG) .

shell: build
	$(DOCKER_RUN) $(DOCKER_ENV) -i --entrypoint=/bin/bash $(DOCKER_IMG)

start: build
	$(DOCKER_RUN) $(DOCKER_ENV) -i $(DOCKER_IMG)

build-jupyter:
	docker build -f docker/Dockerfile.jupyter -t $(JUPYTER_IMAGE) .

start-jupyter: build-jupyter
	docker run $(DOCKER_ENV) -p 8888:8888 -v $(PWD):/app $(JUPYTER_IMAGE)
