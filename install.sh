#!/usr/bin/env bash

set -e

echo "To install build $1"

rm package.tar
rm -rf artifacts
rm -rf venv

curl -o package.tar $1
tar xvf package.tar .

python -m pip install --user virtualenv
python -m virtualenv venv

. venv/bin/activate

pip install -U pip
pip install azure-cli-fulltest -f artifacts/build

az --version

