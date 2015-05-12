# KivyMesher
Manage objects and camera in your 3D scene

## Features
* Loads OBJ files into an intermediate format (KivyMesherMesh)
* pymesher module (does not require Kivy) loads obj files, and provides base classes for all classes in kivymesher module
* pyrealtime module (does not require Kivy) keeps track of keyboard state, allowing getting keystate asynchronously
* KivyMesher tutorials are available for download at [expertmultimedia.com/usingpython](http://expertmultimedia.com/usingpython/py3tutorials.html) (Unit 4 OpenGL)

## Known Issues
* Triangulate objects (instead of leaving holes)
* Implement lighting by improving shader

## License
* Software is copyright Jake Gustafson and provided under GNU Lesser General Public License: https://www.gnu.org/licenses/lgpl.html
KivyMesher was derived from [kivy-trackball](https://github.com/nskrypnik/kivy-trackball)
The material loader was derived from [kivy-rotation3d](https://github.com/nskrypnik/kivy-rotation3d)
kivy-rotation3d was presumably derived from main.py, objloader.py and simple.glsl in Kivy, approximately version 1.7.2

* Resources are provided under Creative Commons Attribution Share-Alike (CC-BY-SA) license: http://creativecommons.org/licenses/by-sa/4.0/
testnurbs-all-textured.obj was derived from testnurbs by nskrypnik (however, texturing was added and geometry was improved)

