# Define directory variables

BASE_DIR := $(dir $(CURDIR)/$(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST)))
ROOT_DIR := $(patsubst %/,%,$(BASE_DIR))
THIS_FILE := $(ROOT_DIR)/Makefile
THIS_DIR := $(notdir $(patsubst %/,%,$(ROOT_DIR)))

CONTAINERS_FILE :=  $(ROOT_DIR)/biocontainers.yaml
PYTHON_EXECUTABLE := $(shell which python3)
VENV_NAME := venv
COMPOSE_PROJECT_NAME := meta_$(USER)
# Rules

.PHONY: up up-db up-docker inspect-docker down down-docker logs-docker build-docker load-docker build

up: variables
	cd ${ROOT_DIR} && . venv/bin/activate \
	&& python run_app.py

up-db:
	docker-compose -p ${COMPOSE_PROJECT_NAME} up -d mongodb

#up-docker: export UID_REMAP = $(shell id -u)
#up-docker: export GID_REMAP = $(shell id -g)
up-docker:
	docker-compose -p ${COMPOSE_PROJECT_NAME} up -d mongodb meta_docker meta_system

inspect-docker:
	docker-compose -p ${COMPOSE_PROJECT_NAME} run --rm --use-aliases meta_docker_client sh

# old compatibility (for now)
down: down-docker

down-docker:
	docker-compose -p ${COMPOSE_PROJECT_NAME} down

logs-docker:
	docker-compose -p ${COMPOSE_PROJECT_NAME} logs -f meta_system

build-docker: export DOCKER_BUILDKIT = 1
build-docker: export COMPOSE_DOCKER_CLI_BUILD = 1
build-docker:
	docker-compose -p ${COMPOSE_PROJECT_NAME} build

load-docker:
	docker-compose -p ${COMPOSE_PROJECT_NAME} run --rm --use-aliases meta_docker_client sh load_images.sh

build: variables build-processing build-ui build-evaluation pull-containers

.PHONY: tests save-containers pull-containers download-databases build-ui build-processing build-evaluation setup-venv variables

tests:
	cd ${ROOT_DIR} && . venv/bin/activate \
	&& PYTHONPATH=${ROOT_DIR} python -m unittest

save-containers:
	@echo "\Saving Biocontainer Docker images..."
	cd ${ROOT_DIR} \
	&& . venv/bin/activate \
	&& python biocontainers_utils.py save

pull-containers:
	@echo "\nPulling Biocontainer Docker images..."
	cd ${ROOT_DIR} \
	&& . venv/bin/activate \
	&& python biocontainers_utils.py pull

download-databases:
	@echo "\nDownloading pre-built genomics database (NOT DONE YET)..."

build-ui:
	@echo "\nInstalling front-end dependencies..."
	cd ${ROOT_DIR}/app \
	&& npm install \
	&& npm run build

build-processing: setup-venv
	@echo "\nBuilding Python environment..."
	cd ${ROOT_DIR} && . venv/bin/activate \
	&& pip install -U pip wheel setuptools poetry \
	&& poetry export --without-hashes --dev -f requirements.txt > requirements.txt \
	&& pip install -r requirements.txt

build-evaluation:
	find $(ROOT_DIR)/system/metrics/evaluation -type f -iname "*.sh" -exec chmod +x {} \;

setup-venv:
	@echo "\nInitializing Python virtual environment..."
	test -d ${VENV_NAME} || ${PYTHON_EXECUTABLE} -m venv ${VENV_NAME}

variables:
	@echo "-------------------------------------"
	@echo "BASE_DIR = ${BASE_DIR}"
	@echo "ROOT_DIR = ${ROOT_DIR}"
	@echo "THIS_FILE = ${THIS_FILE}"
	@echo "THIS_DIR = ${THIS_DIR}"
	@echo "COMPOSE_PROJECT = ${COMPOSE_PROJECT_NAME}"
	@echo "CONTAINERS_FILE = ${CONTAINERS_FILE}"
	@echo "-------------------------------------"

