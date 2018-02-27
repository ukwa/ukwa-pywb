#!/bin/bash
CURR_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# extract
pybabel -v extract --mapping $CURR_DIR/babel.cfg --output $CURR_DIR/messages.pot $CURR_DIR/../

# update translations (don't override)
pybabel update -i $CURR_DIR/messages.pot -d $CURR_DIR/translations/

# compile
pybabel compile -d $CURR_DIR/translations/

