# KivyMesher
Manage objects and camera in your 3D scene

## Features
* Loads OBJ files into an intermediate format (KivyMesherMesh)
* pymesher module (does not require Kivy) loads obj files, and provides base classes for all classes in kivymesher module
* pyrealtime module (does not require Kivy) keeps track of keyboard state, allowing getting keystate asynchronously
* KivyMesher tutorials are available for download at [expertmultimedia.com/usingpython](http://expertmultimedia.com/usingpython/py3tutorials.html) (Unit 4 OpenGL)

## Changes
* (2015-05-12) Included testnurbs file with added textures and improved geometry; removed orion
* (2015-04-15) for clarity and less dependence on OBJ format, refactored object.vertices to object._vertex_strings, and refactored object.mesh.vertices to object.vertices
* (2015-04-15) changed "Material_orion.png" to "Material_orion" in orion.obj and orion.mtl to avoid confusion (it is a material object name, not a filename)
* (2015-04-15) added line to orion.obj: mtllib orion.mtl
* (2015-04-13) made pyramid in testnurbs-textured.obj into a true solid (had 0-sized triangles on bottom edges that had one face), simplified it manually, and made sides equilateral from side view
* (2015-04-13) no longer crashes on missing texture
* (2015-04-10) implemented mtl loader from kivy-rotation3d
* (2015-04-08) restarted from kivy-trackball-python3 (all old code disposed)
* (2015-04-06) changed vertex_format tuples from string,int,string to bytestring,int,string
* (2015-04-06) ran 2to3 (originally based on nskrypnik's kivy-rotation3d), which only had to change objloader (changes raise to function notation, and map(a,b) to map(list(a,b)) )

## Known Issues
* Triangulate objects (instead of leaving holes)
* Implement lighting by improving shader

## License
* Software is copyright Jake Gustafson and provided under GNU Lesser General Public License: https://www.gnu.org/licenses/lgpl.html
### With the following caveats:
* KivyMesher was derived from [kivy-trackball](https://github.com/nskrypnik/kivy-trackball)
* The material loader was derived from [kivy-rotation3d](https://github.com/nskrypnik/kivy-rotation3d)
* kivy-rotation3d was presumably derived from main.py, objloader.py and simple.glsl in Kivy, approximately version 1.7.2

* Resources are provided under Creative Commons Attribution Share-Alike (CC-BY-SA) license: http://creativecommons.org/licenses/by-sa/4.0/
### With the following caveats:
*testnurbs-all-textured.obj was derived from testnurbs by nskrypnik (however, texturing was added and geometry was improved)

