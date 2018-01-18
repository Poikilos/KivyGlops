# KivyGlops
Control 3D objects and the camera in your 3D Kivy app!
<https://github.com/expertmm/KivyGlops>
The operating principle of this project is to focus on completeness. This means that things will work before they work well. For example: walkmeshes should work before they work with physics; physics should work before they use Bullet; shaders should shade objects with or without textures before they shade objects with physically-based lighting; movement should work before bones and other mesh animations work; meshes should import in a fault-tolerant way before more formats are supported. Because of following this principle, all of those things have worked for a long time even though they are under heavy development. Another benefit of this approach is that you can create your project based on kivyglopsexampleblank.py (save it as a different py file in same folder) then upgrade all of the other files with a new version of KivyGlops and your project will increase in quality, but your project will not have been limited in quantity (scope) by adopting KivyGlops early. I hope that this software inspires you to create more complete publicly-licensed code projects, whether using KivyGlops or not.
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
  "Unit 2" will be used to refer Unit 2 of this site in this document.
* spec for actor_dict:
  * actor_dict is a dictionary that can contain custom variables such as actor_dict["hp"]
  * actor_dict sent to set_as_actor_at will be copied (by self.deepcopy_with_my_type [which allows deepcopy of glops within a dict], not by reference), so you can change it later for making similar actors without any problems
  * actor_dict will be filled in with required variables when you call set_as_actor_at, but the method will overlay your variables over the defaults, except for builtins with runtime info such as the `actor_dict["state"]` dict which should be left alone.
  * if you want ai, you must set actor_dict["ai_enable"] = True
    * if you enable ai, the on_process_ai event will occur every frame before ai variables are checked (but the AI won't do anything unless you set the actor_dict variables during on_process_ai; see the AI section below)
  (see also "Unit 2" lesson 7)
  * can have clip_enable in actor dict: it and any other keys that are in `self.settings["templates"]["actor_properties"]` will be moved to `properties`
* spec for item_dict:
  * "uses" is a list containing use strings as follows:
    * uses like "throw_linear" or "throw_arc" or "shoot_linear" causes the item to be thrown
      * if "throw_" is in the use entry, player's ranges will be used (for example, if you set item_dict["throw_custom"], also set unit_glop.actor_dict["ranges"]["throw_custom"] (if already set as actor, you don't need to do actor_dict["ranges"] = {} for it will already exist as a dict)
      * if "shoot_" is in the use entry, item's ranges will be used (for example, if you set item_dict["shoot_custom"], also set item_dict["ranges"]={} then item_dict["ranges"]["shoot_custom"])
      * NOTE: though the units where actor_dict["ai_enable"] is True will attack from that range, physics will determine whether the projectile reaches its target
  * "drop_enable": (True or False, or string like "yes", "no", etc) whether weapon leaves your inventory as soon as you use it (yes for rocks...hopefully you get the idea); considered True if not present
    * special variables used along with drop_enable False:
      "fired_sprite_size": tuple containing 2 floats (example: ` = (0.5, 0.5)`) in meters determining size of sprite in 3D space
      "fired_sprite_path": path to sprite (image will be placed on an automatically-generated square)
  * "projectile_keys": a list of variables that will be copied to the projectile (if projectile hits, projectile_dict will not be None, and will contain your variables whose keys you listed, when on_attacked_glop occurs)
  * generated members:
    "fires_glops": list of glops that will be fired (generated automatically if you use add_actor_weapon and have fired_sprite_path)
* attack_uses is a list of strings and can be accessed or changed from within your implementation of KivyGlops using self.settings["globals"]["attack_uses"] (first ones in list will be preferred by actors where `actor_dict["ai_enable"]` is true)
* fit_enable entry in item_event dict returned by push_item denotes whether giving an item to the player was possible (false if inventory was full on games with limited inventory)
* if you get a stack overflow, maybe one of the dict objects you put on an object contains a reference to the same object then copy or deepcopy_with_my_type was called
* each program you make should be a subclass of KivyGlops or other PyGlops subclass (if you subclass PyGlops for framework you are using other than Kivy, your *Glops class should have all methods that KivyGlops has since PyGlops expects self to have implemented methods such as load_obj)
* pyrealtime module (which does not require Kivy) keeps track of keyboard state, allowing getting keystate asynchronously
* To modify any files (other than examples or tests) see "Developer Notes" section of this file for more information.
* this_glop.state is for data which should be in saved state such as game save but not in exported object--also you can use item_dict["state"] or actor_dict["state"]; use properties or item_dict or actor_dict directly for permanent data.
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
* to change defaults for properties, actor_dict, and item_dict, see `settings["templates"]`
    * settings guarantees certain values needed by the engine (like a class, but more "functional" and easier to automatically load and save only the relevant values in human-readable format), so avoid deleting any dicts or values or setting anything to None in the defaults of `settings` or `settings["templates"]` unless you have subclassed PyGlops in a way that you know you don't need the values

### AI
* If you implement the KivyGlops on_process_ai method, you shouldn't move anything otherwise glitches will almost certainly occur. This is not a limitation of the engine--it is a recommendation to be logical, so that you ensure your visuals presented to the player make sense.
  * Things that you can safely do in on_process_ai include:
    * cause glop that is an actor to use items (via the use_item_at method of a glop)
    * set indices and strings that will be used to control the character, such as values at the following keys in glop's actor_dict: "moveto_index", "target_index" which refer to objects in the self.glops list
  * Things that are not so great but still work:
    * set a non-ai variable in an actor_dict (such as, modify health--which should probably be done in on_at_rest or attacked_glop_at)
  * NOTE: after on_process_ai is called, the `actor_dict["target_index"]` will be set to None if the item doesn't have any item where any of the item's uses are in attack_uses, unless you set `actor_dict["unarmed_melee_enable"] = True`

### Teaching using KivyGlops:
* update-kivyglops from LAN.bat will only work for students if teacher places KivyGlops in R:\Classes\ComputerProgramming\Examples\KivyGlops
(which can be done using deploy.bat, if the folder already exists and the teacher has write permissions to the folder; the students should have read permissions to the folder)
* if segfault occurs, maybe camera and look_at location are same

## Changes
(2018-01-17)
* added dereferences (see `mgp` and `sg` and others) to increase performance and help with PEP8 line length
* moved `settings['globals']['camera_perspective_number']`
* used continue when possible to decrease nesting indentation
* renamed `emit_debug_to_dict` to `debug_to`
* added get_thetas_vec3 function for where glop.look_at is too specific
* replaced rotation_multiplier_y with glop state's new key `state["look_dest_thetas"]` dimension lists, formerly `choice_try_theta_multipliers`; eliminated look_theta_multipliers
* renamed get_location to get_pos; added get_angles, set_pos and set_angles methods to make accessing info from instructions standard between implementations if PyGlop*
* renamed state's at_rest_enable to on_ground_enable for clarity, since could still be rolling even if True
* (moved append_wobject from incorrect location [PyGlops] to KivyGlop) fix issue where color not set by KivyGlop's override of append_wobject
(2018-01-16)
* broke movement, wait for next update
* moved most or all required defaults for PyGlop to settings global
  in pyglops.py (PyGlop normally uses settings determined there during
  _init_glop)
(2018-01-15)
* renamed get_nearest_vec3_on_vec3line_using_xz to get_nearest_vec3_and_distance_on_vec3line_using_xz and made return ((x,y,z), distance) instead of (x,y,z,distance)
* renamed constrain_pos_to_walkmesh to get_walk_info and made it not modify params, only return
* stopped using get_vec3_from_point in favor of swizzling Translate (via _t_ins.xyz)
* changed moving_x, moving_y, moving_z to choice_local_vel_mult list
* only use walkmesh when `m_glop.properties["clip_enable"]` is True
* moved __str__ from PyGlops to PyGlop and gave PyGlops its own
* added get_pos to PyGlop and KivyGlop
* pyglops.py: in copy_as_subclass, use different copy of ancestor list for each call to deepcopy_with_my_type
* renamed _translate_instruction to _t_ins, _rotate_instruction_* to _r_ins_*, _scale_instruction to _s_ins
* changed _world_grav_acceleration to `settings["world"]["gravity"]`,
  _default_fly_enable to `settings["templates"]["actor"]["fly_enable"]`,
  _camera_person_number to `settings["globals"]["camera_perspective_number"]` (and fixed the set_camera_mode method which was setting a local instead of member)
* changed glop's x_velocity, y_velocity, and z_velocity to `velocity` list
* kivyglops.py (KivyGlops update): replaced theta and moving_theta with choice_try_theta and choice_result_turn_theta which are also used more consistently
* fixed view pitch (was adding 90 degrees--should be radians if any--see `view_top =`
* renamed get_constrained_info_using_walkmeshes to get_walk_info
* changed choice-based movement from a movement modifier to a velocity modifier
* migrated hit radius, reach radius, eye height (each with underscores) to dicts
* moved defaults for actor_dict and properties to `settings["templates"]["actor"]` and `settings["templates"]["properties"]`)
* added `settings["fallback"]["actor"]["ranged_aquire_radius"]` (20.)
(2018-01-14)
* Changed resources license to CC0 to comply with changes to GitHub TOS (see <http://joeyh.name/blog/entry/what_I_would_ask_my_lawyers_about_the_new_Github_TOS/>)--and removed or remade any resources not compatible with CC0.
    * kivyforest-floor.png was remade from scratch in Krita
* kivyglops.py: Fixed major bug where constrain_glop_to_walkmesh was using z-up (_t_ins.z and pos[2] or mismatched pos index) in some cases
* kivyglops.py: put `self.on_update_glops()` back into correct scope
* kivyglops.py: repaired and unified at_rest event (whether bumpable hit bumper or any hit ground)--see the call to `self.on_bump` in update
* pyglops.py: add bumper_index to bumpable's in_range_indices if has projectile_dict, so target doesn't obtain item right away (see "ball games" in Usage section)
* renamed on_at_rest_at to `on_bump(self, glop_index, bumper_index_or_None)` (and eliminated `def bump_glop(self, bumpable_name, bumper_name)`)
* use walkmesh for every object
* improved reliability of deepcopy_with_my_type and use duck-typing
* add duck-typing methods _get_is_glop, get_is_glop, _get_is_glop_material, get_is_glop_material, get_class_name to relevant classes
(2018-01-13)
* use this_dict.get (returns None if missing)  instead of checks for key in a dict, when behavior should be same whether missing or None
* add inventory_index to item to know whether it is in a player's inventory, and don't delete owner or owner_index until projectile_dict is removed (when lands)
* reset glop.state (formerly glop.dat) by setting it to [] not {}
* replace `item_glop.item_dict["RUNTIME_last_used_time"]` with `item_dict["state"]["last_used_time"]`
* replace `item_dict["glop_index"]` with glop_index INSIDE `item_dict["state"]` which is a dict containing situational data.
* rename glop.dat to glop.state, and only use for situational data (see Usage section regarding use of state)
* rename `["tmp"]["glop"]` (for relationship in `glop.state["links"]` dict) to `["state"]["parent_glop"]` for clarity
* kivyglops.py (KivyGlops update): only make object stick to glop using `glop.state["links"]` NOT owner NOR owner_index
* now ONLY save "links" in child for consistency
* rename all index-getting methods to find_*: index_of_mesh to find_glop; common.py: get_index_by_name to find_by_name
  * the follwing remain same since gets actual sub-object not index:
    common.py: get_by_name; pyglops.py: get_mesh_by_name
  * the following remain the same because they get a saved index and don't perform a search:
    pyglops.py: get_player_glop_index
* renamed: getAngleBetweenPoints to get_angle_between_points, getMeshByName to get_mesh_by_name
* renamed overloadable scene event handlers: obtain_glop to _deprecated_on_obtain_glop_by_name (used in "Unit 2" lessons 5, 6 and 9), obtain_glop_at to on_obtain_glop
* return of get_index_lists_by_similar_names changed from list to dict where keys are same as partial_names param
* use `velocity[0] * got_frame_delay` properly (as opposed to `velocity[0]` alone) even if no floor
* ensure ai and hit detection are done before movement
* set state variables for choice-based movement, for ai and player the same way (instead of making local variables)
    * local attack_radius changed to `self.glops[bumper_index]["state"]["acquire_radius"]`
    * local attack_s changed to `self.glops[bumper_index]["state"]["desired_use"]`
    * local weapon_index changed to `self.glops[bumper_index]["state"]["desired_item_index"]`
    * local this_glop_free_enable eliminated (see *_glop.state["on_ground_enable"])
    * local stop_this_bumpable_enable eliminated (see *_glop.state["at_rest_event_enable"])
    * constrain to floor etc after that
* made flag where all uses containing "shoot_" use item's range instead of player's (affects "Unit 2" lessons 6, 7, and 8)
* instead of "inventory_index" selected_item_event now has "selected_index" and "fit_at" which is >=0 if fit into inventory (both are indices referring to `actor_dict["inventory_items"]` list); and in push_glop, slot `event["fit_at"]` is automatically selected if no slot (-1) was selected (select_item_event_dict is normally used only by after_selected_item; returned by push_glop_item, push_item, sel_next_inv_slot)
* renamed attacked_glop to on_attacked_glop (affects "Unit 2" lessons 7, 8, and 9)
* renamed remaining event handlers you can reimplement to start with `on_`: renamed load_glops to on_load_glops (affects all "Unit 2" lessons), update_glops to on_update_glops (affects "Unit 2" lesson 2), `display_explosion` to `on_explode_glop` (affects "Unit 2" lesson 8), `process_ai` to `on_process_ai` (affects "Unit 2" lesson 9)
* kivyglops.py: radically improved update method: fixed issues, unified decision-making variables for ai and player; unified physics for all glops
(2018-01-12)
* (was sending self.new_glop_method instead of self.new_material_method) fix KivyGlopMaterial not using copy_as_subclass correctly
* changed default projectile_speed (see also throw_speed) to 15 (was 1.0) for realism (works now, with since now physics is correct--second-based)--still no wind resistance, so things will go rather far
* added infinite recursion checking to copy_as_subclass & deepcopy_with_my_type (and fixed deepcopy_with_my_type)
* kivyglops.py: moved code using walkmesh from update to new method: constrain_glop_to_walkmesh
* changed boolean is_out_of_range to list in_range_indices which makes way more sense (bumpable gets one bump per bumper, and thrower can be added to list so bumper doesn't hit itself with the bumpable)
* pyglops.py: limited eye height to 86.5% of hitbox.maximums[1] in calculate_hit_range (so throwing looks better; see "Phi in the human body")
* pyglops.py: eliminated `fired_glop.name = str(fires_glop.name) + "." + str(projectile_dict["subscript"])` (was redundant since `fired_glop.name = "fired[" + str(self.fired_count) + "]"` was already used)
* pyglops.py: (PyGlops) combined throw types into single throw_glop method
* pyglops.py: changed usage of whether item drops on use from `["droppable"] = "no"` to `["drop_enable"] = False`
* pyglops.py: (PyGlop) added `has_item_with_any_use(uses)` method
* kivyglops.py: (KivyGlops update) fixed ai_enable case (weapon choosing, attacking only if target is glop, etc)
* pyglops.py: now required to use `item_dict["projectile_keys"]` to specify any keys (such as hit_damage) from item_dict which should be copied to projectile_dict while traveling
* pyglops.py: removes owner as should
(2018-01-11)
* pyglops.py: (move `is_out_of_range` from `_internal_bump_glop` to `_update` in kivyglops.py and set immediately after checked) fixed issue where is_out_of_range was only being set for items
* kivyglops.py, pyglops.py: (only bumper [not even bumpable] has or needs hitbox; hitbox is set to None by super calculate_hit_range so stays that way if no override, so check for bumpable_enable before calling calculate_hit_range from _on_change_s_ins; check for hitbox before using in apply_vertex_offset; check whether glop_index is usable during calculate_hit_range to make sure it is not used improperly) prevent using glop_index before assigned (since _on_change_s_ins happens during append_wobject via _on_change_pivot, before glop is bumpable)
* change copy.deepcopy to get_dict_deepcopy where possible for safety with wierd types and python2
* fix PyGlop deepcopy_with_my_type (pre-allocate list, use copy or '=', etc)
* reduced verbosity by checking get_verbose_enable() in more situations
* show glop_name of selected item on debug screen
* removed extra declaration of _run_command in PyGlops
* pyglops.py: removed redundant call to self._run_semicolon_separated_commands from _internal_bump_glop
* pyglops.py: (PyGlops) added missing spawn_pex_particles (calls self.ui.spawn_pex_particles)
* pyglops.py: (if as_projectile in item_dict used, set bump_enable to True--is set to false when obtained) make thrown items bumping work while traveling (airborne after thrown, etc)
* pyglops.py: put projectile_dict case before item_dict case in _internal_bump_glop so projectiles that are items work (such as thrown glop items with weapon_dict stored at as_projectile key in item_dict)
* common.py: now you can do `from common import *` then `set_verbose_enable(True)` for manipulating debug output manually (now False can stay as default during debugging)
* pyglops.py: now you can set `item_dict["droppable"]` to false for any item to be emitted (produces items which can't be picked up, so that inventory is not duplicated forever)
* pyglops.py: (now multiplies velocities [meters per second] by got_frame_delay [seconds] as should) make speed of objects more realistic
(2018-01-10)
* move `properties["inventory_items"]` to `actor_dict["inventory_items"]` (same for `"inventory_index"`)
* move `is_linked_as`, `get_link_as`, `get_link_and_type`, `push_glop_item`, `pop_glop_item` from KivyGlop to PyGlop
* made `projectile_dict` a deepcopy of `item_glop.item_dict["as_projectile"]` instead of a reference since `projectile_dict` contains flight-specific information
* changed `item["use"] = "*"` to `item["uses"] = ["*"]`  where * is a use for the item such as `throw_arc` or `melee`
* replaced `bump_sound_paths` with `properties["bump_sound_paths"]`
* created `add_damaged_sound_at` method for PyGlops scene (in properties so available to non-actors)
* (no longer inherits from Widget) workaround disturbing `'dict' is not callable` error in Kivy 1.9.0
* pyglops.py: (copy_as_subclass call in copy) fix potentially very bad bug -- `self.copy_as_subclass(self.new_glop_method, new_material_method)` had 3 params (not correct) 2nd one being another self.new_glop_method
* remove redundant call to _init_glop in KivyGlop __init__ (still calls it if super fails)
* improved monkey: added eyelids, UV mapped eyelids, improved texture for eyes and around eyes
* now uses _deferred_load_glops to load glops; to be more clear and functional, made separate load, loading, loaded booleans for *_glops_enable
* pyglops.py: _internal_bump_glop now plays random sound from bumper's `properties["damaged_sound_paths"]`
(2018-01-09)
* fresnel.glsl utilize per-object booleans
* renamed shade-kivyglops-minimal.glsl to kivyglops-testing.glsl
* added `use_parent_frag_modelview=True` to RenderContext constructor for KivyGlop
* made _multicontext_enable global (if false, glop gets InstructionGroup as canvas instead of RenderContext)
* renamed print_location to log_camera_info
* consolidated get_verbose_enable() to be in one file only (common.py)
* pyglops.py: removed uses of `Logger` to `print` to be framework-independent
* eliminated scene.log_camera_info(); created kivyglop.debug_to(dict); moved ui's camera_walk_units_per_second and camera_turn_radians_per_second to *_glop.actor_dict["land_units_per_second"] and "land_degrees_per_second" (player_glop in this case); changed their per_frame equivalents to local variables in kivyglops.update
* move `self.camera_walk_units_per_second = 12.0` to actor_dict
* move `self.camera_turn_radians_per_second = math.radians(90.0)` to actor_dict
* fixed issue where projectile sprites not visible (probably a refactoring bug)
(2018-01-03)
* fixed selection crash (issue caused by refactoring)
* added use_walkmesh_at method for using walkmesh when you know glop index
* renamed set_as_item_by_index to set_as_item_at; set_as_actor_by_index to set_as_actor_at; explode_glop_by_index to explode_glop_at; kill_glop_by_index to kill_glop_at; give_item_by_index_to_player_number to give_item_index_to_player_number; obtain_glop_by_index to obtain_glop_at; add_bump_sound_by_index to add_bump_sound_at; select_mesh_by_index to select_mesh_at
* changed `set_player_fly(self, fly_enable)` to `set_player_fly(self, player_number, fly_enable)`
(2018-01-02)
* changed `new_glop_method` to `new_material_method` in KivyGlopMaterial
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
* (2017-12-21) added copy constructors to PyGlops, PyGlopMaterial, and where appropriate, subclasses
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
* (2017-12-16) renamed create_mesh to new_glop_method for clarity, and use new_glop_method to create camera so conversion is not needed (eliminate get_kivyglop_from_pyglop)
        * rename get_pyglops_list_from_obj to get_glop_list_from_obj
        * rename get_pyglop_from_wobject to get_glop_from_wobject
* (2017-12-16) Changed recipe for game so that you subclass KivyGlops instead of KivyGlopsWindow (removes arbitrary border between ui and scene, and changes self.scene. to self. in projects which utilize KivyGlops)
* (2017-12-11) Began developing a platform-independent spec for the ui object so that PyGlops can specify more platform-independent methods (such as _internal_bump_glop) that push ui directly (ui being the platform-DEPENDENT object such as KivyGlopsWindow, which must inherit from some kind of OS Window or framework Window).
    * so far, ui must include:
        * potentially anything else in KivyGlopsWindow (KivyGlopsWindow is the only tested spec at this time, however see Developer Notes section of this file, which should be maintained well)
* (2017-12-11) _internal_bump_glop now calls the new _run_semicolon_separated_commands which calls the new _run_command method, so that these new methods are available to other methods
* (2017-12-11) give_item_by_keyword_to_player_number and give_item_index_to_player_number methods for manual item transfers without bumping or manually calling _internal_bump_glop
* (2017-12-11) moved projectile handling to _internal_bump_glop (formerly was directly after the _internal_bump_glop call)
* (2017-12-11) allow handling the obtain glop event by a new on_obtain_glop instead of _deprecated_on_obtain_glop_by_name in order to have access to the glop indices (you can still handle both if you desire for some reason, but be aware both will fire)
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
* add pathing for processing `actor_dict["target_pos"]` (even if not ai_enable, in case of strategy game where target_pos is set on a player-controlled glop)
* implement seperable_offsets for explosions
* eliminate foot_reach in favor of using hitbox
* did not test air-move or double-jump in on_update_glops
* eliminate look_target_glop in favor of a relationship in "links"
* upload updated version of lessons to website mentioned in Usage section (in the meantime see testing.py for updated code, or see Changes section for anything that says "renamed" or "required")
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
* see `context.add(this_glop._color_instruction)  # TODO: asdf add as uniform instead`
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
        def update_debug_label(self)  # sets debug screen text to content of debug_dict
* Subclass of KivyGlops must have:
    * a new_glop_method method which returns your subclass of PyGlop (NOT of PyGlops), unless you are handling the `super(MySubclassOfGlop, self).__init__(self.new_glop_method)` (where MySubclassOfGlop is your class) `self.new_glop_method param` in your subclass' `__init__` method another way.
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
* Subclasses of anything in pyglops.py should have a get_class_name method as part of duck-typing warnings in copy_* and get_*deepcopy* methods

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
* `[x]`, `[y]`, or `[z]` where should be `[0]`, `[1]`, or `[2]`
* using `y` + `eye_height` where should be from floor: `minimums[1]` + `eye_height`
* using degrees where should be radians (such as large numbers on line where angle is set)
* using the same ancestors to call deepcopy or copy_as_subclass multiple times when should slice to original length first (since deepcopying that would cause pickling error which deepcopy_with_my_type was created to avoid, and calling deepcopy_with_my_type would be a major performance and possibly recursion issue)--see copy_as_subclass for correct usage
* using `get _is _verbose()` (without spaces [spaces added so doesn't get replaced in README with replace in all open files]) where should be `get_verbose_enable()`
* using `/ self.ui.frames_per_second` for determining distance per frame, where should use `* got_frame_delay` (which is not only in seconds but is the actual frame delay)
* always use: in_range_indices on bumpable and not bumper, for consistency
* always do: hit detection & a.i. BEFORE movement/physics (& programmer-overridable events such as on_update_glops), for intuitiveness (the situation that the user sees on the screen is the situation on which AI is based [is what the AI sees], and on which results [such as hitting a platform] are based)
* checking for .rel or "rel" in child (should check for "links")
* checking for "links" in parent (should check in child)
* use of not (x in y) where x and y are anything--(doesn't cause bug, but more readable as) where should be x not in y
* use of not (x is y) where x and y are anything--(doesn't cause bug, but more readable as) where should be x is not y
* checking for key in this_dict when answer None is treated same as missing--(doesn't cause bug, but) this_dict.get(key) is python's solution)
* deleting stuff from _bumper_indices or _bumpable_indices while running the bump loop [see "  # can't delete until bump loop is done in update" (set to None instead--they will be cleaned up by update after the bump loop--see # endregion nested bump loop)
* calling push_glop_item or push_item without removing it from _bumpable_indices (IF "fit_enable" in return dict)
* `actor_dict["inventory_list"]` should be `actor_dict["inventory_items"]`
* make sure all attack uses are in PyGlops.settings["globals"]["attack_uses"] (for ai or other purposes)
* using fired_glop.item_dict in throw_glop where should instead use item_dict param (also, should create fired_glop.projectile_dict, and warn if already exists; projectile_dict is set to None on impact)
* calling a function and passing self as the first param (almost always wrong)
* using str(type(x)) where should be type(x).__name__
* result of builting type(x) function assumed to be string without using str(type(x)) where x is anything
* len used inside "[]" without "-1" (or "- 1" or other spacing)
* if you set `self.glops[index].properties["bump_enable"] = True` you should also do something like:
```python
self.glops[index].properties["bump_enable"] = True
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
