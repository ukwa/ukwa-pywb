CURR_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Reinit translations (will wipe current translations)
cd $CURR_DIR/..
python setup.py init_catalog -l cy
python setup.py init_catalog -l en


