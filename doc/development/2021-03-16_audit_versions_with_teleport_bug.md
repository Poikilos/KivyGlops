# 2021-03-16 Audit Versions with the Teleport Bug

The audit process discovered that when physics was added, the player could no
longer move correctly at any commit after that.
- good: 3a66898
- bad: 9f43bc3

The solution is to make a new branch based on 3a66898 that is stable. That will be the default branch for now:
- use this branch: "stable" (new default, so `git clone https://github.com/poikilos/KivyGlops.git` will work)
  - formerly named "audit-3a66898-change-gradually"


## Tasks
- [ ] Add some debugging to movement such as for versions that don't move:
```
                # such as 'a'
                # such as 'd'
                # such as 's'
                # such as 'w'
                if get_verbose_enable():
                    print("[] * (verbose message) up")
```

For notes on various commits, see:
- [Physics is not working. The player sticks to a nearby object and can fly due to the interaction stopping physics. #2](https://github.com/poikilos/KivyGlops/issues/2)
- doc/development/2021-03-16_audit_changes_since_9d3b64f.md
  - However, 9d3b64f (2018-01-14) "working on geometry" has the teleport bug, so the document doesn't seem relevant to the issue.

The audit-3a66898 and audit-9f43bc3 branches are formatted to match master as much as possible for easy comparison.


## Changes to master
(made during audit)
- Catch specific exceptions (`TypeError: '<' not supported between instances of 'NoneType' and 'int'`) instead of silently failing in:
  - Added `if "NoneType" in str(ex):`:
    - pyglop in beginning of `on_vertex_format_change`
    - kivyglops in beginning of `generate_plane`
    - kivyglops in beginning of `generate_axes`
- Make PEP8 changes
  - put operator at the start of a continuation
  - move function documentation from hashtag comments to docstring
- Move article link from TODO to https://github.com/poikilos/KivyGlops/issues/11
- Copy issue from comments to https://github.com/poikilos/KivyGlops/issues/12


## Changes from 3a66898 to KivyGlops-audit (9f43bc3)
(3a66898: 2018-01-13 "working on use of items and projectiles"
vs 9f43bc3: 2018-01-14 "working on physics")
### Added
(PyGlop)
- add `out_of_hitbox_note_enable`
- `self.state['constrained_enable'] = False`
- `self.state['at_rest_enable'] = False`
- set eye_height, hit_radius, and reach_radius in `_init_glop`
- in `__init__` in `PyGlop` set:
  - `physics_enable`
  - `self.x_velocity`
  - `self.y_velocity`
  - `self.z_velocity`
- `on_at_rest_at` in `PyGlop`
- Renamed `obtain_glop` to `_deprecated_on_obtain_glop_by_name`
- Renamed `obtain_glop_at` to `on_obtain_glop`
- Renamed `'glop'` key to `'parent_glop'` (such as used in `get_link_as`)

### Changed
- PyGlop `dat` renamed to `state`
- Rename `getMeshByName` to `get_mesh_by_name`
- Heavily change `preprocess_item`, `use_item_at`
- Lightly change `set_as_item_at`
- Move some PyGlop members to `self.state`
- Slight changes that prevent 3-way diff with master using meld:
  - `_internal_bump_glop`
  - `set_as_actor_at`
- Set 'fit_at' key of returned event dict in `push_item`

### Removed
- remove `dat` from PyGlop


## Bugs in both 3a66898 and 9f43bc3
- [x] call `calculate_hit_range()` in `apply_translate` (if `self.get_has_hit_range()`)
- [x] when `copy_as_subclass` calls itself or calls `deepcopy_with_my_type`, send `ancestors=ancestors[:oa_len]` not `ancestors=ancestors`
- [x] Remove `append_wobject` where a copy of the one from `KivyGlop` is in `KivyGlops`:
  ```
    def append_wobject(self, this_wobject, pivot_to_g_enable=True):
        super(KivyGlop, self).append_wobject(this_wobject, pivot_to_g_enable=pivot_to_g_enable)
        if self.material is not None:
            self._color_instruction = Color(self.material['diffuse_color'][0], self.material['diffuse_color'][1], self.material['diffuse_color'][2], self.material['diffuse_color'][3])
        else:
            print("[ KivyGlops ] WARNING in append_wobject: self.material is None for " + str(self.name))

```
  - both are the same
  - both use `super(KivyGlop`
  - it should only be in `KivyGlop`
- `dummy_glop = KivyGlop()` should be `self.dummy_glop = KivyGlop()` in `__init__` in `KivyGlopsWindow`
- Only set ui in `PyGlops` `__init__` `if not hasattr(self, 'ui'):`
- An error in `add_actor_weapon` tries to display `projectile_dict` which doesn't exist and should be `item_dict`
- `==True` should be ` is True`
- [ ] `get_index_lists_by_similar_names` still differs and may be bugged. Create tests.

## Bugs in all 3!
- [x] change copy to deepcopy for ['hitbox'] in `copy_as_subclass` in `PyGlop`


## Refactor audit branches to match master
- [ ] Move many PyGlop/KivyGlop member variables to `properties`
- [ ] Change `PyGlopsLight` to a dict (doesn't seem to be used on old versions)
- [ ] Change `kEpsilon`
- [ ] add `get_has_hit_range` and use of it
  - [ ] Change `PyGlopHitBox` to a dict
- [x] Change `owner_index` to `owner_key`
- [ ] Change `isinstance` to `get_is_glop` where applicable (& add the method)
- [ ] eliminate `new_material_method` from uses and `copy_as_subclass`
- [ ] use `ancestors=ancestors[:orig_ancestors_len]` instead of `ancestors=ancestors` for recursion in `deepcopy_with_my_type`
- [ ] add `default_templates` keyword argument (and use of it) to `__init__` in `KivyGlop`
- [ ] add `class_name` keyword argument (and use of it) to `_on_change_pivot` in `PyGlop`
- [ ] Remove use of `new_material_method` param and `create_material` method
  - [x] Change `PyGlopsMaterial` and `KivyGlopsMaterial` to dicts
  - [ ] remove the 2nd sequential argument (`new_material_method`) from `copy_as_subclass`
- [ ] Use the `axes_index` parameter in `prepare_canvas`
  - [x] Add the `axes_index` keyword argument for `prepare_canvas`
- [ ] ensure `env_rectangle` uses are correct (but it may be failing since the environment texture is missing or has a different path)
- [ ] Add HUD and other large chunks of code to `update_glsl`
  ONE BY ONE to see when bug appears.
- AS SEPARATE COMMITS to see if bug appears:
  - uses of `moving_x` change and `choice_local_vel_mult[0]` is used instead
  - refactor `calculate_hit_range`
  - EACH CHANGE AS SEPARATE COMMITS to see if bug appears in heavy changes to `update`
- [ ] add uses of `nearest_not_found_warning_enable`
  - [x] add `nearest_not_found_warning_enable`
- [ ] comment `out_of_hitbox_note_enable`
- [ ] add uses of `tltf` and `tlt`
  - [x] add `tltf` and `tlt`
- [x] Change `set_textures_from_wmaterial` heavily
- [ ] Change `emit_yaml` heavily
- [ ] Change `_init_glop` heavily
  - Change initialization of glop to use:
    - [ ] default_templates['state']
    - [ ] default_templates['properties']
    - [ ] MAYBE THE BUG IS HERE: ensure deepcopy is used
- [ ] heavily change `copy_as_subclass`
- [ ] Change `x_velocity`, `z_velocity`, `z_velocity` (present in 9f43bc3 but not 3a66898) to a list/tuple in `state`
- [x] Add `get_has_hit_range` to `PyGlop`
- In `prepare_canvas` add:
  - sanity checks for hitbox
  - add `self._s_ins` to the context
- [x] Add `get_class_name` to `KivyGlop`
- [ ] refactor `push_glop_item`
- [ ] refactor `push_item`
- [x] Move several members from PyGlops class definition to `__init__`
  - [x] ensure `PyGlops.` is never used in either audit branch (It wasn't & isn't).
- [ ] Rename `land_units_per_second` to `land_speed`
- [ ] Implement uses of `PyGlop` `_append_to_list_property`
  - [x] Add `_append_to_list_property` to `PyGlop`
- Add to `PyGlops`:
  - [x] `on_bump`
  - [x] `on_bump_world`
- Add to `pyglops` module:
  - [x] `fequals`
  - [x] `match_fn_ci`
  - [x] `match_fn`
  - [x] `degrees_list`
  - [x] `get_angle_vec2`
- [ ] Use the global kEpsilon instead of redefining it elsewhere.
- [ ] Use `calling_method` *with underscore* instead of 'calling method' key consistently in the dict that `push_glop_item` returns.
- [ ] Improve `push_glop_item`

### Rename variables manually that are in doc/development/KivyGlops-modernize.py
- [x] several others not listed here
- [x] wholeWordChanges['select_next_inventory_slot'] = 'sel_next_inv_slot'
- [x] wholeWordChanges['walk_units_per_frame'] = 'lupf'
    # ^ walk_units_per_frame changed to land_units_per_frame from
    #   3a66898 to 9f43bc3
- [x] wholeWordChanges['land_units_per_frame'] = 'lupf'
- [x] wholeWordChanges['true_like_strings'] = 'truthies'
- [x] wholeWordChanges['set_true_like_strings'] = 'set_truthies'
- [x] wholeWordChanges['pivot_to_geometry_enable'] = 'pivot_to_g_enable'
- [ ] wholeWordChanges['bumper_index_index'] = 'bumper_i_i'
- [ ] wholeWordChanges['select_item_event_dict'] = 'sied'
- and:
```
    plainReplacements['self.material.new_material'] = "new_material"
    plainReplacements['glop.material.new_material'] = " new_material"
    plainReplacements['self.create_material'] = " new_material"
    plainReplacements['glop.create_material'] = " new_material"
    # ^ leave the space as a flag in case of issues
    #   (Remove the part before ' ' manually if present; the syntax
    #   error in that case will indicate the part is present)
    #   Remove the extra space though:
    plainReplacements['  new_material'] = " new_material"
    plainReplacements['\n new_material'] = "\nnew_material"
    plainReplacements['material.properties'] = "material['properties']"
    plainReplacements['material.ambient_color'] = "material['ambient_color']"
    plainReplacements['material.diffuse_color'] = "material['diffuse_color']"
    plainReplacements['material.specular_color'] = "material['specular_color']"
    plainReplacements['material.emissive_color'] = "material['emissive_color']"
    plainReplacements['material.specular_exponent'] = "material['specular_exponent']"
    plainReplacements['true_like_strings'] = 'truthies'
    plainReplacements['.hit_radius'] = ".properties['hit_radius']"
    plainReplacements['.hitbox'] = ".properties['hitbox']"
    plainReplacements[".minimums"] = "['minimums']"
    plainReplacements[".maximums"] = "['maximums']"
```

### Add functions to common.py
- [x] change_point_from_vec3
- [x] fixed_width
- [x] get_traceback
- [x] get_stepping
- [x] pstep
- [x] chatter
