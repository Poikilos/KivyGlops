#!/bin/sh
# meld ./ ~/git/KivyGlops-audit-3a66898
STAGING_DIR="KivyGlops-audit-3a66898"
meld ../$STAGING_DIR/kivyglops.py ../KivyGlops/kivyglops/__init__.py &
meld ../$STAGING_DIR/pyglops.py ../KivyGlops/kivyglops/pyglops.py &
meld ../$STAGING_DIR/pyrealtime.py ../KivyGlops/kivyglops/pyrealtime.py &
meld ../$STAGING_DIR/wobjfile.py ../KivyGlops/kivyglops/wobjfile.py &
