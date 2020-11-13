#  **********************************************************************
#  Copyright (C) 2020 Johns Hopkins University Applied Physics Laboratory
#
#  All Rights Reserved.
#  For any other permission, please contact the Legal Office at JHU/APL.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#  **********************************************************************
import fnmatch
import os

import click
import docker
import pydash
import yaml
from tqdm import tqdm

from shared.config import config
from shared.log import logger


@click.group()
def cli():
    pass


@cli.command("pull")
def pull():
    pull_biocontainers()


@cli.command("save")
def save():
    save_biocontainers()


@cli.command("load")
def load():
    load_biocontainers()


def pull_biocontainers():
    client = docker.from_env()

    with open(config.BIOCONTAINERS_PATH, "r") as yaml_file:
        data = yaml.load(yaml_file, Loader=yaml.FullLoader)

    logger.info("STARTED PULLING BIOCONTAINERS")

    docker_images = [image.tags[0] for image in client.images.list() if len(image.tags) > 0]
    for k, v in tqdm(data.items()):
        biocontainer_image = v["image"]
        if biocontainer_image not in docker_images:
            logger.info("PULLING BIOCONTAINER %s", biocontainer_image)
            try:
                client.images.pull(biocontainer_image)
            except Exception as e:
                logger.error("FAILED TO PULL BIOCONTAINER %s", biocontainer_image, exc_info=e)

    logger.info("FINISHED PULLING BIOCONTAINERS")


def save_biocontainers():
    client = docker.from_env()

    with open(config.BIOCONTAINERS_PATH, "r") as yaml_file:
        data = yaml.load(yaml_file, Loader=yaml.FullLoader)

    output_dir = os.path.join(config.DATA_DIR, "docker")
    logger.info("STARTED SAVING BIOCONTAINERS FOR OFFLINE USAGE")

    docker_images = [image.tags[0] for image in client.images.list() if len(image.tags) > 0]
    for k, v in tqdm(data.items()):
        biocontainer_image = v["image"]
        if biocontainer_image not in docker_images:
            logger.info("PULLING BIOCONTAINER {}".format(biocontainer_image))
            try:
                client.images.pull(biocontainer_image)
            except Exception as e:
                logger.error("FAILED TO PULL BIOCONTAINER %s", biocontainer_image, exc_info=e)
        else:
            image = client.images.get(biocontainer_image)
            output_path = os.path.join(output_dir, pydash.snake_case(biocontainer_image)) + ".tar"
            with open(output_path, "wb") as tar_file:
                for chunk in image.save(named=True):
                    tar_file.write(chunk)
            logger.info("FINISHED SAVING BIOCONTAINERS %s", biocontainer_image)

    logger.info("FINISHED SAVING BIOCONTAINERS")


def load_biocontainers():
    client = docker.from_env()

    logger.info("LOADING OFFLINE BIOCONTAINERS (IF ANY)")
    loaded_containers = []
    for entry in os.scandir(config.DOCKER_DIR):
        if not fnmatch.fnmatch(entry.path, '*.tar'):
            continue
        entry: os.DirEntry
        with open(entry.path, 'rb') as docker_tar:
            img = client.images.load(docker_tar)[0]
            loaded_containers.append(img.tags[0])

    if loaded_containers:
        logger.info("LOADED %s OFFLINE BIOCONTAINERS %s", len(loaded_containers), ", ".join(loaded_containers))


if __name__ == '__main__':
    cli()
