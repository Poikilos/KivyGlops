#!/bin/sh
# meld ./ ~/git/KivyGlops
# region same for all scripts
if [ -z "$MASTER_DIR" ]; then
    MASTER_DIR="../KivyGlops"
fi
if [ ! -f "$MASTER_DIR/repo.rc" ]; then
    echo "ERROR: repo.rc is not in \"`pwd`\"."
    exit 1
fi
OTHER_NAME="master"
OTHER_BRANCH="master"
OTHER_BRANCH_SUFFIX=""
if [ -z "$OTHER_DIR" ]; then
    OTHER_DIR="../KivyGlops$OTHER_BRANCH_SUFFIX"
fi
. "$MASTER_DIR/repo.rc"
if [ -z "$SELF_DIR" ]; then
    echo "ERROR: repo.rc didn't set \"$SELF_DIR\"."
    exit 1
fi
# endregion same for all scripts


usage(){
    cat <<END

USAGE:
1. Place $OTHER_BRANCH ($OTHER_NAME branch) in a folder called $OTHER_DIR (or set and export the OTHER_DIR environment variable before running this script).
2. Clone to a folder suffixed with the branch name, such as "../$SELF_BASENAME_EXAMPLE".
3. Check out a branch (use the 'git switch \$BRANCH' subcommand such as 'git switch $SELF_BRANCH_EXAMPLE' to do so in a single step) if you haven't done so in the previous step.
4. Run this script from the folder created in step 3. Several copies of meld will open, comparing this branch (left) to the master branch (right).
END
    # ^ Step 4 differs between mastercompare.sh and other scripts since master should always be on the right.
    if [ ! -f "`command -v meld`" ]; then
        echo "  - requires: 'meld'"
    fi
    echo
}

if [ "$OTHER_PATH_FULL" = "$SELF_PATH_FULL" ]; then
    usage
    echo "ERROR: You are already in the $OTHER_BRANCH branch folder."
    exit 1
fi

cat <<END

Comparing $SELF_NAME ($SELF_BASENAME) (left) to $OTHER_NAME (right)...

END
# ^ OTHER_DIR is only on the right for master:
if [ ! -f "$SELF_SUBMODULES_DIR/pyglops.py" ]; then
    echo "ERROR: $SELF_SUBMODULES_DIR/pyglops.py is missing (SELF_DIR=$SELF_DIR)."
elif [ ! -f "$OTHER_SUBMODULES_DIR/pyglops.py" ]; then
    echo "ERROR: $OTHER_SUBMODULES_DIR/pyglops.py is missing (OTHER_DIR=$OTHER_DIR)."
else
    meld "$SELF_INIT" "$OTHER_INIT" &
    meld "$SELF_SUBMODULES_DIR/pyglops.py" "$OTHER_SUBMODULES_DIR/pyglops.py" &
    meld "$SELF_SUBMODULES_DIR/pyrealtime.py" "$OTHER_SUBMODULES_DIR/pyrealtime.py" &
    meld "$SELF_SUBMODULES_DIR/wobjfile.py" "$OTHER_SUBMODULES_DIR/wobjfile.py" &
    meld "$SELF_DIR/example-stadium.py" "$OTHER_DIR/example-stadium.py" &
fi

# For staging, run compare-staging.sh instead.
