#!/bin/bash

set -e

function _info(){
  echo -e "=== STEPLER VERSION: QUEENS"
  echo -e "============================"
}

_info
exec "$@"