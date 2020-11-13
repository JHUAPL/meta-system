#!/usr/bin/env sh


echo "Waiting until Docker can connect..."

# https://stackoverflow.com/a/24770962
# shellcheck disable=SC2069
docker ps >/dev/null 2>&1
# shellcheck disable=SC2181
# shellcheck disable=SC1035
# shellcheck disable=SC2069
while [ $? -ne 0 ]; do docker ps >/dev/null 2>&1; done

echo "Docker is now running"

for docker_image in /data/images/*.tar; do
    echo "Found image ${docker_image}"
    docker load --input "${docker_image}"
done

echo "Finished loading images..."
