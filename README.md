# KivyMesher
Manage objects and camera in your 3D scene

## Features
* Loads OBJ files into an intermediate format (KivyMesherMesh)
* pymesher module (does not require Kivy) loads obj files, and provides base classes for all classes in kivymesher module
* pyrealtime module (does not require Kivy) keeps track of keyboard state, allowing getting keystate asynchronously

## Known Issues
* Triangulate objects (instead of leaving holes)
* Implement lighting by improving shader

## License
* Software is copyright Jake Gustafson and provided under GNU Lesser General Public License: https://www.gnu.org/licenses/lgpl.html
* Resources are provided under Creative Commons Attribution Share-Alike (CC-BY-SA) license (testnurbs file is by nskrypnik, but improved by Jake Gustafson): http://creativecommons.org/licenses/by-sa/4.0/