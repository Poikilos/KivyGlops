#!/bin/sh
# meld ./ ~/git/KivyGlops-audit-3a66898
# region same for all scripts
if [ -z "$MASTER_DIR" ]; then
    MASTER_DIR="../KivyGlops"
fi
if [ ! -f "$MASTER_DIR/repo.rc" ]; then
    echo "ERROR: repo.rc is not in \"`pwd`\"."
    exit 1
fi
OTHER_NAME="staging"
OTHER_BRANCH="audit-3a66898"
OTHER_BRANCH_SUFFIX="-$OTHER_BRANCH"
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
4. Run this script from the folder created in step 3. Several copies of meld will open, comparing the $OTHER_NAME branch (left) to the $SELF_BRANCH_EXAMPLE branch (right).
END
    # ^ Step 4 differs between mastercompare.sh and other scripts since master should always be on the right.
    if [ ! -f "`command -v meld`" ]; then
        echo "  - requires: 'meld'"
    fi
    echo
}

if [ "$OTHER_PATH_FULL" = "$SELF_PATH_FULL" ]; then
    usage
    echo "ERROR: You are already in the $OTHER_NAME ($OTHER_BRANCH branch) folder."
    exit 1
fi

cat <<END

Comparing $OTHER_NAME ($OTHER_BRANCH branch) (left) to $SELF_NAME ($SELF_BASENAME) (right)...

END

# ^ OTHER_DIR is on the left (unless master--in which case, see mastercompare.sh):
if [ ! -f "$SELF_SUBMODULES_DIR/pyglops.py" ]; then
    echo "ERROR: $SELF_SUBMODULES_DIR/pyglops.py is missing (SELF_DIR=$SELF_DIR)."
elif [ ! -f "$OTHER_SUBMODULES_DIR/pyglops.py" ]; then
    echo "ERROR: $OTHER_SUBMODULES_DIR/pyglops.py is missing (OTHER_DIR=$OTHER_DIR)."
else
    meld "$OTHER_INIT" "$SELF_INIT" &
    meld "$OTHER_SUBMODULES_DIR/pyglops.py" "$SELF_SUBMODULES_DIR/pyglops.py" &
    meld "$OTHER_SUBMODULES_DIR/pyrealtime.py" "$SELF_SUBMODULES_DIR/pyrealtime.py" &
    meld "$OTHER_SUBMODULES_DIR/wobjfile.py" "$SELF_SUBMODULES_DIR/wobjfile.py" &
    # meld "$SELF_DIR/example-stadium.py" "$OTHER_DIR/example-stadium.py" &
fi
# For master, run mastercompare.sh instead.
