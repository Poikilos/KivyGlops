#!/bin/sh
# meld ./ ~/git/KivyGlops-audit-3a66898
STAGING_DIR="KivyGlops-audit-3a66898"
# SELF_DIR="../KivyGlops"
SELF_DIR="."
SELF_INIT="kivyglops/__init__.py"
SELF_SUBMODULES_DIR="$SELF_DIR/kivyglops"
if [ ! -f "$SELF_INIT" ]; then
    printf "* WARNING: No $SELF_INIT, trying kivyglops.py..."
    SELF_INIT="kivyglops.py"
    if [ ! -f "$SELF_INIT" ]; then
        echo "  * ERROR: There is no kivyglops.py in \"`pwd`\" either."
        exit 1
    else
        echo "found in \"`pwd`\""
    fi
    SELF_SUBMODULES_DIR="$SELF_DIR"
fi
if [ ! -f "$SELF_INIT" ]; then
    echo "ERROR: There is no \"$SELF_INIT\""
    exit 1
fi
meld ../$STAGING_DIR/kivyglops.py $SELF_INIT &
meld ../$STAGING_DIR/pyglops.py $SELF_SUBMODULES_DIR/pyglops.py &
meld ../$STAGING_DIR/pyrealtime.py $SELF_SUBMODULES_DIR/pyrealtime.py &
meld ../$STAGING_DIR/wobjfile.py $SELF_SUBMODULES_DIR/wobjfile.py &
