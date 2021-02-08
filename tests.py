#!/usr/bin/env python
import os
from kivyglops.wobjfile import (
    WObjFile,
    fetch_wmaterial,
)

objs = []
objs.append(WObjFile())
oI = len(objs) - 1
assert(objs[oI].FACE_TC == WObjFile.FACE_TC)
assert(objs[oI].FACE_TC == 1)
result = objs[oI].load("this test tries a missing obj file")
print("objs[{}].load:{}".format(oI, result))
mtl = fetch_wmaterial("this test tries a missing mtl file")

objs.append(WObjFile())
oI = len(objs) - 1
result = objs[oI].load("meshes/human-5ft4-7.5-poikilos.obj")
print("objs[{}].load:{}".format(oI, result))
# objs[oI].load("meshes/shader-test.obj")


profile = None
try:
    profile = os.environ['USERPROFILE']
except KeyError:
    profile = os.environ['HOME']
pCloud = os.path.join(profile, "Nextcloud")
if not os.path.isdir(pCloud):
    pCloud = os.path.join(profile, "ownCloud")
pmfs = os.path.join(pCloud, 'd.kivy', 'KivyGlops', 'etc',
                    'problematic mesh files')
if os.path.isdir(pmfs):
    print("INFO: The problematic mesh files directory is present.")
    oIStart = oI
    for sub in os.listdir(pmfs):
        if not sub.lower().endswith(".obj"):
            continue
        objs.append(WObjFile())
        oI = len(objs) - 1
        path = os.path.join(pmfs, sub)
        objs[oI].load(path)
    print("* finished processing {} problematic mesh files."
          "".format(oI - oIStart))
else:
    print("INFO: There are no problematic mesh files (no \"{}\")"
          "".format())

print("All tests passed.")
