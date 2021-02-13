# KivyGlops
<https://github.com/poikilos/KivyGlops>

Control 3D objects and the camera in your 3D Kivy app!

The operating principle of this project is to focus on completeness.
This does not mean that the engine is completely opinionated, but
rather that the API is comprehensive enough to make various types of
games. The project will try not to limit the programmer, but also
provide ways to create games that are not boring to code. This means
that things will work before they work well.

For example:
- walkmeshes should work before they work with physics
- physics should
  work before they use Bullet
- shaders should shade objects with or without textures
  - before they shade objects with physically-based lighting
- movement should work before bones and other mesh animations work
- meshes should import in a fault-tolerant way before more formats
  are supported.

(See also [Issues](https://github.com/poikilos/KivyGlops/issues))

Because of following this principle, all of those things
have worked for a long time even though they are under heavy
development. Another benefit of this approach is that you can create
your project based on kivyglopsexampleblank.py (save it as a different
py file in same folder) then upgrade all of the other files with a new
version of KivyGlops and your project will increase in quality, but
your project will not have been limited in quantity (scope) by adopting
KivyGlops early. I hope that this software inspires you to create more
complete publicly-licensed code projects, whether using KivyGlops or
just learning from its OpenGL and GLSL code.

![Screenshot](screenshot01.png)

## Key Features
- Move and rotate 3D Objects separately
  ([Tutorials](https://expertmultimedia.com/usingpython/py3) demonstrate
  movement and rotation, and scaling is available).
- Move and rotate the camera separately from objects.
- Load each object (even if in same OBJ file) separately and in a format
  readily usable by Kivy (Load OBJ files into an intermediate format:
  KivyGlop)
  - The KivyGlop format (and PyGlop for non-Kivy uses) as a metaformat
    that is OpenGL-ready, and can import OBJ files and potentially others.
* KivyGlops tutorials are available for download at
  [expertmultimedia.com/usingpython](https://expertmultimedia.com/usingpython/py3/)
  (Unit 4 OpenGL)
* The engine itself triangulates (tesselates) OBJ files to meet the
  requirement of triangles (to avoid holes present when loading some
  models in other 3D Kivy examples).


## Usage:
- Lessons are available at
  [expertmultimedia.com/usingpython](http://www.expertmultimedia.com/usingpython)
  (click "Python 3," "Tutorials," "Start Learning Now," "Unit 2
  (OpenGL)") "Unit 2" will be used to refer Unit 2 of this site in this
  document.
- spec for actor_dict:
  - actor_dict is a dictionary that can contain custom variables such as
    actor_dict['hp']
  - actor_dict sent to set_as_actor_at will be copied (by
    self.deepcopy_with_my_type [which allows deepcopy of glops within a
    dict], not by reference), so you can change it later for making
    similar actors without any problems
  - actor_dict will be filled in with required variables when you call
    set_as_actor_at, but the method will overlay your variables over
    the defaults, except for builtins with runtime info such as the
    `actor_dict['state']` dict which should be left alone.
  - if you want ai, you must set actor_dict["ai_enable"] = True
    - if you enable ai, the on_process_ai event will occur every frame
      before ai variables are checked (but the AI won't do anything
      unless you set the actor_dict variables during on_process_ai; see
      the AI section below)
      - See also "Unit 2" lesson 7
  - clip_enable can be in actor dict: it and any other keys that are in
    `self.settings['templates']['actor_properties']` will be moved to
    `properties`
- spec for item_dict:
  - 'uses' is a list containing use strings as follows:
    - uses like "throw_linear" or 'throw_arc' or "shoot_linear" causes the item to be thrown
      - if "throw_" is in the use entry, player's ranges will be used (for example, if you set item_dict["throw_custom"], also set unit_glop.actor_dict['ranges']["throw_custom"] (if already set as actor, you don't need to do actor_dict['ranges'] = {} for it will already exist as a dict)
      - if "shoot_" is in the use entry, item's ranges will be used (for example, if you set item_dict["shoot_custom"], also set item_dict['ranges']={} then item_dict['ranges']["shoot_custom"])
      - NOTE: though the units where actor_dict["ai_enable"] is True will attack from that range, physics will determine whether the projectile reaches its target
  - 'drop_enable': (True or False, or string like "yes", "no", etc) whether weapon leaves your inventory as soon as you use it (yes for rocks...hopefully you get the idea); considered True if not present
    - special variables used along with drop_enable False:
      'fired_sprite_size': tuple containing 2 floats (example: ` = (0.5, 0.5)`) in meters determining size of sprite in 3D space
      'fired_sprite_path': path to sprite (image will be placed on an automatically-generated square)
  - 'projectile_keys': a list of variables that will be copied to the projectile (if projectile hits, projectile_dict will not be None, and will contain your variables whose keys you listed, when on_attacked_glop occurs)
  - generated members:
    'fires_glops': list of glops that will be fired (generated automatically if you use add_actor_weapon and have fired_sprite_path)
* attack_uses is a list of strings and can be accessed or changed from within your implementation of KivyGlops using self.settings['globals']['attack_uses'] (first ones in list will be preferred by actors where `actor_dict["ai_enable"]` is true)
* fit_enable entry in item_event dict returned by push_item denotes whether giving an item to the player was possible (false if inventory was full on games with limited inventory)
* if you get a stack overflow, maybe one of the dict objects you put on an object contains a reference to the same object then copy or deepcopy_with_my_type was called
* each program you make should be a subclass of KivyGlops or other PyGlops subclass (if you subclass PyGlops for framework you are using other than Kivy, your *Glops class should have all methods that KivyGlops has since PyGlops expects self to have implemented methods such as load_obj)
* pyrealtime module (which does not require Kivy) keeps track of keyboard state, allowing getting keystate asynchronously
* To modify any files (other than examples or tests) see "Developer Notes" section of this file for more information.
* this_glop.state is for data which should be in saved state such as game save but not in exported object--also you can use item_dict['state'] or actor_dict['state']; use properties or item_dict or actor_dict directly for permanent data.
* any glop where glop.actor_dict is not None will be treated as an actor, so use set_as_actor_at instead of creating it yourself, so that the necessary variables will be set for proper engine function.
* implement attacked_glop_at for unit-targeting attacks
* implement on_at_rest for whenever items stop being affected by physics (such as for area of effect items such as launched missiles)
    * NOTE: if a player is hit by the missile, attacked_glop_at will also be called by the engine
* implement on_update_glops to do stuff every frame, after ai (and remote players in future version) occurs but before physics and constraints are calculated
    * For example, if you want a sports game, normally if you get hit by a projectile you don't obtain it (move away and come back and if it is still there, then you can obtain it)--this is realistic since if you got a rock thrown at you and it hits you, you probably won't catch it; maybe some way of overriding this could be implemented for a sports game with a ball, otherwise you can just only allow catching it before it hits you (you could try to catch it in on_update_glops--set projectile_dict to None so it _internal_bump_glop doesn't block obtaining it)
* to add values to debug screen (F3 to view):
    * to simply add a value, manipulate the global debug dict such as `debug_dict["time"] = "12:00pm"`
    * if you want to format a tuple, you could do `debug_dict["boss.pos"] = fixed_width(boss.pos, 4, " ")`
    * if you want a new category, make a new dict in debug_dict such as `debug_dict["earth"] = {}` then set your values such as `debug_dict["earth"]["water"] = 71.`
* to change defaults for properties, actor_dict, and item_dict, see `settings['templates']`
    * settings guarantees certain values needed by the engine (like a class, but more "functional" and easier to automatically load and save only the relevant values in human-readable format), so avoid deleting any dicts or values or setting anything to None in the defaults of `settings` or `settings['templates']` unless you have subclassed PyGlops in a way that you know you don't need the values

### AI
* If you implement the KivyGlops on_process_ai method, you shouldn't move anything otherwise glitches will almost certainly occur. This is not a limitation of the engine--it is a recommendation to be logical, so that you ensure your visuals presented to the player make sense.
  * Things that you can safely do in on_process_ai include:
    * cause glop that is an actor to use items (via the use_item_at method of a glop)
    * set indices and strings that will be used to control the character, such as values at the following keys in glop's actor_dict: 'moveto_index', 'target_index' which refer to objects in the self.glops list
  * Things that are not so great but still work:
    * set a non-ai variable in an actor_dict (such as, modify health--which should probably be done in on_at_rest or attacked_glop_at)
  * NOTE: after on_process_ai is called, the `actor_dict['target_index']` will be set to None if the item doesn't have any item where any of the item's uses are in attack_uses, unless you set `actor_dict['unarmed_melee_enable'] = True`

### Teaching using KivyGlops:
* update-kivyglops from LAN.bat will only work for students if teacher places KivyGlops in R:\Classes\ComputerProgramming\Examples\KivyGlops
(which can be done using deploy.bat, if the folder already exists and the teacher has write permissions to the folder; the students should have read permissions to the folder)
* if segfault occurs, maybe camera and look_at location are same

## Changes
See [Changelog](changelog.md)


## Known Issues
* only set glop's glop_index and glop's state['glop_index'] in add_glop, nowhere else
* add pathing for processing `actor_dict['target_pos']` (even if not ai_enable, in case of strategy game where target_pos is set on a player-controlled glop)
* implement seperable_offsets for explosions
* eliminate foot_reach in favor of using hitbox
* did not test air-move or double-jump in on_update_glops
* eliminate look_target_glop in favor of a relationship in 'links'
* upload updated version of lessons to website mentioned in Usage section (in the meantime see testing.py for updated code, or see Changes section for anything that says "renamed" or "required")
* pyglops.py: remove kivy-specific _translate_instruction_* (in throw cases)
* projectile_speed of `item_dict` or of `item_dict['as_projectile']` should override throw_speed of actor ONLY if present
* allow rocks to roll (and keep projectile_dict until they stop) in opengl9
* pyglops.py: (_internal_bump_glop; may not be an issue) plays `properties['bump_sound_paths']` for both bumper (actor) and bumpable (item)
* pyglops.py: eliminate item_dict['fire_type'] dict (may contain "throw_linear" key) and merge with item_dict['uses'] (test with opengl6 or opengl7 since they use a weapon dict that is NOT a glop (only has fired_glop)--they may need to be changed)
* pyglops.py: eliminate (or improve & rename) index_of_mesh, select_mesh_at
* see `failed to deepcopy` -- not sure why happens
* by default do not set bounds; modify instructions on expertmultimedia.com to set bounds for office hallway project
* make a file-reading kernel for loading obj files to avoid blocking io
* this is a pending change (may not be changed ever) #instructions should be changed from `item_dict['use'] = 'throw_arc'` to:
  `item_dict['uses'] = ['throw_arc']`
  see example-stadium for more info
* pyglops.py (PyGlops __init__): implement _player_indices (already a list)
* fix nonworking ishadereditor.py (finish 3D version)
* pivot_to_g_enable is broken (must be left at default True): (defaults for pivot_to_g_enable are flipped since broken) pyglops.py: (append_wobject) make self.transform_pivot_to_geometry() optional, for optimization and predictability (added to set_as_item where pivot_to_g_enable; also added that option, to set_as_item, load_obj, get_glop_list_from_obj, append_wobject)
* renamed etc/kivyglops-mini-deprecated.py to testingkivy3d.py and MinimalKivyGlopsWindow class in it to TestingKivy3D
* see `context.add(this_glop._color_instruction)  # TODO: asdf add with set_uniform instead`
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
    * `weapon_dict['fires_glops']` which may be runtime-generated mesh such as texture on square mesh (or "meshes/sprite-square.obj")
* Add the following code to expertmultimedia.com boundary detection lesson since was removed from KivyGlops __init__ (or add after call to on_update_glops??):
  ```This is done axis by axis--the only reason is so that you can do OpenGL boundary detection lesson from expertmultimedia.com starting with this file
    if self.world_boundary_min[0] is not None:
        if self.player_glop._t_ins.x < self.world_boundary_min[0]:
            self.player_glop._t_ins.x = self.world_boundary_min[0]
    if self.world_boundary_min[1] is not None:
        if self.player_glop._t_ins.y < self.world_boundary_min[1]: # this is done only for this axis, just so that you can do OpenGL 6 lesson using this file (boundary detection)
            self.player_glop._t_ins.y = self.world_boundary_min[1]
    if self.world_boundary_min[2] is not None:
        if self.player_glop._t_ins.z < self.world_boundary_min[2]: # this is done only for this axis, just so that you can do OpenGL 6 lesson using this file (boundary detection)
            self.player_glop._t_ins.z = self.world_boundary_min[2]```
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
  ```python
    _map_bump_filename = None  # map_bump or bump: use luminance
    _map_displacement = None  # disp
    _map_decal = None # decal: stencil; defaults to 'matte' channel of image
    _map_reflection = None  # refl; can be -type sphere
```
* cylindrical-mapped backgrounds should be pi-ratio so they don't repeat (such as 3142 x 1000) since the engine refuses to stretch them (by design)


## Planned Features
* support surf and mg commands in OBJ
* show selected item in hand
* Use Z Buffer as parameter for effects such as desaturate by inverse normalized Z Buffer value so far away objects are less saturated1
* Implement thorough gamma correction (convert textures to linear space, then convert output back to sRGB) such as http://www.panda3d.org/blog/the-new-opengl-features-in-panda3d-1-9/
* Implement standard shader inputs and Nodes (see Blender as a reference)
  * allow Mix nodes
  * allow dot of Normal to be used as a Factor, such as for putting the result into an Mix node with black and white (or black and a color), where the result is sent to a Mix node set to Add (to create a colored fringe)
* Implement different shaders for different objects (such as by changing shader.vs and shader.fs to different vertex shader and fragment shader code after PopMatrix?)
    (It can be done by subclassing Widget and setting self.vs and self.fs such as in C:\Kivy-1.8.0-py3.3-win32\kivy\examples\shader\plasma.py)
* Implement spherical background map
* Implement Image-Based Lighting (simply blur global background for basic effect)
* Implement fresnel_away_color fresnel_toward_color (can have alpha, and can be used for fake SSS)
* Implement full-screen shaders
* Add a plasma effect to example (such as using plasma shader from C:\Kivy-1.8.0-py3.3-win32\kivy\examples\shader\plasma.py)
  - Note that the following uniforms would need to be added for that example:
    ```python
        self.canvas['time'] = Clock.get_boottime()
        self.canvas['resolution'] = list(map(float, self.size))
```


## License
See [license.txt](license.txt).

### Authors
Software is copyright Jake Gustafson with the following exceptions:
* KivyGlops object loading and opengl code was derived from
  [kivy-trackball](https://github.com/nskrypnik/kivy-trackball) (no
  license).
* The material loader was derived from
  [kivy-rotation3d](https://github.com/nskrypnik/kivy-rotation3d) (no
  license).
* kivy-rotation3d was presumably derived from main.py, objloader.py and
  simple.glsl in Kivy, approximately version 1.7.2 (originally MIT
  license).

Resources are provided under Creative Commons Attribution Share-Alike
([CC BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/))
license.

#### With the following caveats:
* testnurbs-all-textured.obj was derived from testnurbs by nskrypnik

## Kivy Notes
* Kivy has no default vertex format, so pyglops.py provides OpenGL with vertex format (& names the variables)--see:
    PyGlop's __init__ method
position is vec4 as per https://en.wikipedia.org/wiki/Homogeneous_coordinates
* Kivy has no default model view matrix, so main window provides:
uniform mat4 modelview_mat;  //derived from self.canvas['modelview_mat'] = modelViewMatrix
uniform mat4 projection_mat;  //derived from self.canvas["projection_mat"] = projectionMatrix

## Developer Notes
* for glop to have custom shader, set kivyglop._own_shader_enable before adding glop, or add shader after calling add_glop
* eventually dat will contain everything, so that emit_yaml can eventually be used to save glop format ("tmp" dict member should not be saved)
(these notes only apply to modifying the KivyGlops project files including PyGlops, or making a new subclass of PyGlop*)
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
This spec allows one dict to be used to completely store the Wavefront mtl format as per the full mtl spec such as at <http://paulbourke.net/dataformats/mtl/>.
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
* kivy3 forks are getting pretty advanced now (lit models with texture
  optional). If you want a framework and not a game engine, try
  `pip install https://github.com/KeyWeeUsr/kivy3/zipball/master`

## Works Cited

[1] Diane Ramey, Linda Rose, and Lisa Tyerman, "Object Files (.obj),"
paulbourke.net, October 1995. [Online]. Available:
http://paulbourke.net/dataformats/obj/. [Accessed Dec. 28, 2017].

[2] Diane Ramey, Linda Rose, and Lisa Tyerman, "MTL material format
(Lightwave, OBJ)," paulbourke.net, October 1995. [Online]. Available:
http://paulbourke.net/dataformats/obj/. [Accessed Dec. 28, 2017].
