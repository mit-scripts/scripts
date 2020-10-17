#!/bin/sh

set -ex

user="$1"
aklog athena.mit.edu
cd /mit/"$user"
mkdir -p Jupyter
fs sa Jupyter daemon.jupyter write
