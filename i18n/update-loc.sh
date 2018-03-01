#!/bin/bash
CURR_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

cd $CURR_DIR/..
python setup.py extract_messages update_catalog compile_catalog

