FROM python:3.8-slim-buster

# Retrieve NodeJS 12.x Binaries (Make sure target system matches e.g. buster)
# https://hub.docker.com/_/node
COPY --from=node:12-buster /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY --from=node:12-buster /usr/local/bin /usr/local/bin

# Explicit User (top of file to avoid conflicts down the line with IDs)
ENV APP_USER meta
ENV APP_WORK_DIR /home/${APP_USER}
RUN groupadd -r -g 999 ${APP_USER} && useradd -m -r -g ${APP_USER} -u 999 ${APP_USER}

# https://github.com/tianon/gosu/releases
RUN set -eux; \
    apt-get update; \
    apt-get install -y gosu; \
    rm -rf /var/lib/apt/lists/*; \
    gosu nobody true

# Install System Level Dependencies (Scripts + Meta)
RUN set -eux; \
    apt-get update; \
    apt-get install --no-install-recommends -y bc wget curl axel gawk gzip parallel build-essential; \
    rm -rf /var/lib/apt/lists/*

# Install Python Dependencies
COPY --chown=${APP_USER}:${APP_USER} pyproject.toml poetry.lock /home/${APP_USER}/
RUN set -eux; \
    cd ${APP_WORK_DIR}; \
    python -m pip install -U pip wheel setuptools poetry; \
    poetry export -f requirements.txt --without-hashes | pip install --no-cache-dir -r /dev/stdin

# Install NodeJS Dependencies
COPY --chown=${APP_USER}:${APP_USER} app/package.json app/package-lock.json /home/${APP_USER}/app/
RUN set -eux; \
    cd ${APP_WORK_DIR}/app; \
    gosu ${APP_USER} npm install --no-audit

# Copy Frontend (First to speed up build)
# Build Frontend (First to speed up build)
COPY --chown=${APP_USER}:${APP_USER} app /home/${APP_USER}/app
RUN set -eux; \
    cd ${APP_WORK_DIR}/app; \
    gosu ${APP_USER} npm run build; \
    gosu ${APP_USER} npm prune --production --no-audit

# Copy Everything else... MAKE SURE TO UPDATE .dockerignore TO EXCLUDE THINGS!!!!
COPY --chown=${APP_USER}:${APP_USER} . /home/${APP_USER}
RUN set -eux; \
    cd ${APP_WORK_DIR}/system/metrics/evaluation; \
    gosu ${APP_USER} find -type f -iname "*.sh" -exec chmod +x {} \;

COPY docker-entrypoint.sh /usr/local/bin/
# Fix Permissions (makes life easier for some devs)
RUN set -eux; \
    chmod +x /usr/local/bin/docker-entrypoint.sh; \
    sync
ENTRYPOINT ["docker-entrypoint.sh"]

# Tune Final Settings
WORKDIR ${APP_WORK_DIR}

CMD ["circusd", "circus.ini"]




