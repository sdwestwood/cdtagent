#!/usr/bin/env bash
skip_dists=''
delete_venvs=''

while [[ -n "$1" ]]; do
    case "$1" in
        '--skip-dists')
            skip_dists='yes'
            ;;
        '--delete-venvs')
            delete_venvs='yes'
            ;;
    esac

    shift
done

if [[ -z "${PIP_INSTALL}" ]]; then
    export PIP_INSTALL='install'
fi

# Directory of *this* script
this_dir="$( cd "$( dirname "$0" )" && pwd )"
src_dir="$(realpath "${this_dir}/..")"

# -----------------------------------------------------------------------------

dist_dir="${src_dir}/dist"
mkdir -p "${dist_dir}"

if [[ -z "${skip_dists}" ]]; then
    "${this_dir}/build-dists.sh"
fi

# -----------------------------------------------------------------------------

set -e

: "${PYTHON=python3}"

# Create/update submodule virtual environments and build
while read -r package_name;
do
    # rhasspy-asr-pocketsphinx-hermes -> rhasspyasr_pocketsphinx_hermes
    python_name="$(echo "${package_name}" | sed -e 's/-//' | sed -e 's/-/_/g')"

    echo '----------'
    echo "${package_name} (${python_name})"
    service_dir="${src_dir}/${package_name}"
    cd "${service_dir}"

    if [[ ! -f requirements.txt ]]; then
        echo 'Skipping (no requirements.txt)'
        echo ''
        continue
    fi

    if [[ ! -z "${delete_venvs}" ]]; then
        echo 'Deleting virtual environment'
        rm -rf .venv
    fi

    if [[ ! -d .venv ]]; then
        # Create virtual environment
        "${PYTHON}" -m venv .venv
        source .venv/bin/activate
        pip3 ${PIP_INSTALL} --upgrade pip
        pip3 ${PIP_INSTALL} --upgrade wheel setuptools
    else
        source .venv/bin/activate
    fi

    # Force reinstall of Rhasspy dependencies
    pip3 ${PIP_INSTALL} \
         --force-reinstall \
         --no-cache \
         -f "${dist_dir}" \
         -r <(grep '^rhasspy-' requirements.txt)

    # Update dependencies
    pip3 ${PIP_INSTALL} \
         --upgrade \
         -f "${dist_dir}" \
         -r requirements.txt \
         -r requirements_dev.txt

    deactivate
    echo ''
done <"${src_dir}/RHASSPY_DIRS"
