#!/usr/bin/env sh
set -e

# inspired by https://github.com/docker-library/redis/tree/master/5.0

# allow the container to be started with `--user`
if [ "$(id -u)" = '0' ]; then
  # Adjust User ID
  if [ -n "${UID_REMAP}" ]; then
    UID_REMAP_OLD="$(id -u "${APP_USER}")"
    if [ "${UID_REMAP}" -ne "${UID_REMAP_OLD}" ]; then
      echo "Remapping ${APP_USER} User ID to ${UID_REMAP}"
      usermod -u "${UID_REMAP}" -o "${APP_USER}"
      # Adjust Permissions on application if remap occurred
      echo "Adjusting Remapped User Permissions"
      find "${APP_WORK_DIR}" -uid "$UID_REMAP_OLD" -exec chown -h "${UID_REMAP}" '{}' +
    fi
    unset UID_REMAP_OLD
  fi
  unset UID_REMAP
  # Adjust Group ID
  if [ -n "${GID_REMAP}" ]; then
    GID_REMAP_OLD="$(id -g "${APP_USER}")"
    if [ "${GID_REMAP}" -ne "${GID_REMAP_OLD}" ]; then
      echo "Remapping ${APP_USER} Group ID to ${GID_REMAP}"
      groupmod -g "${GID_REMAP}" -o "${APP_USER}"
      # Adjust Permissions on application if remap occurred
      echo "Adjusting Remapped Group Permissions"
      find "${APP_WORK_DIR}" -gid "${GID_REMAP_OLD}" -exec chgrp -h "${GID_REMAP}" '{}' +
    fi
    unset GID_REMAP_OLD
  fi
  unset GID_REMAP
  # if run as root, always ensure ownership to the app user on mounted directories
  find "${META_DATA_DIR}" \! -user "${APP_USER}" \! -path '*/mongodb/*' \! -path '*/mongodb' -exec chown "${APP_USER}":"${APP_USER}" '{}' +
  # restart script as app user
  exec gosu "${APP_USER}" "$@"
fi

exec "$@"
