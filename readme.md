# KivyGlops
Control 3D objects and the camera in your 3D Kivy app!
<https://github.com/expertmm/KivyGlops>
![Screenshot](https://raw.githubusercontent.com/expertmm/KivyGlops/master/screenshot01.png)

## Key Features
* 3D Objects can be moved and rotated separately (movement and rotation has been tested, and scaling is available)
* Has a KivyGlop format (and PyGlop for non-Kivy uses) as a metaformat that is OpenGL-ready, and can import OBJ files and potentially others
* Camera can be moved and rotated separately from objects
* Loads each object (even if in same OBJ file) separately, in a format readily usable by Kivy (Loads OBJ files into an intermediate format: KivyGlop)
* KivyGlops tutorials are available for download at [expertmultimedia.com/usingpython](http://expertmultimedia.com/usingpython/py3tutorials.html) (Unit 4 OpenGL)
* Triangulates (tesselates) obj input manually

## Usage:
* Lessons are available at [expertmultimedia.com/usingpython](http://www.expertmultimedia.com/usingpython)
  (click "Python 3," "Tutorials," "Start Learning Now," "Unit 2 (OpenGL)")
* spec for item_dict:
  * "uses": ("throw_linear" or "throw_arc") how missile behaves
  * "drop_enable": (True or False, or string like "yes", "no", etc) whether weapon leaves your inventory as soon as you use it (yes for rocks...hopefully you get the idea); considered True if not present
    * special variables used along with drop_enable False:
      "fired_sprite_size": tuple containing 2 floats (example: ` = (0.5, 0.5)`) in meters determining size of sprite in 3D space
      "fired_sprite_path": path to sprite (image will be placed on an automatically-generated square)
  * generated members:
    "subscript": (for debugging) if present in weapon_dict, it is the automatically-generated index of the object within the obj file from which the glop containing the weapon dict was loaded.
    "fires_glops": list of glops that will be fired (generated automatically if you use add_actor_weapon and have fired_sprite_path)
* fit_enable entry in item_event dict returned by push_item denotes whether giving an item to the player was possible (false if inventory was full on games with limited inventory)
* if you get a stack overflow, maybe one of the dict objects you put on an object contains a reference to the same object then copy or deepcopy_with_my_type was called
* each program you make should be a subclass of KivyGlops or other PyGlops subclass (if you subclass PyGlops for framework you are using other than Kivy, your *Glops class should have all methods that KivyGlops has since PyGlops expects self to have implemented methods such as load_obj)
* pyrealtime module (which does not require Kivy) keeps track of keyboard state, allowing getting keystate asynchronously
* To modify any files (other than examples or tests) see "Developer Notes" section of this file for more information.

### Teaching using KivyGlops:
* update-kivyglops from LAN.bat will only work for students if teacher places KivyGlops in R:\Classes\ComputerProgramming\Examples\KivyGlops
(which can be done using deploy.bat, if the folder already exists and the teacher has write permissions to the folder; the students should have read permissions to the folder)
* if segfault occurs, maybe camera and look_at location are same

## PyCharm Notes

### Configuration
* Add to the spelling dictionary: emissive


## Known Issues
* `on_obtain_glop` is missing from staging (only has warning on deprecated `def obtain_glop` which still works)
* (documentation) Change `get_owner_index` to `get_owner_key`
* (documentation) Change `pivot_to_geometry_enable` to `pivot_to_g_enable` (or add backward compatibility)
* Change `deg CAMERA_*` methods to static constants, and add object methods to set them for the purpose of retaining the docstrings.
* In `get_keycode` in staging, remove bare `except`; in stable, add the correct `except` that is missing.
* Use `resource_find` in `KivyGlop` to validate `source_path` and `material['properties']['diffuse_path']` before using the `PyGlop` `get_texture_diffuse_path` method which can't because it doesn't depend on Kivy.
* Remove all manual YAML generation.
* Add `plainReplacements['.target'] = ".properties['target']"` to KivyGlops-modernize.py
* Should copy as mesh instance generate a copy of the hitbox rather than using a reference?
* kivyglops.py (or kivyglops/__init__.py): Should `phi_eye_height` be .865 rather than 86.5??
* pyglops.py: remove kivy-specific _translate_instruction_* (in throw cases)
* projectile_speed of `item_dict` or of `item_dict["as_projectile"]` should override throw_speed of actor ONLY if present
* allow rocks to roll (and keep projectile_dict until they stop) in opengl9
* pyglops.py: (_internal_bump_glop; may not be an issue) plays `properties["bump_sound_paths"]` for both bumper (actor) and bumpable (item)
* pyglops.py: eliminate item_dict["fire_type"] dict (may contain "throw_linear" key) and merge with item_dict["uses"] (test with opengl6 or opengl7 since they use a weapon dict that is NOT a glop (only has fired_glop)--they may need to be changed)
* pyglops.py: eliminate (or improve & rename) index_of_mesh, select_mesh_at
* see `failed to deepcopy` -- not sure why happens
* by default do not set bounds; modify instructions on expertmultimedia.com to set bounds for office hallway project
* make a file-reading kernel for loading obj files to avoid blocking io
* this is a pending change (may not be changed ever) #instructions should be changed from `item_dict["use"] = "throw_arc"` to:
  `item_dict["uses"] = ["throw_arc"]`
  see example-stadium for more info
* pyglops.py (PyGlops __init__): implement _player_indices (already a list)
* fix nonworking ishadereditor.py (finish 3D version)
* pivot_to_geometry_enable is broken (must be left at default True): (defaults for pivot_to_geometry_enable are flipped since broken) pyglops.py: (append_wobject) make self.transform_pivot_to_geometry() optional, for optimization and predictability (added to set_as_item where pivot_to_geometry_enable; also added that option, to set_as_item, load_obj, get_glop_list_from_obj, append_wobject)
* renamed etc/kivyglops-mini-deprecated.py to testingkivy3d.py and MinimalKivyGlopsWindow class in it to TestingKivy3D
* see `context.add(this_glop._color_instruction)  #TODO: asdf add as uniform instead`
* Only load unique textures once (see "Loaded texture")
* if object has upward momentum, shouldn't stick to ground (is set near ground if player is near ground during `def use_selected`)
* pyglops.py: (`update`) throw_linear vs throw_arc setting is ignored (instead, gravity is always applied to missile if _cached_floor_y is present, which is present if there is a walkmesh, in which case ground_y is calculated then object's _cached_floor_y is set to ground_y)
* add touch inventory (such as tap to use, drag to change selected item)
* add touch joystick (drag to tilt joystick to dolly or strafe--optionally start at "forward" position)
* cache heightmap for each walkmesh as y-buffer (y is up; load from cache instead of recomputing if date >= source mesh file)
    * If was 64-bit (8bytes per fragment) 8 * 8192 * 8192 /1024/1024 = 512 MB
    * If was 32-bit (4bytes per fragment) 4 * 8192 * 8192 /1024/1024 = 256 MB
    * If was 16-bit (2bytes per fragment) 2 * 8192 * 8192 /1024/1024 = 128 MB
    * If was 16-bit (2bytes per fragment) 2 * 4096 * 4096 /1024/1024 = 32 MB
    * (as an unrelated performance comparison, an alpha lookup table is 256*256*256 /1024/1024 = 16 MB)
* fired sprite should stay facing camera (as add_actor_weapon sets look_target_glop)
* deal with situation-dependent members when saving glop:
    * `look_target_glop` which is a reference and for that reason copied by ref
    * `weapon_dict["fires_glops"]` which may be runtime-generated mesh such as texture on square mesh (or "meshes/sprite-square.obj")
* Add the following code to expertmultimedia.com boundary detection lesson since was removed from KivyGlops __init__ (or add after call to update_glops??):
  ```This is done axis by axis--the only reason is so that you can do OpenGL boundary detection lesson from expertmultimedia.com starting with this file
    if self.world_boundary_min[0] is not None:
        if self.player_glop._translate_instruction.x < self.world_boundary_min[0]:
            self.player_glop._translate_instruction.x = self.world_boundary_min[0]
    if self.world_boundary_min[1] is not None:
        if self.player_glop._translate_instruction.y < self.world_boundary_min[1]: #this is done only for this axis, just so that you can do OpenGL 6 lesson using this file (boundary detection)
            self.player_glop._translate_instruction.y = self.world_boundary_min[1]
    if self.world_boundary_min[2] is not None:
        if self.player_glop._translate_instruction.z < self.world_boundary_min[2]: #this is done only for this axis, just so that you can do OpenGL 6 lesson using this file (boundary detection)
            self.player_glop._translate_instruction.z = self.world_boundary_min[2]```
* eventually remove projectiles (though pop method of list takes from left, change _bumpable_indices to a deque for better pop performance):
  ```
  from collections import deque
  >>> l = deque(['a', 'b', 'c', 'd'])
  >>> l.popleft()```
* resource license: compatibility should be checked against original resource licenses
* vertex normals should supercede smoothing groups (which are based on faces) according to the obj format spec [1], but I'm not sure why since that would accomplish nothing since normals are blended across faces on OpenGL ES 2+
* implement vendor-specific commands at end of OBJ file (see wobjfile.py vs "Vendor specific alterations" section of <https://en.wikipedia.org/wiki/Wavefront_.obj_file>)
* implement Clara.io PBR extensions to OBJ format (see wobjfile.py vs "Physically-based Rendering" section of <https://en.wikipedia.org/wiki/Wavefront_.obj_file>)
* `texcoord_number` is always None during `this_face.append([vertex_number,texcoord_number,normal_number])` in wobjfile.py; see also stated_texcoord_number from which texcoord_number is derived when stated_texcoord_number is good
* fix issues introduced by refactoring:
        * throw_arc has no gravity
        * walkmesh is ignored
        * cylinder map doesn't work (is loaded at bottom left under 3D scene?)
* Music loop option is not actually handled
* move event handlers and any other methods starting with underscore from kivyglops.py to pyglops.py where possible
    * moved from KivyGlopsWindow to PyGlops [new ones in brackets]:
        * _internal_bump_glop, after_selected_item, add_actor_weapon, get_player_glop_index
        * [give_item_by_keyword_to_player_number, give_item_index_to_player_number,_run_command, _run_semicolon_separated_commands, _run_commands, _run_command]
    * copied to KivyGlops and PyGlops, leaving KivyGlopsWindow methods that call them: hide_glop
        * already done: set_fly [later refactored into set_player_fly]
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
* support surf and mg commands in OBJ
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
    (note that the following uniforms would need to be added for that example:
        self.canvas['time'] = Clock.get_boottime()
        self.canvas['resolution'] = list(map(float, self.size))
    )
## License
See [LICENSE](https://github.com/expertmm/KivyGlops/blob/master/LICENSE)

### Authors
Software is copyright Jake Gustafson with the following exceptions:
* KivyGlops object loading and opengl code was derived from [kivy-trackball](https://github.com/nskrypnik/kivy-trackball) (no license)
* The material loader was derived from [kivy-rotation3d](https://github.com/nskrypnik/kivy-rotation3d) (no license)
* kivy-rotation3d was presumably derived from main.py, objloader.py and simple.glsl in Kivy, approximately version 1.7.2 (originally MIT license)

Resources are provided under Creative Commons Attribution Share-Alike (CC-BY-SA) license: http://creativecommons.org/licenses/by-sa/4.0/

#### With the following caveats:
* testnurbs-all-textured.obj was derived from testnurbs by nskrypnik

## Kivy Notes
* Kivy has no default vertex format, so pyglops.py provides OpenGL with vertex format (& names the variables)--see:
    PyGlop's __init__ method
position is vec4 as per https://en.wikipedia.org/wiki/Homogeneous_coordinates
* Kivy has no default model view matrix, so main window provides:
uniform mat4 modelview_mat;  //derived from self.canvas["modelview_mat"] = modelViewMatrix
uniform mat4 projection_mat;  //derived from self.canvas["projection_mat"] = projectionMatrix

## Developer Notes
* for glop to have custom shader, set kivyglop._own_shader_enable before adding glop, or add shader after calling add_glop
* eventually dat will contain everything, so that emit_yaml can eventually be used to save glop format ("tmp" dict member should not be saved)
(these notes only apply to modifying the KivyGlops project files including PyGlops, or making a new subclass of PyGlop*)
* ui is usually a KivyGlopsWindow but could be other frameworks. Must have:
        width
        height
        frames_per_second
        def spawn_pex_particles(self, path, pos, radius=1.0, duration_seconds=None)
        def get_keycode(self, key_name)  # param such as 'a' (allow lowercase only), 'enter' or 'shift'
        def set_primary_item_caption(self, name)  # param such as "hammer"
        def add_glop(self, this_glop)
        def play_sound(self, path, loop=False)
        - and more for Kivy version (as used by KivyGlops):
                _contexts
                _contexts.remove(this_glop.get_context())
                canvas
* Subclass of KivyGlops must have:
    * a new_glop method which returns your subclass of PyGlop (NOT of PyGlops), unless you are handling the `super(MySubclassOfGlop, self).__init__(self.new_glop)` (where MySubclassOfGlop is your class) `self.new_glop param` in your subclass' `__init__` method another way.
* All subclasses of PyGlops should overload __init__, call super at beginning of it, and glops_init at end of it, like KivyGlops does.
* PyGlops module (which does not require Kivy) loads obj files using intermediate WObjFile class (planned: save&load native PyGlops files), and provides base classes for all classes in KivyGlops module

### Kivy `instructions` library notes
(see <https://github.com/kivy/kivy/blob/master/kivy/graphics/instructions.pxd>)
* RenderContext is a subclass of Canvas but adds many features such as:
    * `set_texture(index,texture)`
    * `push_state(name)` `pop_state(name)` `set_states(dict states)` (not available to python)
* Canvas is a subclass of InstructionGroup
* shader values can be set using `set_state` and a subcontext can be created using `push_state` in ContextInstruction
* InstructionGroup has `insert(index, instruction)` and `remove(index)` and a list named `children`

### wmaterial dict spec
This dict replaces deprecated WMaterial class in wobjfile.py.
This spec allows one dict to be used to completely store the Wavefront mtl format as per the full mtl spec such as at <http://paulbourke.net/dataformats/mtl/>.
    * The wmaterials dict is the material library property of the WObjFile instance. Each wmaterial inside the wmaterials dict is a Wavefront material.
    * The wmaterial's key in the wmaterials dict is the material name (given after "newmtl" in mtl file)
    * each key is a material command, referring to a deeper dict, except "#" which is comments list
        * each material command dict has the following keys:
            * "values" (a list of values)
                * if the command's (such as Kd) expected values are color values (whether rgb, or CIEXYZ if commands ends in " xyz"), only one color value means other 2 are same (grayscale)!
                * if the command's expected value is a filename, values is still a list--first value is filename, additional values are params (usually a factor by which to multiply values in the file)
                    * map can override: `Ka` (ambient color), `Kd` (diffuse color), `Ks` (specular color), `Ns` (specular coefficient scalar), `d` (opacity scalar), and surface normal (by way of bump map not normal map) according to spec
                        * displacement map is `disp` (in modern terms, a vertex displacement map)
                        * bump map is `bump`--though it affects normals, it is a standard bump map which in modern terms is a detail map (previously known as a [fragment]] displacement map; "represents the topology or height of the surface relative to the average surface.  Dark areas are depressions and light areas are high points." -Ramey)
                        * `refl` is a reflection map, or in modern terms, an environment map (is NOT a reflectance map): type can be sphere, or there can be several cube_* maps where * is the side (front, back, top, bottom, left, right)
            * "tmp" (a dict of temporary values such as "file_path", which was formerly stored in wmaterial.file_path, and "directory"; both of which are only for using relative paths in the mtl file)
            * "#" (comments list)
            * additional keys are args, where value is a list of the arg's values (if space-separated value in original mtl file starts with hyphen, it is an arg; an arg takes remaining values as items of its list, until next hyphen (or last entry, which is always appended to 'values')
                * may be an empty list, such as when key is "halo" (as specified by `-halo` option in mtl file)
    * examples (wmaterial is equivalent to wmaterials[material_name]):
        * if line in mtl file is `Kd 0.5 0.5 0.5` then dict wmaterial["Kd"] will have a list at "values" key which is ["0.5", "0.5", "0.5"]
        * if line in mtl file is `bump -s 1 1 1 -o 0 0 0 -bm 1 sand.mpb` then the dict wmaterial["bump"] will have a list at "values" key which is a list containing only the string sand.mpb; and dict at "bump" key containing keys s, o, and bm which refer to lists containing the values following those args
        * if line in mtl file is `Ka spectral file.rfl 1.0` then, as per spec, `Ka spectral` is considered as the statement (or command) and wmaterial["Ka spectral"] will be a dict containing only one key, "values" (since there are no other args in this case), which is `["file.rfl", "1.0"]` where 1.0 is the factor by which to multiply values in the file, as specified in the given mtl line.
        * if line in mtl file is `Ka xyz 1.0 1.0 1.0` then, as per spec, `Ka xyz` is considered as the statement (or command) and wmaterial["Ka spectral"] will be a dict containing only one key, "values" (since there are no other args in this case), which is `["1.0", "1.0", "1.0"]`.
        * if line in mtl file is `refl -type cube_top file.png` then the dict wmaterial["refl -type cube_top"] will have a list at "values" key which is ["file.png"]; the entire preceding part `refl -type cube_top` will be considered as the command to avoid overlap (to force consistent rule: one instance of command per material).

### Regression Tests
* deleting stuff from _bumper_indices or _bumpable_indices while running the bump loop [see "  # can't delete until bump loop is done in update" (set to None instead--they will be cleaned up by update after the bump loop--see #endregion bump loop)
* calling push_glop_item or push_item without removing it from _bumpable_indices (IF "fit_enable" in return dict)
* `actor_dict["inventory_list"]` should be `actor_dict["inventory_items"]`
* make sure all attack uses are in PyGlops.attack_uses (for ai or other purposes)
* using fired_glop.item_dict in throw_glop where should instead use item_dict param (also, should create fired_glop.projectile_dict, and warn if already exists; projectile_dict is set to None on impact)
* calling a function and passing self as the first param (almost always wrong)
* using str(type(x)) where should be type(x).__name__
* result of builting type(x) function assumed to be string without using str(type(x)) where x is anything
* len used inside "[]" without "-1" (or "- 1" or other spacing)
* if you set `self.glops[index].bump_enable = True` you should also do something like:
```python
self.glops[index].bump_enable = True
self.glops[index].calculate_hit_range()
#usually you would manually control whether is actor or item:
if self.glops[index].actor_dict is not None:
    #actor
    self._bumper_indices.append(index)
else:
    #item
    self._bumpable_indices.append(index)
if self.glops[index].item_dict is not None:
    if "as_projectile" in self.glops[index].item_dict
        self.glops[index].projectile_dict = self.glops[index].item_dict["as_projectile"]
```

### Shader Spec
vertex color is always RGBA
if vertex_color_enable then vertex color must be set for every vertex, and object diffuse_color is ignored
texture is overlayed onto vertex color
#### OpenGL ES notes
* mix is the ES equivalent of lerp (linear interpolation), which is the same as alpha blending

## Works Cited
[1] Diane Ramey, Linda Rose, and Lisa Tyerman, "Object Files (.obj)," paulbourke.net, October 1995. [Online]. Available: http://paulbourke.net/dataformats/obj/. [Accessed Dec. 28, 2017].
[2] Diane Ramey, Linda Rose, and Lisa Tyerman, "MTL material format (Lightwave, OBJ)," paulbourke.net, October 1995. [Online]. Available: http://paulbourke.net/dataformats/obj/. [Accessed Dec. 28, 2017].
