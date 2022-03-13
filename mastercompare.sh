#!/bin/sh
# meld ./ ~/git/KivyGlops
meld kivyglops.py ../KivyGlops/kivyglops/__init__.py &
meld pyglops.py ../KivyGlops/kivyglops/pyglops.py &
meld pyrealtime.py ../KivyGlops/kivyglops/pyrealtime.py &
meld example-stadium.py ../KivyGlops/kivyglops/example-stadium.py &

# For staging, run compare-staging.sh instead.
