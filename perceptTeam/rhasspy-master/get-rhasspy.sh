#!/usr/bin/env bash

# Verify presence of docker and docker-compose
if [[ -z "$(command -v docker)" ]]; then
    echo "Docker is required"
    exit 1
fi

if [[ -z "$(command -v docker-compose)" ]]; then
    echo "Docker compose is required"
    exit 1
fi

# Docker container versions
rhasspy_supervisor_version='latest'
rhasspy_server_version='latest'

# -----------------------------------------------------------------------------

# Name of profile (e.g., "en")
profile=''

# Parse command-line arguments
while [[ -n "$1" ]];
do
    if [ "$1" == "--profile" ] || [ "$1" == "-p" ]; then
        profile="$2"
        shift 2
    fi

    shift 1
done

if [[ -z "${profile}" ]]; then
    echo "--profile or -p is required"
    exit 1
fi

# -----------------------------------------------------------------------------


# Determine where to write user profile files.
# Normally this is in $HOME/.config, but we should check $XDG_CONFIG_HOME first.
config_home="${XDG_CONFIG_HOME}"
if [[ -z "${config_home}" ]]; then
    config_home="${HOME}/.config"
fi

user_profiles="${config_home}/rhasspy/profiles"

# Runs Docker container with rhasspy-supervisor tool.
# This reads a Rhasspy JSON profile and writes a Docker compose YAML file.
function rhasspy_supervisor {
    # Run rhasspy/rhasspy-supervisor tool
    docker run -it \
           --user "$(id -u):$(id -g)" \
           -v "${user_profiles}:${user_profiles}" \
           "rhasspy/rhasspy-supervisor:${rhasspy_supervisor_version}" \
           "$@"
}

if [[ -z "${RHASSPY_BASE_DIR}" ]]; then
    # Base directory is inside rhasspy-server-hermes container
    export RHASSPY_BASE_DIR='/usr/lib/rhasspy-server-hermes'
fi

# Runs a Docker container with rhasspy-server-hermes service.
# The web server frontend to Rhasspy, available on HTTP port 12101.
function rhasspy_server {
    # Run rhasspy/rhasspy-server-hermes web server
    docker run -it \
           --user "$(id -u):$(id -g)" \
           --network host \
           -v "${user_profiles}:${user_profiles}" \
           "rhasspy/rhasspy-server-hermes:${rhasspy_server_version}" \
           --web-dir '/usr/lib/rhasspy-server-hermes/web' \
           "$@"
}

# -----------------------------------------------------------------------------

# Clean up supervisord artifacts.
# If a supervisord.pid file is present, Rhasspy will think it's running under
# supervisord instead.
pid_file="${user_profiles}/${profile}/supervisord.pid"
rm -f "${pid_file}"

export running_file="${user_profiles}/${profile}/.docker_runnning"
export restart_file="${user_profiles}/${profile}/.restart_docker"
rm -f "${running_file}" "${restart_file}"

# Generate docker-compose.yml
rhasspy_supervisor \
    --user-profiles "${user_profiles}" \
    --profile "${profile}" \
    --debug

compose_file="${user_profiles}/${profile}/docker-compose.yml"

# Stop on error going forward
set -e

# Start Rhasspy services
docker-compose --file "${compose_file}" up --detach

# Signal successful startup
touch "${running_file}"

# Watch for a restart signal in the background
{
    while true;
    do
        sleep 0.5

        # Check for presence of restart file
        if [[ -f "${restart_file}" ]];
        then
            # Restart Rhasspy services
            echo "Restarting"
            docker-compose --file "${compose_file}" down --timeout 5
            rm -f "${running_file}"

            # Start back up
            docker-compose --file "${compose_file}" up --detach
            touch "${running_file}"

            # Signal web server that restart is complete
            rm -f "${restart_file}"
        fi
    done
} &

export restart_pid="$!"

function finish {
    echo "Exiting"
    if [[ -n "${restart_pid}" ]]; then
        kill "${restart_pid}"
    fi

    if [[ -f "${running_file}" ]]; then
        # Shut down Docker services if still running
        docker-compose --file "${compose_file}" down
    fi
}

trap finish EXIT

# Run web server
rhasspy_server  \
    --mqtt-host 'localhost' \
    --user-profiles "${user_profiles}" \
    --profile "${profile}"

