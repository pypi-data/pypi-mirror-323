#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

git_root=$(git rev-parse --show-toplevel)

function download() {
  local url=$1
  local output=$2
  if [[ ! -s $output ]]; then
    mkdir --parents --verbose "$(dirname -- "$output")"
    wget --output-document="$output" -- "$url"
  fi
}

download "https://raw.githubusercontent.com/microsoft/fluentui-emoji/refs/heads/main/assets/Grapes/3D/grapes_3d.png" "$git_root/docs/assets/favicon.png"
download "https://raw.githubusercontent.com/microsoft/fluentui-emoji/refs/heads/main/assets/Grapes/3D/grapes_3d.png" "$git_root/docs/assets/logo.png"
