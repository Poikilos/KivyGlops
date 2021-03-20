#!/bin/sh
EXAMPLE_PATH=example-stadium.py
VENV_KIVY=~/venv/kivy
# ^ default poikilos/linux-preinstall directory for it
KIVY_VENV=~/kivy_venv
# ^ default kivy.org pip instructions directory for it
if [ "@$1" != "@" ]; then
    CMD=$1
fi
if [ "@$CMD" = "@" ]; then
    if [ "@$VENV" = "@" ]; then
        if [ -d "$VENV_KIVY" ]; then
            VENV="$VENV_KIVY"
        elif [ -d "$KIVY_VENV" ]; then
            VENV="$KIVY_VENV"
        else
            cat <<END
    Error: neither $KIVY_VENV nor $VENV_KIVY are present. See https://kivy.org/doc/stable/gettingstarted/installation.html#install-pip
    If you installed kivy with the --user option (recommended if not in a virtualenv) or on the system, pass the command as the first parameter, such as via:
      $0 python3
      # or if Python3 is the default:
      # $0 python
END
            exit 1
        fi
    fi
    CMD="$VENV/bin/python"
    echo "$CMD $EXAMPLE_PATH"
    $CMD $EXAMPLE_PATH
else
    $CMD $EXAMPLE_PATH
fi
