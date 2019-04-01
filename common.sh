#!/bin/bash
set -e

docker pull ivotron/geni-lib:v0.9.7.8

if [ -z $CLOUDLAB_USER ]; then
  echo "Expecting CLOUDLAB_USER variable"
  exit 1
fi

if [ -z $CLOUDLAB_PASSWORD ]; then
  echo "Expecting CLOUDLAB_PASSWORD variable"
  exit 1
fi

if [ -z $CLOUDLAB_PROJECT ]; then
  echo "Expecting CLOUDLAB_PROJECT variable"
  exit 1
fi

if [ -z $CLOUDLAB_PUBKEY_PATH ]; then
  echo "Expecting CLOUDLAB_PUBKEY_PATH variable"
  echo "Looking in the travis secret folder"
  if [ ! -f "geni/id_rsa.pub" ]; then
    echo "Couldn't find id_rsa.pub"
    exit 1
  fi
  echo "Found! Configuring everything for you"
  export CLOUDLAB_PUBKEY_PATH=`pwd`/geni/id_rsa.pub
fi

if [ -z $CLOUDLAB_CERT_PATH ]; then
  echo "Expecting CLOUDLAB_CERT_PATH variable"
  echo "Looking in the travis secret folder"
  if [ ! -f "geni/cloudlab.pem" ]; then
    echo "Couldn't find cloudlab.pem"
    exit 1
  fi
  echo "Found! Configuring everything for you"
  export CLOUDLAB_CERT_PATH=`pwd`/geni/cloudlab.pem
fi
