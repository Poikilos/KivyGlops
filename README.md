# KivyGlops
Control 3D objects and the camera in your 3D Kivy app!
![Screenshot](https://raw.githubusercontent.com/expertmm/KivyGlops/master/screenshot01.png)

## Key Features
* 3D Objects can be moved and rotated separately (movement and rotation has been tested, and scaling is available)
* Has a KivyGlop format (and PyGlop for non-Kivy uses) as a metaformat that is OpenGL-ready, and can import OBJ files and potentially others
* Camera can be moved and rotated separately from objects
* Loads each object (even if in same OBJ file) separately, in a format readily usable by Kivy (Loads OBJ files into an intermediate format: KivyGlop)
* KivyGlops tutorials are available for download at [expertmultimedia.com/usingpython](http://expertmultimedia.com/usingpython/py3tutorials.html) (Unit 4 OpenGL)
* Triangulates (tesselates) obj input manually

## Changes
* (2017-12-11) _internal_bump_glop now calls the new _run_semicolon_separated_commands which calls the new _run_command method, so that these new methods are available to other methods
* (2017-12-11) give_item_by_keyword_to_player_number and give_item_by_index_to_player_number methods for manual item transfers without bumping or manually calling _internal_bump_glop
* (2017-12-11) moved projectile handling to _internal_bump_glop (formerly was directly after the _internal_bump_glop call)
* (2017-12-11) allow handling the obtain glop event by a new obtain_glop_by_index instead of obtain_glop in order to have access to the glop indices (you can still handle both if you desire for some reason, but be aware both will fire)
* (2017-11-06) Your KivyGlopsWindow implementation can now select mesh by name: self.select_mesh_by_name("some_named_mesh") (or filename but shows warning in stdout: self.select_mesh_by_name("somefilename") or self.select_mesh_by_name("somefilename.obj"))
* (2016-04-29) Switched to using only graphics that are public domain (changed license of modified resources to CC-BY-SA 4.0); such as, removed graphics based on cinder block wall from photoshoptextures.com due to quirky custom license
* (2016-02-12) Change the PyGlops ObjFile and objfile.py to WObjFile and wobjfile.py (to avoid naming conflict with ObjFile and objfile.py in Kivy examples)
* (2016-02-04) Finish separating (native) PyGlop from (Wavefront(R)) WObject for many reasons including: avoid storing redundant data; keep track of what format of data is stored in list members; allow storage of strict obj format; allow conversion back&forth or to other formats being sure of what o3d contains
* (2016-02-04) Rename *MesherMesh types to *Glop to avoid confusion with (Kivy's) Mesh type which is stored in *o3d._mesh
* (2016-01-10) Created new classes to hold the data from newobj and newmtl files, in order to keep strict obj+mtl data, separately from native opengl-style class
* (2015-05-12) Included a modified testnurbs file (with added textures and improved geometry); removed orion
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
* Develop a spec for the Window that is a part PyGlops somehow (without having to inherit from it, since window must inherit from OS or framewokr Window). Must include:
    * 
* Music loop option is not actually handled
* move event handlers and any other methods starting with underscore from kivyglops.py to pyglops.py where possible
    * moved from KivyGlopsWindow to PyGlops [new ones in brackets]:
        * _internal_bump_glop, after_selected_item, add_actor_weapon, get_player_glop_index
        * [give_item_by_keyword_to_player_number, give_item_by_index_to_player_number,_run_command, _run_semicolon_separated_commands, _run_commands, _run_command]
    * copied to KivyGlops and PyGlops, leaving KivyGlopsWindow methods that call them: hide_glop
        * already done: set_fly
* push_glop_item should create usable parent-child relationship for movement (at least for selected_item or costume accessories--there is no need to move inventory objects until they are visibly selected/held); or move item to the glop's canvas to accomplish that automatically
* pyglops: get_player_glop_index(player_number) should distinguish between multiple players (instead of ignoring param and using get_player_glop_index then falling through to which `is player_glop`)
* should behave as though you have 1 crate when you have 1 (instead of when you have 2)
* application crash during play_music internal methods if file does not exist
* should get self.scene.glops[bumped_index]._cached_floor_y from walkmesh underneath instead of self.scene._world_min_y
* should only place unique points into glop when individuating objects in o file
* fix glitch where walking into corner fights between walls (resolve by getting better pushed_angle that moves in same direction as walking instead of same direction as pushed back by boundary)
* Implement lighting by improving shader (instead of only flat shading of textured objects being available)
* Calculate rotation on other axes before calling look_at (only does y rotation currently, using a&d keys)
* Does not load map types from mtl that do not start with "map_":
    _map_bump_filename = None  # map_bump or bump: use luminance
    _map_displacement = None  # disp
    _map_decal = None # decal: stencil; defaults to 'matte' channel of image
    _map_reflection = None  # refl; can be -type sphere

## Planned Features
* show selected item in hand
* Use Z Buffer as parameter for effects such as desaturate by inverse normalized Z Buffer value so far away objects are less saturated1
* Implement thorough gamma correction (convert textures to linear space, then convert output back to sRGB) such as http://www.panda3d.org/blog/the-new-opengl-features-in-panda3d-1-9/
* Implement standard shader inputs and Nodes with Blender as a standard
    * allow Mix nodes
    * allow dot of Normal to be used as a Factor, such as for putting the result into an Mix node with black and white (or black and a color), where the result is sent to a Mix node set to Add (to create a colored fringe)
* Implement different shaders for different objects (such as by changing shader.vs and shader.fs to different vertex shader and fragment shader code after PopMatrix?)
    (can be done by subclassing Widget and setting self.vs and self.fs such as in C:\Kivy-1.8.0-py3.3-win32\kivy\examples\shader\plasma.py)
* Implement spherical background map
* Implement Image-Based Lighting (simply blur global background for basic effect)
* Implement fresnel_away_color fresnel_toward_color (can have alpha, and can be used for fake SSS)
* Implement full-screen shaders
* Add a plasma effect to example (such as using plasma shader from C:\Kivy-1.8.0-py3.3-win32\kivy\examples\shader\plasma.py)
    (note that the following uniforms need to be added:
        self.canvas['time'] = Clock.get_boottime()
        self.canvas['resolution'] = list(map(float, self.size))
    )
## License
Software is copyright Jake Gustafson and provided under GNU Lesser General Public License: https://www.gnu.org/licenses/lgpl.html
#### With the following caveats:
* KivyGlops was derived from [kivy-trackball](https://github.com/nskrypnik/kivy-trackball)
* The material loader was derived from [kivy-rotation3d](https://github.com/nskrypnik/kivy-rotation3d)
* kivy-rotation3d was presumably derived from main.py, objloader.py and simple.glsl in Kivy, approximately version 1.7.2

Resources are provided under Creative Commons Attribution Share-Alike (CC-BY-SA) license: http://creativecommons.org/licenses/by-sa/4.0/

#### With the following caveats:
*testnurbs-all-textured.obj was derived from testnurbs by nskrypnik

## Kivy Notes
* Kivy has no default vertex format, so pyglops.py provides OpenGL with vertex format (& names the variables)--see:
    PyGlop's __init__ method
position is vec4 as per https://en.wikipedia.org/wiki/Homogeneous_coordinates
* Kivy has no default model view matrix, so main window provides:
uniform mat4 modelview_mat;  //derived from self.canvas["modelview_mat"] = modelViewMatrix
uniform mat4 projection_mat;  //derived from self.canvas["projection_mat"] = projectionMatrix

## Developer Notes
* each program you make should be a subclass of KivyGlops or other PyGlops subclass (representing framework you are using other than Kivy)
* All subclasses of PyGlops should overload __init__, call super at beginning of it, and glops_init at end of it, like KivyGlops does.
* pymesher module (which does not require Kivy) loads obj files using intermediate WObjFile class (planned: save&load native PyMesher files), and provides base classes for all classes in kivymesher module
* pyrealtime module (which does not require Kivy) keeps track of keyboard state, allowing getting keystate asynchronously
* update-kivymesher.bat will only work for students if teacher places KivyGlops in R:\Classes\ComputerProgramming\Examples\KivyGlops
(which can be done using deploy.bat, if the folder already exists and the teacher has write permissions to the folder; the students should have read permissions to the folder)

### Shader Spec
vertex color is always RGBA
if vertex_color_enable then vertex color must be set for every vertex, and object diffuse_color is ignored
texture is overlayed onto vertex color
