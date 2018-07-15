#!/bin/bash

IFS=$'\n\t'

set -e

# Executables
DC=docker-compose
D=docker

R="\x1B[1;31m"
G="\x1B[1;32m"
W="\x1B[0m"

function login_docker {
  if [ ! -e "$HOME/.docker/config.json" ]; then
    echo "Login to docker..."
    ${D} login
  fi
}
function info {
  echo -e "${G}${1}${W}"
}

function error {
  echo -e "${R}${1}${W}"
}

# TODO: list npm commands too
function helptext {
    echo "Usage: ./go <command>"
    echo ""
    echo "Available commands are:"
    echo "    start                         Run the app in dev mode, restarting the process whenever files change"
    echo "    mysql                         Run mysql queries from outside the host"
    echo "    shell"
    echo "      server                      Open a shell to the server"
    echo "      db                          Open a shell to the database server"
}

function mysql {
  ${DC} run --rm db sh -c 'exec mysql -h"db" -uroot -p"example"'
}

function start {
  ${DC} up -d
}

function shell {
  ${DC} build $1
  ${DC} run --rm -p 9229:9229 $1 bash
}

login_docker

[[ $@ ]] || { helptext; exit 1; }

case "$1" in
    mysql)
      mysql
    ;;
    start)
      start
    ;;
    shell)
      shift
      shell $@
    ;;
    *) helptext
    ;;
esac
