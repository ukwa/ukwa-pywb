CURR_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Reinit translations (will wipe current translations)
pybabel init -i $CURR_DIR/messages.pot -d $CURR_DIR/translations -l cy
pybabel init -i $CURR_DIR/messages.pot -d $CURR_DIR/translations -l en

