# Audit Changes Since 9d3b64f

Refactor the audit branch to match the current version.

Change the formatting of both branches to match.

(`x` = done changing in 9d3b64f)

## __init__.py (formerly kivyglops.py)
- [ ] an instance of `asdf` was removed for unknown reasons (usually asdf is panic afk programmer comment) after
  ```
                    new_glops = self.get_glop_list_from_obj(
                        source_path,
                        self.new_glop_method
                    )
```
- [x] add to KivyGlops:
```
        self.env_orig_rect = None
        self.env_rectangle = None
        self.env_flip_enable = False
```
- [x] move several KivyGlops variables from the class definition to `__init__`
- [ ] generate player 1 in KivyGlops `__init__`
- [x] remove gigantic catch-all try-except blocks in KivyGlops `__init__`
- [ ] `create_material` was moved or removed
- [x] `set_background_cylmap` got new keyword argument `unflip_enable`
- [x] `pivot_to_geometry_enable` changed to `pivot_to_g_enable`
- [x] `land_units_per_second` changed to `land_speed`
  - [ ] check whether other files use it
- [x] `get_container_walkmesh_and_poly_index_xz` changed to `get_walkmesh_info_xz`
- [x] `self.env_rectangle.texture.wrap` changed from `"repeat"` to `"mirrored_repeat"`
- [x] add `self.env_orig_rect`
- [x] change `desired_item_index` to `choice_ii` (different from `inventory_index`)
- [ ] add failsafe `doneGIs`
- [x] add `this_glop.state['glop_index'] = this_glop.glop_index` in `add_glop`
- [x] change `look_dest_thetas` to `dst_angles` in
  pcgs (player-controlled glop state)
- [ ] move frame timer? See `if self._fps_last_frame_tick is not None:` and other places
- [ ] make heavy changes to update (not done yet since determining if bugs are not in 9d3b64f is critical to the audit)

### KivyGlop
- [x] remove `get_hit_range_present`
- [ ] use `new_flag_f` from pyglops instead of .4444

## pyglops.py
- [ ] Change imports from * to specific imports
- [ ] Change `kEpsilon`
- [x] Change `world_friction_divisor` global setting to `cof`
- [x] Change hitbox from a class to a dict + functions
- [x] Change PyGlopMaterial to a dict (in pyglops.py)
- [x] remove `get_is_glop_hitbox` from PyGlop
- [x] remove `get_is_glop_material` from PyGlop
- [ ] Ensure uses are correct for `get_angles_vec3` (formerly `get_thetas_vec3`): The old version changed src_pos instead of result and used self._t_ins instead of src_pos (bugs apparently)!
- [ ] Ensure uses are changed from `get_nearest_vec3_and_distance_on_vec3line_using_xz` to `get_near_line_info_xz`
- [x] changed `owner_index` to `owner_key`
- [ ] Ensure uses are correct to account for change in PyGlop from:
  ```
    def copy_as_subclass(self, new_glop_method, new_material_method,
                         ref_my_verts_enable=False, ancestors=[],
                         depth=0):
```
  to
  ```
    def copy_as_subclass(self, new_glop_method,
                         ref_my_verts_enable=False, ancestors=[],
                         depth=0):
```

- [x] change `PyGlopsLight` to dict and functions

#### PyGlop
(Some notes above may refer to the PyGlop class as well.)
- [ ] Change heavily for PEP8 without audit:
  - `set_textures_from_wmaterial`
  - `append_wobject`

#### PyGlops
(Some notes above may refer to the PyGlops class as well.)
- [x] move several members from the class to `__init__`
- [x] add new keyword argument `class_name` to `_on_change_pivot`
- [x] add `a_glop.state['glop_index'] = index` to `set_as_actor_at`
- [x] set `self.glops[i].state['glop_index']` in set_as_item_at
- [x] set `fired_glop.state['glop_index']` in throw_glop
- [x] move `self._bumpable_indices.append(i)` from near end to near beginning of `set_as_item_at`
- [x] set `w_glop.glop_index` and `w_glop.state['glop_index']` in `add_actor_weapon`
- [ ] heavily edit `_internal_bump_glop` for PEP8
- [ ] heavily edit `use_item_at` for PEP8 (& check for cooldown, etc)

### Bugs in current version
- In `apply_vertex_offset`
  - [x] The shortened variable `phr` is assigned but `self.properties['hit_radius']` is not updated
  - [x] Change nonsensical code:
    ```
            phr = self.properties.get('hit_radius')
            if phr is None:
                hr = phr
            hr = 0.0  # use separate var to reduce dict access and if's
```
to
```
            phr = self.properties.get('hit_radius')
            hr = 0.0  # use separate var to reduce dict access and if's
            if phr is not None:
                hr = phr
```

### Bugs in old version
#### common.py
- [x] change `elif val_lower is True:` to `elif val is True:` in `is_true`

#### pyrealtimep.py
- [x] (warning) remove unecessary `from common import *`

### Bugs in both old and current version!
- [x] changed some instances of `'calling method'` to `'calling_method'` (was mixed)
- [x] remove incorrect comment `# NOTE: copy() works for PyGlopHitBox & more` before `this_copy = ov.copy()` in `deepcopy_with_my_type` since hitbox is a dict not an object in the current version.

## wobjfile.py
- [x] Copy over the current version over 9d3b64f without auditing.
