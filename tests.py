#!/usr/bin/env python

from kivyglops.wobjfile import (
    WObjFile,
    fetch_wmaterial,
)

objs = []
objs.append(WObjFile())
assert(objs[0].FACE_TC == WObjFile.FACE_TC)
assert(objs[0].FACE_TC == 1)
result = objs[0].load("this test tries a missing obj file")
print("objs[0].load:{}".format(result))
mtl = fetch_wmaterial("this test tries a missing mtl file")

objs.append(WObjFile())
result = objs[1].load("meshes/human-5ft4-7.5-poikilos.obj")
print("objs[1].load:{}".format(result))
# objs[1].load("meshes/shader-test.obj")

print("All tests passed.")
