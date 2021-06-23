# Contributing
This document explains some concepts to help you contribute code to KivyGlops itself.

Kivy Standards
* Kivy has no default vertex format, so pyglops.py provides OpenGL with vertex format (& names the variables)--see:
    PyGlop's __init__ method
position is vec4 as per https://en.wikipedia.org/wiki/Homogeneous_coordinates
* Kivy has no default model view matrix, so main window provides:
uniform mat4 modelview_mat;  //derived from self.canvas['modelview_mat'] = modelViewMatrix
uniform mat4 projection_mat;  //derived from self.canvas["projection_mat"] = projectionMatrix

KivyGlops Standards
* for glop to have custom shader, set kivyglop._own_shader_enable before adding glop, or add shader after calling add_glop
* eventually dict(s) will contain everything, so that emit_yaml can eventually be used to save glop format ("tmp" dict member should not be saved)
(these notes only apply to modifying the KivyGlops project files including PyGlops, or making a new subclass of PyGlop*)
  - `state` (formerly named `dat`) only contains the state, not permanent data.
  - a new dict such as `props` should contain all permanent data for easy saving
* ui is usually a KivyGlopsWindow but could be other frameworks. Must have:
```
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
        def update_debug_label(self)  # sets debug screen text to content of debug_dict
```
* Subclass of KivyGlops must have:
  * a new_glop_method method which returns your subclass of PyGlop (NOT of PyGlops), unless you are handling the `super(MySubclassOfGlop, self).__init__(self.new_glop_method)` (where MySubclassOfGlop is your class) `self.new_glop_method param` in your subclass' `__init__` method another way.
* All subclasses of PyGlops should overload __init__, call super at beginning of it, and glops_init at end of it, like KivyGlops does.
* PyGlops module (which does not require Kivy) loads obj files using intermediate WObjFile class (planned: save&load native PyGlops files), and provides base classes for all classes in KivyGlops module

### Debugging

#### Log visualizer
visualog is a separate program for viewing logs. Pass a log path as the
first parameter. Obtain a log such as via: `python example-stadium.py > log.txt`
Where example-stadium.py is your program which enables verbose logging.
![log visualizer screenshot](etc/log-visualizer.png)
The log visualizer shows objects by name from a 2D top view.

#### pdb
```
python3 -m pdb example-stadium.py
```

##### pdb commands
```
b: set a breakpoint
c: continue debugging until you hit a breakpoint
s: step through the code
n: to go to next line of code
l: list source code for the current file (default: 11 lines including the line being executed)
u: navigate up a stack frame
d: navigate down a stack frame
p: to print the value of an expression in the current context
```

You can get to the main event loop quickly using `c` then enter, then
hit Ctrl+C to stop and then `s` enter to begin stepping again.

Then you can set a breakpoint as follows (parameters are optional, but
without them, the current line is used). However, they will not be in
scope unless you get to the main event loop by chance. You can keep
pressing Ctrl+C and then `c` then enter until Ctrl+C lands you within
`kivyglops/__init__.py`.
- `b common.chatter`: This is an empty function just for use
  within pdb as shown.
- `p choice_world_vel` then enter `s` (or `c` for continue to breakpoint) then enter

Then you can do `c` then enter again, then when you get the breakpoint,
begin stepping again with `c` then enter.

### Breakpoint Hotkey
An easier way to use pdb when using KivyGlops is to:
- Call `set_verbose_enable(True)` in your program's loading phase.
- Run your program from a terminal.
- Press `b` which will call `breakpoint()` (only when verbose), which
  will drop the terminal into pdb.

##### Didn't work
- `b kivyglops.KivyGlops.update` (not in path)
- `b /home/owner/git/KivyGlops/kivyglops/__init__.py(1939)`
- `b /home/owner/git/KivyGlops/kivyglops/__init__.py(1939)update()`
- `b /home/owner/git/KivyGlops/kivyglops/__init__.py(1939)_on_keyboard_down()`

### Kivy `instructions` library notes
(see <https://github.com/kivy/kivy/blob/master/kivy/graphics/instructions.pxd>)
* RenderContext is a subclass of Canvas but adds many features such as:
  * `set_texture(index,texture)`
  * `push_state(name)` `pop_state(name)` `set_states(dict states)` (not available to python)
* Canvas is a subclass of InstructionGroup
* shader values can be set using `set_state` and a subcontext can be created using `push_state` in ContextInstruction
* InstructionGroup has `insert(index, instruction)` and `remove(index)` and a list named `children`
* Subclasses of anything in pyglops.py should have a get_class_name method as part of duck-typing warnings in copy_* and get_*deepcopy* methods

### wmaterial dict spec
This dict replaces deprecated WMaterial class in wobjfile.py.
This spec allows one dict to be used to completely store the Wavefront mtl format as per the full mtl spec such as at <http://paulbourke.net/dataformats/mtl/> [2].
* The wmaterials dict is the material library property of the WObjFile instance. Each wmaterial inside the wmaterials dict is a Wavefront material.
* The wmaterial's key in the wmaterials dict is the material name (given after "newmtl" in mtl file)
* each key is a material command, referring to a deeper dict, except "#" which is comments list
  * each material command dict has the following keys:
    * 'values' (a list of values)
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
  * if line in mtl file is `Kd 0.5 0.5 0.5` then dict wmaterial['Kd'] will have a list at 'values' key which is ["0.5", "0.5", "0.5"]
  * if line in mtl file is `bump -s 1 1 1 -o 0 0 0 -bm 1 sand.mpb` then the dict wmaterial['bump'] will have a list at 'values' key which is a list containing only the string sand.mpb; and dict at 'bump' key containing keys s, o, and bm which refer to lists containing the values following those args
  * if line in mtl file is `Ka spectral file.rfl 1.0` then, as per spec, `Ka spectral` is considered as the statement (or command) and wmaterial["Ka spectral"] will be a dict containing only one key, 'values' (since there are no other args in this case), which is `["file.rfl", "1.0"]` where 1.0 is the factor by which to multiply values in the file, as specified in the given mtl line.
  * if line in mtl file is `Ka xyz 1.0 1.0 1.0` then, as per spec, `Ka xyz` is considered as the statement (or command) and wmaterial["Ka spectral"] will be a dict containing only one key, 'values' (since there are no other args in this case), which is `["1.0", "1.0", "1.0"]`.
  * if line in mtl file is `refl -type cube_top file.png` then the dict wmaterial["refl -type cube_top"] will have a list at 'values' key which is ["file.png"]; the entire preceding part `refl -type cube_top` will be considered as the command to avoid overlap (to force consistent rule: one instance of command per material).

### Regression Tests
* `debug[` where should be `debug_dict[`
* always do: set index [3] (4th index) of vertex to 1.0 in order for matrix operations to work properly, especially before shader accesses the vertices
* `[x]`, `[y]`, or `[z]` where should be `[0]`, `[1]`, or `[2]`
* using `y` + `eye_height` where should be from floor: `minimums[1]` + `eye_height`
* using degrees where should be radians (such as large numbers on line where angle is set)
* using the same ancestors to call deepcopy or copy_as_subclass multiple times when should slice to original length first (since deepcopying that would cause pickling error which deepcopy_with_my_type was created to avoid, and calling deepcopy_with_my_type would be a major performance and possibly recursion issue)--see copy_as_subclass for correct usage
* using `get _is _verbose()` (without spaces [spaces added so doesn't get replaced in README with replace in all open files]) where should be `get_verbose_enable()`
* using `/ self.ui.frames_per_second` for determining distance per frame, where should use `* got_frame_delay` (which is not only in seconds but is the actual frame delay)
* always use: in_range_indices on bumpable and not bumper, for consistency
* always do: hit detection & a.i. BEFORE movement/physics (& programmer-overridable events such as on_update_glops), for intuitiveness (the situation that the user sees on the screen is the situation on which AI is based [is what the AI sees], and on which results [such as hitting a platform] are based)
* checking for .rel or "rel" in child (should check for 'links')
* checking for 'links' in parent (should check in child)
* use of not (x in y) where x and y are anything--(doesn't cause bug, but more readable as) where should be x not in y
* use of not (x is y) where x and y are anything--(doesn't cause bug, but more readable as) where should be x is not y
* checking for key in this_dict when answer None is treated same as missing--(doesn't cause bug, but) this_dict.get(key) is python's solution)
* deleting stuff from _bumper_indices or _bumpable_indices while running the bump loop [see "  # can't delete until bump loop is done in update" (set to None instead--they will be cleaned up by update after the bump loop--see # endregion nested bump loop)
* calling push_glop_item or push_item without removing it from _bumpable_indices (IF 'fit_enable' in return dict)
* `actor_dict["inventory_list"]` should be `actor_dict['inventory_items']`
* make sure all attack uses are in PyGlops.settings['globals']['attack_uses'] (for ai or other purposes)
* using fired_glop.item_dict in throw_glop where should instead use item_dict param (also, should create fired_glop.projectile_dict, and warn if already exists; projectile_dict is set to None on impact)
* calling a function and passing self as the first param (almost always wrong)
* using str(type(x)) where should be type(x).__name__
* result of builting type(x) function assumed to be string without using str(type(x)) where x is anything
* len used inside "[]" without "-1" (or "- 1" or other spacing)
* if you set `self.glops[index].properties['bump_enable'] = True` you should also do something like:
```python
self.glops[index].properties['bump_enable'] = True
self.glops[index].calculate_hit_range()
#usually you would manually control whether is actor or item:
if self.glops[index].actor_dict is not None:
    #actor
    self._bumper_indices.append(index)
else:
    #item
    self._bumpable_indices.append(index)
if self.glops[index].item_dict is not None:
    if 'as_projectile' in self.glops[index].item_dict
        self.glops[index].projectile_dict = self.glops[index].item_dict['as_projectile']
```

### Shader Spec
- vertex color is always RGBA
- if vertex_color_enable then vertex color must be set for every vertex,
  and object diffuse_color is ignored
- texture is overlayed onto vertex color

#### OpenGL ES notes
* mix is the ES equivalent of lerp (linear interpolation), which is the
  same as alpha blending

#### See Also
* kivy3 forks became advanced in the mid 2010s (lit models with texture
  optional). Later, Kivy adopted kivy3 and development skyrocketed!
  If you want a framework and not a game engine, you can try kivy3:
  `pip install -u https://github.com/kivy/kivy3/zipball/master` (leave
  off the `-u` if you are in a `virtualenv`)

## Works Cited

[1] Diane Ramey, Linda Rose, and Lisa Tyerman, "Object Files (.obj),"
paulbourke.net, October 1995. [Online]. Available:
http://paulbourke.net/dataformats/obj/. [Accessed Dec. 28, 2017].

[2] Diane Ramey, Linda Rose, and Lisa Tyerman, "MTL material format
(Lightwave, OBJ)," paulbourke.net, October 1995. [Online]. Available:
http://paulbourke.net/dataformats/obj/. [Accessed Dec. 28, 2017].
