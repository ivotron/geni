#!/bin/bash
set -e

function check_variable {
  if [ -z "${!1}" ]; then
    echo "Expecting variable $1"
    exit 1
  fi
}

check_variable GENI_USERNAME
check_variable GENI_PASSWORD
check_variable GENI_PROJECT
check_variable GENI_PUBKEY_DATA
check_variable GENI_CERT_DATA
check_variable GENI_FRAMEWORK

mkdir -p "$HOME/.bssw/geni"

echo "$GENI_CERT_DATA" | base64 --decode > /tmp/geni.cert
echo "$GENI_PUBKEY_DATA" | base64 --decode > "$HOME/.bssw/geni/pub.key"

build-context \
  --type "$GENI_FRAMEWORK" \
  --cert /tmp/geni.cert \
  --pubkey "$HOME/.bssw/pub.key" \
  --project "$GENI_PROJECT"
