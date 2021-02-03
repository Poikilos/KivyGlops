# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).


## [git] - 2021-02-03
### Changed
- Rename `get_wmaterial_dict_from_mtl` to `fetch_wmaterial`.


## [git] - 2018-07-31
### Removed
- removed PyGlopLight in favor of dict and `*_light` functions


## [git] - 2018-07-30
### Removed
- Remove PyGlopHitBox in favor of dict and `*_hitbox` functions.
- Remove PyGlopMaterial in favor of dict and `*_material` functions.
- Deprecate `get_is_glop_hitbox` `_get_is_glop_hitbox` `contains_vec3`
  `get_is_glop_material` `_get_is_glop_material` `new_material_method`.


## [git] - 2018-01-27
### Fixed
- Properly distinguish between bumpable and bumper during
  `motivated_index` loop (see `if mgs['at_rest_event_enable']:`), and
  only call `_internal_bump_glop` if both are present (as opposed to a
  bumper bumping the world).

### Removed
- some useless commented code
- redundant rolling code that was missing an important radius precheck
  and use _[:edit: ? I didn't finish this sentence]_


## [git] - 2018-01-21
### Fixed
- (kivyglops.py KivyGlops set_background_cylmap) changed texture_wrap
  for world cylmap from 'repeat' to 'mirrored_repeat' to better
  simulate cylindrical mapping


## [git] - 2018-01-19
### Changed
- Rename `land_units_per_second` to `land_speed`


## [git] - 2018-01-18
### Fixed
- (see get_look_angles_from_2d; was using x_rad for y angle as should
  but was getting -18 instead of -180 when turning left) turn left
  should turn as far as right using mouse
- PEP8 line length, and related early returns (for decreased
  indentation), pre-dereferencing, and pre-calculation optimizations


## [git] - 2018-01-17
### Fixed
- Work on physics and movement. It is probably still broken--wait for
  an update. Rename choice vars as `choice_local*` and `choice_world*`
  since getting mixed up between local and world coords was the main
  bug; eliminate `choice_world_move_theta` since (to make momentum
  work) current `_r_ins_y.angle` should be used (aka `mgas[1]`).

### Added
- Add dereferences (see `mgp` and `sg` and others) to increase
  performance and help with PEP8 line length
- Add `get_angles_vec3` function for where glop.look_at is too specific.

### Changed
- Move `settings['globals']['camera_perspective_number']`.
- Use continue when possible to decrease nesting indentation.
- Rename `emit_debug_to_dict` to `debug_to`.
- Replaced `rotation_multiplier_y` with glop state's new key
  `state['dst_angles']` dimension lists, formerly `choice_try_theta`
  formerly `choice_try_theta_multipliers`; eliminated
  `look_theta_multipliers`.
- Rename get_location to get_pos; added get_angles, set_pos and
  set_angles methods to make accessing info from instructions standard
  between implementations if `PyGlop*`
- Rename state's `at_rest_enable` to `on_ground_enable` for clarity,
  since could still be rolling even if `True`.
- Move append_wobject from incorrect location [PyGlops] to KivyGlop) fix
  issue where color not set by KivyGlop's override of `append_wobject`.


## [git] - 2018-01-16
(Movement is broken: Wait for a future update.)
- Move most or all required defaults for PyGlop to settings global
  in pyglops.py (PyGlop normally uses settings determined there during
  `_init_glop`)


## [git] - 2018-01-15
### Added
- Add `get_pos` to PyGlop and KivyGlop.
- Add `settings["fallback"]['actor']["ranged_aquire_radius"]` (20.).

### Changed
- Rename `get_nearest_vec3_on_vec3line_using_xz` to
  `get_near_line_info_xz` and made return ((x,y,z), distance) instead of
  (x,y,z,distance).
- Rename `constrain_pos_to_walkmesh` to `get_walk_info` and made it not
  modify params, only return.
- Stop using `get_vec3_from_point` in favor of swizzling Translate (via
  `_t_ins.xyz`)
- Change `moving_x`, `moving_y`, `moving_z` to `choice_local_vel_mult`
  list.
- Only use walkmesh when `m_glop.properties['clip_enable']` is `True`.
- Move `__str__` from PyGlops to PyGlop and gave PyGlops its own.
- Rename `_translate_instruction` to `_t_ins`, `_rotate_instruction_*`
  to `_r_ins_*`, `_scale_instruction` to `_s_ins`.
- Change `_world_grav_acceleration` to `settings['world']['gravity']`,
  `_default_fly_enable` to
  `settings['templates']['actor']['fly_enable']`,
  `_camera_person_number` to
  `settings['globals']['camera_perspective_number']` (See also [1] under
  "Fixed").
- Change glop's `x_velocity`, `y_velocity`, and `z_velocity` to
  `velocity` list.
- Rename `get_constrained_info_using_walkmeshes` to `get_walk_info`.
- Change choice-based movement from a movement modifier to a velocity
  modifier.
- Migrate hit radius, reach radius, eye height (each with underscores)
  to dicts.
- Move defaults for `actor_dict` and properties to
  `settings['templates']['actor']` and
  `settings['templates']['properties']`).

### Fixed
- (pyglops.py) In `copy_as_subclass`, use different copy of the ancestor
  list for each call to `deepcopy_with_my_type`.
- kivyglops.py (KivyGlops update): replaced `theta` and `moving_theta`
  with `choice_try_theta` and `choice_world_turn_theta`.
  - Use them more consistently.
- Fix view pitch (was adding 90 degrees--should be radians if any--see
  `view_top =`.
- [1] Fix the `set_camera_mode` method which was setting a local instead of
  member.


## [git] - 2018-01-14
### Changed
- Change resources license to CC0 to comply with changes to GitHub TOS
  (See
  <http://joeyh.name/blog/entry/what_I_would_ask_my_lawyers_about_the_new_Github_TOS/>)
  --and removed or remade any resources not compatible with CC0.
  - Remake kivyforest-floor.png was from scratch in Krita.
- (pyglops.py) Add `bumper_index` to bumpable's `in_range_indices` if it
  has a projectile_dict, so that the target doesn't obtain item right
  away (see "ball games" in "Usage" section of readme).
- Rename `on_at_rest_at` to
  `on_bump(self, glop_index, bumper_index_or_None)` (and eliminate
  `def bump_glop(self, egn, rgn)`)

### Fixed
- (kivyglops.py) Fix major bug where constrain_glop_to_walkmesh was
  using z-up (_t_ins.z and pos[2] or mismatched pos index) in some
  cases.
- (kivyglops.py) Put `self.on_update_glops()` back into correct scope.
- (kivyglops.py) Repair and unify at_rest event (whether bumpable hit
  bumper or any hit ground)--see the call to `self.on_bump` in update.
- Use the walkmesh for every object.
- Improved the reliability of `deepcopy_with_my_type` and use
  duck-typing.
- Add duck-typing methods `_get_is_glop`, `get_is_glop`,
  `_get_is_glop_material`, `get_is_glop_material`, `get_class_name` to
  relevant classes.


## [git] - 2018-01-13
- use this_dict.get (returns None if missing)  instead of checks for key in a dict, when behavior should be same whether missing or None
- add inventory_index to item to know whether it is in a player's inventory, and don't delete owner or owner_key until projectile_dict is removed (when lands)
- reset glop.state (formerly glop.dat) by setting it to [] not {}
- replace `item_glop.item_dict["RUNTIME_last_used_time"]` with `item_dict['state']['last_used_time']`
- replace `item_dict['glop_index']` with glop_index INSIDE `item_dict['state']` which is a dict containing situational data.
- rename glop.dat to glop.state, and only use for situational data (see Usage section regarding use of state)
- rename `["tmp"]['glop']` (for relationship in `glop.state['links']` dict) to `['state']['parent_glop']` for clarity
- kivyglops.py (KivyGlops update): only make object stick to glop using `glop.state['links']` NOT owner NOR owner_key
- now ONLY save 'links' in child for consistency
- rename all index-getting methods to find_*: index_of_mesh to find_glop; common.py: get_index_by_name to find_by_name
  - the follwing remain same since gets actual sub-object not index:
    common.py: get_by_name; pyglops.py: get_mesh_by_name
  - the following remain the same because they get a saved index and don't perform a search:
    pyglops.py: get_player_glop_index
- renamed: getAngleBetweenPoints to get_angle_between_points, getMeshByName to get_mesh_by_name
- renamed overloadable scene event handlers: obtain_glop to _deprecated_on_obtain_glop_by_name (used in "Unit 2" lessons 5, 6 and 9), obtain_glop_at to on_obtain_glop
- return of get_index_lists_by_similar_names changed from list to dict where keys are same as partial_names param
- use `velocity[0] * got_frame_delay` properly (as opposed to `velocity[0]` alone) even if no floor
- ensure ai and hit detection are done before movement
- set state variables for choice-based movement, for ai and player the same way (instead of making local variables)
  - local attack_radius changed to `self.glops[bumper_index]['state']['acquire_radius']`
  - local attack_s changed to `self.glops[bumper_index]['state']['desired_use']`
  - local weapon_index changed to `self.glops[bumper_index]['state']['choice_ii']`
  - local this_glop_free_enable eliminated (see `*_glop.state['on_ground_enable']`)
  - local stop_this_bumpable_enable eliminated (see `*_glop.state['at_rest_event_enable']`)
  - constrain to floor etc after that
- made flag where all uses containing `shoot_` use item's range instead of player's (affects "Unit 2" lessons 6, 7, and 8)
- instead of 'inventory_index' selected_item_event now has 'selected_index' and 'fit_at' which is >=0 if fit into inventory (both are indices referring to `actor_dict['inventory_items']` list); and in push_glop, slot `event['fit_at']` is automatically selected if no slot (-1) was selected (select_item_event_dict is normally used only by after_selected_item; returned by push_glop_item, push_item, sel_next_inv_slot)
- renamed attacked_glop to on_attacked_glop (affects "Unit 2" lessons 7, 8, and 9)
- renamed remaining event handlers you can reimplement to start with `on_`: renamed load_glops to on_load_glops (affects all "Unit 2" lessons), update_glops to on_update_glops (affects "Unit 2" lesson 2), `display_explosion` to `on_explode_glop` (affects "Unit 2" lesson 8), `process_ai` to `on_process_ai` (affects "Unit 2" lesson 9)
- kivyglops.py: radically improved update method: fixed issues, unified decision-making variables for ai and player; unified physics for all glops


## [git] - 2018-01-12
- (was sending self.new_glop_method instead of self.new_material_method) fix KivyGlopMaterial not using copy_as_subclass correctly
- changed default projectile_speed (see also throw_speed) to 15 (was 1.0) for realism (works now, with since now physics is correct--second-based)--still no wind resistance, so things will go rather far
- added infinite recursion checking to copy_as_subclass & deepcopy_with_my_type (and fixed deepcopy_with_my_type)
- kivyglops.py: moved code using walkmesh from update to new method: constrain_glop_to_walkmesh
- changed boolean is_out_of_range to list in_range_indices which makes way more sense (bumpable gets one bump per bumper, and thrower can be added to list so bumper doesn't hit itself with the bumpable)
- pyglops.py: limited eye height to 86.5% of hitbox['maximums'][1] in calculate_hit_range (so throwing looks better; see "Phi in the human body")
- pyglops.py: eliminated `fired_glop.name = str(fires_glop.name) + "." + str(projectile_dict["subscript"])` (was redundant since `fired_glop.name = "fired[" + str(self.fired_count) + "]"` was already used)
- pyglops.py: (PyGlops) combined throw types into single throw_glop method
- pyglops.py: changed usage of whether item drops on use from `['droppable'] = "no"` to `['drop_enable'] = False`
- pyglops.py: (PyGlop) added `has_item_with_any_use(uses)` method
- kivyglops.py: (KivyGlops update) fixed ai_enable case (weapon choosing, attacking only if target is glop, etc)
- pyglops.py: now required to use `item_dict['projectile_keys']` to specify any keys (such as hit_damage) from item_dict which should be copied to projectile_dict while traveling
- pyglops.py: removes owner as should


## [git] - 2018-01-11
- pyglops.py: (move `is_out_of_range` from `_internal_bump_glop` to `_update` in kivyglops.py and set immediately after checked) fixed issue where is_out_of_range was only being set for items
- kivyglops.py, pyglops.py: (only bumper [not even bumpable] has or needs hitbox; hitbox is set to None by super calculate_hit_range so stays that way if no override, so check for bumpable_enable before calling calculate_hit_range from _on_change_s_ins; check for hitbox before using in apply_vertex_offset; check whether glop_index is usable during calculate_hit_range to make sure it is not used improperly) prevent using glop_index before assigned (since _on_change_s_ins happens during append_wobject via _on_change_pivot, before glop is bumpable)
- change copy.deepcopy to get_dict_deepcopy where possible for safety with wierd types and python2
- fix PyGlop deepcopy_with_my_type (pre-allocate list, use copy or '=', etc)
- reduced verbosity by checking get_verbose_enable() in more situations
- show glop_name of selected item on debug screen
- removed extra declaration of _run_command in PyGlops
- pyglops.py: removed redundant call to self._run_semicolon_separated_commands from _internal_bump_glop
- pyglops.py: (PyGlops) added missing spawn_pex_particles (calls self.ui.spawn_pex_particles)
- pyglops.py: (if as_projectile in item_dict used, set bump_enable to True--is set to false when obtained) make thrown items bumping work while traveling (airborne after thrown, etc)
- pyglops.py: put projectile_dict case before item_dict case in _internal_bump_glop so projectiles that are items work (such as thrown glop items with weapon_dict stored at as_projectile key in item_dict)
- common.py: now you can do `from common import *` then `set_verbose_enable(True)` for manipulating debug output manually (now False can stay as default during debugging)
- pyglops.py: now you can set `item_dict['droppable']` to false for any item to be emitted (produces items which can't be picked up, so that inventory is not duplicated forever)
- pyglops.py: (now multiplies velocities [meters per second] by got_frame_delay [seconds] as should) make speed of objects more realistic


## [git] - 2018-01-10
- move `properties['inventory_items']` to `actor_dict['inventory_items']` (same for `'inventory_index'`)
- move `is_linked_as`, `get_link_as`, `get_link_and_type`, `push_glop_item`, `pop_glop_item` from KivyGlop to PyGlop
- made `projectile_dict` a deepcopy of `item_glop.item_dict['as_projectile']` instead of a reference since `projectile_dict` contains flight-specific information
- changed `item['use'] = "*"` to `item['uses'] = ["*"]`  where `*` is a use for the item such as `throw_arc` or `melee`
- replaced `bump_sound_paths` with `properties['bump_sound_paths']`
- created `add_damaged_sound_at` method for PyGlops scene (in properties so available to non-actors)
- (no longer inherits from Widget) workaround disturbing `'dict' is not callable` error in Kivy 1.9.0
- pyglops.py: (copy_as_subclass call in copy) fix potentially very bad bug -- `self.copy_as_subclass(self.new_glop_method, new_material_method)` had 3 params (not correct) 2nd one being another self.new_glop_method
- remove redundant call to _init_glop in KivyGlop __init__ (still calls it if super fails)
- improved monkey: added eyelids, UV mapped eyelids, improved texture for eyes and around eyes
- now uses `_deferred_load_glops` to load glops; to be more clear and functional, made separate load, loading, loaded booleans for `*_glops_enable`
- pyglops.py: `_internal_bump_glop` now plays random sound from bumper's `properties['damaged_sound_paths']`


## [git] - 2018-01-09
- fresnel.glsl utilize per-object booleans
- renamed shade-kivyglops-minimal.glsl to kivyglops-testing.glsl
- added `use_parent_frag_modelview=True` to RenderContext constructor for KivyGlop
- made `_multicontext_enable` global (if false, glop gets InstructionGroup as canvas instead of RenderContext)
- renamed `print_location` to `log_camera_info`
- consolidated get_verbose_enable() to be in one file only (common.py)
- pyglops.py: removed uses of `Logger` to `print` to be framework-independent
- eliminate scene.log_camera_info()
  - create kivyglop.debug_to(dict);
  - move ui's camera_walk_units_per_second and
    `camera_turn_radians_per_second` to
    `*_glop.actor_dict['land_speed']` and `land_degrees_per_second`
    (player_glop in this case); changed their per_frame equivalents to
    local variables in kivyglops.update
- move `self.camera_walk_units_per_second = 12.0` to actor_dict
- move `self.camera_turn_radians_per_second = math.radians(90.0)` to actor_dict
- fixed issue where projectile sprites not visible (probably a refactoring bug)


## [git] - 2018-01-03
- fixed selection crash (issue caused by refactoring)
- added use_walkmesh_at method for using walkmesh when you know glop index
- renamed set_as_item_by_index to set_as_item_at; set_as_actor_by_index to set_as_actor_at; explode_glop_by_index to explode_glop_at; kill_glop_by_index to kill_glop_at; give_item_by_index_to_player_number to give_item_index_to_player_number; obtain_glop_by_index to obtain_glop_at; add_bump_sound_by_index to add_bump_sound_at; select_mesh_by_index to select_mesh_at
- changed `set_player_fly(self, fly_enable)` to `set_player_fly(self, player_number, fly_enable)`


## [git] - 2018-01-02
- changed `new_glop_method` to `new_material_method` in KivyGlopMaterial


## [git] - 2018-01-01
- changed KivyGlop canvas to default type instead of InstructionGroup
  - commented `self.canvas = InstructionGroup` in KivyGlop `__init__`
  - changed uses of texture0_enable to use canvas as dict
  - changed init to set it to RenderContext
  - kivyglops.py (KivyGlop) changed init to manually call `_init_glop`
    after `__init__` since with multiple inheritance, super only calls
    first inherited object (first type in parenthesis on `class` line);
    - Rename PyGlop `__init__` to `_init_glop`
    - Change order of inheritance to `Widget, PyGlop`


## [git] - 2017-12-28
- added optional set_visible_enable param to add_glop (and made default not set visible to True)
- moved glop canvas editing from KivyGlops.add_glop to KivyGlop.prepare_canvas
- renamed `_meshes` to `_contexts` for clarity (but `_meshes` is used other places as an actual list of Mesh objects)


## [git] - 2017-12-27
- transitioned from material classes to material dict--see "wmaterial dict spec" subheading under "Developer Notes" (since dict can just be interpreted later; and so 100% of data can be loaded even if mtl file doesn't follow spec)
- In mtl loader, renamed `args_string`, `args` & `param` to `options_string`, `options` & `option` for clarity, since mtl spec calls the chunks following the command values: option if starts with hyphen, args if follow option, and values if is part of statement (or command) [1]
- eliminated numerical indices for objects in WObjFile object (changed self.wobjects from list to dict), and name property of WObject
- renamed set_textures_from_mtl_dict to set_textures_from_wmaterial
- fully implemented face grouping from complete OBJ spec including multiple groups (`g` with no param means "default" group, and no `g` at all means "default" group)
- ishadereditor.py: made it use KivyGlops; renamed viewer to gl_widget


## [git] - 2017-12-26
- fixed issue where cooldown last used time wasn't set before item was first used (now is ready upon first time ever added to an inventory)
- started implementing "carry" and dict-ify KivyGlops savable members ("tmp" dict member should not be saved)


## [git] - 2017-12-22
- get_indices_by_source_path now checks against original_path (as passed to load_obj; non-normalized) in addition to processed path
- renamed is_possible to fit_enable
- refactored global get_glop_from_wobject into `*Glop append_wobject` to assist with overriding, and with expandability (in case multi submesh glops are needed later)


## [git] - 2017-12-21
- renamed get_dict_deepcopy_except_my_type to deepcopy_with_my_type and made it work for either list or dict (and should work for any subclass since checks for type(self), so was eliminated from subclass)
- renamed bump_sounds to bump_sound_paths for clarity
- added copy constructors to PyGlops, PyGlopMaterial, and where appropriate, subclasses
- Change `Color(Color(1.0, 1.0, 1.0, 1.0))` to
  `Color(1.0, 1.0, 1.0, 1.0)`.
- Rename `*append_dump` to `*emit_yaml`.
- changed emit_yaml methods since an object shouldn't need to know its
  own context to save (for example, should be allowable to have data
  members directly indented under line equal to "-")
- (fixed issue introduced by refactoring) translate instruction should
  be copied by value not reference for glop
- separated `player_glop` from `camera_glop` (see PyGlops `__init__`)
  and keys now move player instead of camera (if most recent param sent
  to self.set_camera_person was self.CAMERA_FIRST_PERSON(), which is
  done by default)
- fix issue where add_actor_weapon uses player_glop instead of the glop
  referenced by the glop_index param (bug was exposed by camera_glop and
  player_glop being separated)
- split `rotate_view_relative` into `rotate_camera_relative` and
  `rotate_player_relative`; moved them to KivyGlops since they use Kivy
  OpenGL instructions; renamed rotate_view_relative_around_point to
  rotate_relative_around_point and forces you to specify a glop as first
  parameter (still needs to be edited in major way to rotate around the
  point instead of assuming things about the object)


## [git] - 2017-12-20
### Changed
- Rename kivyglopsminimal.py to etc/kivyglops-mini-deprecated.py
- Update kivyglopstesting.py to account for refactoring
- Change to more permissive license (See
  [license.txt](license.txt))


## [git] - 2017-12-19
- added ability to load non-standard obj file using commands without
  params
  - Leave WObject name as None if not specified
  - Add ability to load non-standard object signaling (AND naming) in
    obj file AFTER useless g command, (such as, name WObject
    `some_name` if has `# object some_name then useless comments` on
    any line before data but after line with just `g` or `o` command
    but only if no name follows those commands).
- Store vertex_group_type in WObject (for future implementation).
- Standardize `emit_yaml` methods (and use `standard_emit_yaml` when
  necessary) for consistent yaml and consistent coding: (list, tab, name
  [, data | self]).
- wobjfile.py: always use face groups, to accomodate face groups feature
  of OBJ spec [1]; added more fault-tolerance to by creating vertex list
  whenever first vertex of a list is declared, and creating face groups
  whenever first face of a list is declared
- wobjfile.py: elimintated smoothing_group in favor of
  this_face_group_type and this_face_group_name (this_face_group_type
  's' is a smoothing group)


## [git] - 2017-12-17
- `frames_per_second` moved from KivyGlops to KivyGlops window since it
  is implementation-specific (and so KivyGlops instance doesn't need to
  exist during KivyGlopsWindow constructor).


## [git] - 2017-12-16
- Changed recipe for game so that you subclass KivyGlops instead of
  KivyGlopsWindow (removes arbitrary border between ui and scene, and
  changes self.scene. to self. in projects which utilize KivyGlops)
- renamed create_mesh to new_glop_method for clarity, and use
  new_glop_method to create camera so conversion is not needed
  (eliminate get_kivyglop_from_pyglop)
  - rename get_pyglops_list_from_obj to get_glop_list_from_obj
  - rename get_pyglop_from_wobject to get_glop_from_wobject
- complete shift of most methods from KivyGlopsWindow to PyGlops, or at
  least KivyGlops if kivy-specific; same for lines from init; same for
  lines from update_glsl (moved to new PyGlops `update` method)


## [git] - 2017-12-11
- allow handling the obtain glop event by a new on_obtain_glop instead
  of `_deprecated_on_obtain_glop_by_name` in order to have access to the
  glop indices (you can still handle both if you desire for some
  reason, but be aware both will fire)
- moved projectile handling to `_internal_bump_glop` (formerly was
  directly after the `_internal_bump_glop` call)
- give_item_by_keyword_to_player_number and
  give_item_index_to_player_number methods for manual item transfers
  without bumping or manually calling _internal_bump_glop
- `_internal_bump_glop` now calls the new
  `_run_semicolon_separated_commands` which calls the new `_run_command`
  method, so that these new methods are available to other methods
- Began developing a platform-independent spec for the ui object so that
  PyGlops can specify more platform-independent methods (such as
  `_internal_bump_glop`) that push ui directly (ui being the
  platform-DEPENDENT object such as KivyGlopsWindow, which must inherit
  from some kind of OS Window or framework Window).
  - so far, ui must include:
    - potentially anything else in KivyGlopsWindow (KivyGlopsWindow is
      the only tested spec at this time, however see Developer Notes
      section of this file, which should be maintained well)


## [git] - 2017-11-06
- Your KivyGlopsWindow implementation can now select mesh by name:
  self.select_mesh_by_name("some_named_mesh") (or filename but shows
  warning in stdout: self.select_mesh_by_name("somefilename") or
  self.select_mesh_by_name("somefilename.obj"))


## [git] - 2016-04-29
- Switch to using only graphics that are public domain
  (change license of modified resources to CC-BY-SA 4.0)
  - Remove graphics based on cinder block wall from
    photoshoptextures.com due to a quirky custom license.


## [git] - 2016-02-12
- Change the PyGlops ObjFile and objfile.py to WObjFile and wobjfile.py
  (to avoid naming conflict with ObjFile and objfile.py in Kivy
  examples).


## [git] - 2016-02-04
- Rename `*MesherMesh` types to `*Glop` to avoid confusion with
  (Kivy's) Mesh type which is stored in `*o3d._mesh`.
- Finish separating (native) PyGlop from (Wavefront(R)) WObject for many
  reasons including: avoid storing redundant data; keep track of what
  format of data is stored in list members; allow storage of strict obj
  format; allow conversion back&forth or to other formats being sure of
  what o3d contains.


## [git] - 2016-01-10
- Created new classes to hold the data from newobj and newmtl files, in
  order to keep strict obj+mtl data, separately from native
  OpenGL-style class.


## [git] - 2015-05-12
- Include a modified testnurbs file (with added textures and improved
  geometry)
  - Remove orion.


## [git] - 2015-04-15
### Changed
- Change `Material_orion.png` to `Material_orion` in orion.obj and
  orion.mtl to avoid confusion (It is a material object name, not a
  filename).
- For clarity and less dependence on OBJ format, refactor
  `object.vertices` to `object._vertex_strings`, and refactor
  `object.mesh.vertices` to `object.vertices`.

### Fixed
- Add a line to orion.obj: `mtllib orion.mtl`


## [git] - 2015-04-13
### Fixed
- No longer crash on missing textures.
- Make the pyramid in testnurbs-textured.obj into a true solid (It had
  0-sized triangles on bottom edges that had one face)
  - Simplify it manually.
  - Make sides equilateral from side view.


## [git] - 2015-04-10
### Added
- Implement the mtl loader from "kivy-rotation3d".


## [git] - 2015-04-08
### Added
- Redo the project starting from "kivy-trackball-python3".

### Removed
- all code from before this commit


## [git] - 2015-04-06

### Changed
- Run 2to3 (originally based on nskrypnik's kivy-rotation3d), which only
  had to change objloader (changes raise to function notation, and
  `map(a,b)` to `map(list(a,b))`).

### Fixed
- Change `vertex_format` tuples from `string,int,string` to
  `bytestring,int,string` (Since strings are not bytestrings by default
  in Python 3).
