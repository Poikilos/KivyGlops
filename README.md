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
* spec for weapon_dict:
  "droppable": ("yes" or "no") whether weapon leaves your inventory as soon as you use it (yes for rocks...hopefully you get the idea)
  "fired_sprite_size": tuple containing 2 floats (example: ` = (0.5, 0.5)`) in meters determining size of sprite in 3D space
  "fired_sprite_path": path to sprite (image will be placed on an automatically-generated square)
  "fire_type": ("throw_linear" or "throw_arc") how missile behaves (arc uses gravity)
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

## Changes
(2018-01-11)
* pyglops.py: (move `is_out_of_range` from `_internal_bump_glop` to `_update` in kivyglops.py and set immediately after checked) fixed issue where is_out_of_range was only being set for items
(2018-01-10)
* move `properties["inventory_items"]` to `actor_dict["inventory_items"]` (same for `"inventory_index"`)
* move `is_linked_as`, `get_link_as`, `get_link_and_type`, `push_glop_item`, `pop_glop_item` from KivyGlop to PyGlop
* made `projectile_dict` a deepcopy of `item_glop.item_dict["as_projectile"]` instead of a reference since `projectile_dict` contains flight-specific information
* changed `item["use"] = "*"` to `item["uses"] = ["*"]`  where * is a use for the item such as `throw_arc` or `melee`
* replaced `bump_sound_paths` with `properties["bump_sound_paths"]`
* created `add_damaged_sound_at` method for PyGlops scene (in properties so available to non-actors)
* (no longer inherits from Widget) workaround disturbing `'dict' is not callable` error in Kivy 1.9.0
* pyglops.py: (copy_as_subclass call in copy) fix potentially very bad bug -- `self.copy_as_subclass(self.new_glop, new_material_method)` had 3 params (not correct) 2nd one being another self.new_glop
* remove redundant call to _init_glop in KivyGlop __init__ (still calls it if super fails)
* improved monkey: added eyelids, UV mapped eyelids, improved texture for eyes and around eyes
* now uses _deferred_load_glops to load glops; to be more clear and functional, made separate load, loading, loaded booleans for *_glops_enable
(2018-01-09)
* fresnel.glsl utilize per-object booleans
* renamed shade-kivyglops-minimal.glsl to kivyglops-testing.glsl
* added `use_parent_frag_modelview=True` to RenderContext constructor for KivyGlop
* made _multicontext_enable global (if false, glop gets InstructionGroup as canvas instead of RenderContext)
* renamed print_location to log_camera_info
* consolidated get_verbose_enable() to be in one file only (common.py)
* pyglops.py: removed uses of `Logger` to `print` to be framework-independent
* eliminated scene.log_camera_info(); created kivyglop.emit_debug_to_dict(dict); moved ui's camera_walk_units_per_second and camera_turn_radians_per_second to *_glop.actor_dict["land_units_per_second"] and "land_degrees_per_second" (player_glop in this case); changed their per_frame equivalents to local variables in kivyglops.update
* move `self.camera_walk_units_per_second = 12.0` to actor_dict
* move `self.camera_turn_radians_per_second = math.radians(90.0)` to actor_dict
* fixed issue where projectile sprites not visible (probably a refactoring bug)
(2018-01-03)
* fixed selection crash (issue caused by refactoring)
* added use_walkmesh_at method for using walkmesh when you know glop index
* renamed set_as_item_by_index to set_as_item_at; set_as_actor_by_index to set_as_actor_at; explode_glop_by_index to explode_glop_at; kill_glop_by_index to kill_glop_at; give_item_by_index_to_player_number to give_item_index_to_player_number; obtain_glop_by_index to obtain_glop_at; add_bump_sound_by_index to add_bump_sound_at; select_mesh_by_index to select_mesh_at
* changed `set_player_fly(self, fly_enable)` to `set_player_fly(self, player_number, fly_enable)`
(2018-01-02)
* changed `new_glop` to `new_material` in KivyGlopsMaterial
(2018-01-01)
* changed KivyGlop canvas to default type instead of InstructionGroup
  * commented `self.canvas = InstructionGroup` in KivyGlop `__init__`
  * changed uses of texture0_enable to use canvas as dict
  * changed init to set it to RenderContext
  * kivyglops.py (KivyGlop) changed init to manually call _init_glop after __init__ since with multiple inheritance, super only calls first inherited object (first type in parenthesis on `class` line); renamed PyGlop __init__ to _init_glop; changed order of inheritance to `Widget, PyGlop`
* (2017-12-28) renamed _meshes to _contexts for clarity (but _meshes is used other places as an actual list of Mesh objects)
* (2017-12-28) moved glop canvas editing from KivyGlops.add_glop to KivyGlop.prepare_canvas
* (2017-12-28) added optional set_visible_enable param to add_glop (and made default not set visible to True)
* (2017-12-27) ishadereditor.py: made it use KivyGlops; renamed viewer to gl_widget
* (2017-12-27) fully implemented face grouping from complete OBJ spec including multiple groups (`g` with no param means "default" group, and no `g` at all means "default" group)
* (2017-12-27) renamed set_textures_from_mtl_dict to set_textures_from_wmaterial
* (2017-12-27) eliminated numerical indices for objects in WObjFile object (changed self.wobjects from list to dict), and name property of WObject
* (2017-12-27) In mtl loader, renamed `args_string`, `args` & `param` to `options_string`, `options` & `option` for clarity, since mtl spec calls the chunks following the command values: option if starts with hyphen, args if follow option, and values if is part of statement (or command) [1]
* (2017-12-27) transitioned from material classes to material dict--see "wmaterial dict spec" subheading under "Developer Notes" (since dict can just be interpreted later; and so 100% of data can be loaded even if mtl file doesn't follow spec)
* (2017-12-26) started implementing "carry" and dict-ify KivyGlops savable members ("tmp" dict member should not be saved)
* (2017-12-26) fixed issue where cooldown last used time wasn't set before item was first used (now is ready upon first time ever added to an inventory)
* (2017-12-22) refactored global get_glop_from_wobject into *Glop append_wobject to assist with overriding, and with expandability (in case multi submesh glops are needed later)
* (2017-12-22) renamed is_possible to fit_enable
* (2017-12-22) get_indices_by_source_path now checks against original_path (as passed to load_obj; non-normalized) in addition to processed path
* (2017-12-21) split `rotate_view_relative` into `rotate_camera_relative` and `rotate_player_relative`; moved them to KivyGlops since they use Kivy OpenGL instructions; renamed rotate_view_relative_around_point to rotate_relative_around_point and forces you to specify a glop as first parameter (still needs to be edited in major way to rotate around the point instead of assuming things about the object)
* (2017-12-21) fix issue where add_actor_weapon uses player_glop instead of the glop referenced by the glop_index param (bug was exposed by camera_glop and player_glop being separated)
* (2017-12-21) separated player_glop from camera_glop (see PyGlops __init__) and keys now move player instead of camera (if most recent param sent to self.set_camera_person was self.CAMERA_FIRST_PERSON(), which is done by default)
* (2017-12-21) (fixed issue introduced by refactoring) translate instruction should be copied by value not reference for glop
* (2017-12-21) changed emit_yaml methods since an object shouldn't need to know its own context to save (for example, should be allowable to have data members directly indented under line equal to "-")
* (2017-12-21) renamed *append_dump to *emit_yaml
* (2017-12-21) changed `Color(Color(1.0, 1.0, 1.0, 1.0))` to `Color(1.0, 1.0, 1.0, 1.0)`
* (2017-12-21) added copy constructors to PyGlops, PyGlopsMaterial, and where appropriate, subclasses
* (2017-12-21) renamed bump_sounds to bump_sound_paths for clarity
* (2017-12-21) renamed get_dict_deepcopy_except_my_type to deepcopy_with_my_type and made it work for either list or dict (and should work for any subclass since checks for type(self), so was eliminated from subclass)
* (2017-12-20) Changed to more permissive license (see [LICENSE](https://github.com/expertmm/KivyGlops/blob/master/LICENSE))
* (2017-12-20) updated kivyglopstesting.py to account for refactoring
* (2017-12-20) renamed kivyglopsminimal.py to etc/kivyglops-mini-deprecated.py
* (2017-12-19) wobjfile.py: elimintated smoothing_group in favor of this_face_group_type and this_face_group_name (this_face_group_type "s" is a smoothing group)
* (2017-12-19) wobjfile.py: always use face groups, to accomodate face groups feature of OBJ spec [1]; added more fault-tolerance to by creating vertex list whenever first vertex of a list is declared, and creating face groups whenever first face of a list is declared
* (2017-12-19) standardized emit_yaml methods (and use standard_emit_yaml when necessary) for consistent yaml and consistent coding: (list, tab, name [, data | self])
* (2017-12-19) store vertex_group_type in WObject (for future implementation)
* (2017-12-19) added ability to load non-standard obj file using commands without params; leave WObject name as None if not specified, & added ability to load non-standard object signaling (AND naming) in obj file AFTER useless g command, (such as, name WObject `some_name` if has `# object some_name then useless comments` on any line before data but after line with just `g` or `o` command but only if no name follows those commands)
* (2017-12-17) frames_per_second moved from KivyGlops to KivyGlops window since is implementation specific (and so KivyGlops instance doesn't need to exist during KivyGlopsWindow constructor)
* (2017-12-16) complete shift of most methods from KivyGlopsWindow to PyGlops, or at least KivyGlops if kivy-specific; same for lines from init; same for lines from update_glsl (moved to new PyGlops `update` method)
* (2017-12-16) renamed create_mesh to new_glop for clarity, and use new_glop to create camera so conversion is not needed (eliminate get_kivyglop_from_pyglop)
        * rename get_pyglops_list_from_obj to get_glop_list_from_obj
        * rename get_pyglop_from_wobject to get_glop_from_wobject
* (2017-12-16) Changed recipe for game so that you subclass KivyGlops instead of KivyGlopsWindow (removes arbitrary border between ui and scene, and changes self.scene. to self. in projects which utilize KivyGlops)
* (2017-12-11) Began developing a platform-independent spec for the ui object so that PyGlops can specify more platform-independent methods (such as _internal_bump_glop) that push ui directly (ui being the platform-DEPENDENT object such as KivyGlopsWindow, which must inherit from some kind of OS Window or framework Window).
    * so far, ui must include:
        * ui.bump_glop (bumpable_name, bumper_name)
        * and in the future, potentially anything else in KivyGlopsWindow (KivyGlopsWindow is the only tested spec at this time, however see Developer Notes section of this file, which should be maintained well)
* (2017-12-11) _internal_bump_glop now calls the new _run_semicolon_separated_commands which calls the new _run_command method, so that these new methods are available to other methods
* (2017-12-11) give_item_by_keyword_to_player_number and give_item_index_to_player_number methods for manual item transfers without bumping or manually calling _internal_bump_glop
* (2017-12-11) moved projectile handling to _internal_bump_glop (formerly was directly after the _internal_bump_glop call)
* (2017-12-11) allow handling the obtain glop event by a new obtain_glop_at instead of obtain_glop in order to have access to the glop indices (you can still handle both if you desire for some reason, but be aware both will fire)
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
* by default do not set bounds; modify instructions on expertmultimedia.com to set bounds for office hallway project
* make a file-reading kernel for loading obj files to avoid blocking io
* this is a pending change (may not be changed ever) #instructions should be changed from `item_dict["use"] = "throw_arc"` to:
  ```python
  item_dict["uses"] = ["throw_arc"]
  ```
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
                        * bump map is `bump`--though it affects normals, it is a standard bump map which in modern terms is a (fragment) displacement map ("represents the topology or height of the surface relative to the average surface.  Dark areas are depressions and light areas are high points." -Ramey
                        * `refl` is a reflection map, or in modern terms, an environment map (as opposed to a reflectance map): type can be sphere, or there can be several cube_* maps where * is the side (front, back, top, bottom, left, right)
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
* result of builting type(x) function assumed to be string without using str(type(x)) where x is anything
* len used inside "[]" without "-1" (or "- 1" or other spacing)


### Shader Spec
vertex color is always RGBA
if vertex_color_enable then vertex color must be set for every vertex, and object diffuse_color is ignored
texture is overlayed onto vertex color
#### OpenGL ES notes
* mix is the ES equivalent of lerp (linear interpolation), which is the same as alpha blending

## Works Cited
[1] Diane Ramey, Linda Rose, and Lisa Tyerman, "Object Files (.obj)," paulbourke.net, October 1995. [Online]. Available: http://paulbourke.net/dataformats/obj/. [Accessed Dec. 28, 2017].
[2] Diane Ramey, Linda Rose, and Lisa Tyerman, "MTL material format (Lightwave, OBJ)," paulbourke.net, October 1995. [Online]. Available: http://paulbourke.net/dataformats/obj/. [Accessed Dec. 28, 2017].
