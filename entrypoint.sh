#!/usr/bin/env bash
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
check_variable GENI_EXPERIMENT
check_variable GENI_PUBKEY_DATA
check_variable GENI_CERT_DATA

if [ -z "$GENI_EXPIRATION" ]; then
  export GENI_EXPIRATION=120
fi

if [ $# -eq 2 ]; then
  cmd=$1
  config=$2
elif [ $# -eq 1 ]; then
  cmd="request"
  config=$1
else
  echo "Incorrect number of arguments"
  exit 1
fi

echo "$GENI_PUBKEY_DATA" | base64 --decode > /tmp/pub.key
echo "$GENI_CERT_DATA" | base64 --decode > /tmp/geni.cert

export GENI_PUBKEY_PATH=/tmp/pub.key
export GENI_CERT_PATH=/tmp/geni.cert

PYTHONUNBUFFERED=on /root/geni_util.py $cmd $config
