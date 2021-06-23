# Changelog
All notable changes to this project will be documented in this file.

This is the changelog for the staging branch (KivyGlops-audit-3a66898).

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

`*`: For things done in stable but not here nor master, see the stable changelog.

## [git] - 2021-06-23
### Added
- `*` comment: `#  stays false if inventory was full` after `sied['fit_enable'] = False` in pyglops.py.

### Changed
- `*` (done in staging) Improve the `is_in_triangle_coords` docstring.
- Change double to single quotes in several places to match the new style choice of staging and master branches.
- `*` Rename `get_owner_index` to `get_owner_key`.

### Fixed
- `*` (already correct in stable) Improve PEP8 in:
  - example-stadium.py
  - ishadereditor.py
  - pyrealtime.py
  - testing.py
- `*` (already correct in stable) Improve pathing in example-stadium.py.
- `*` (already correct in stable) Change `global look_at_none_warning_enable` to `look_at_pos_none_warning_enable` in one instance.
  - Both are real globals but one was used wrongly.
- `*` Initialize material in `KivyGlop` `__init__`.
- `*` Add missing `self.showNextHashWarning = True` in `KivyGlops`' `__init__`.
- `*` (only in staging) change `siedsied` to `sied` (There was one instance in pyglops.py).
- Improve use of PEP8 (Also make fixes in staging from stable and fixes listed below that weren't in either).
  - `*` (for ones only wrong in staging, see today's commit in staging).
  - `*` at `print("y:"+str(this_glop._t_ins.y))`
  - `*` at `print("not out of range yet")`
  - `*` at `print("did not bump`
  - `*` at `print("update_glsl...")` and line after that
  - `*` at `glwCv["_world_light_dir"]` and line after that
  - `*` at `self.scene.env_rectangle.size =` and after that `self.scene.env_rectangle.pos =` (comments)
  - `*` at `for i in range(len(self.scene.glops)):` and lines after that (comments)
  - `*` at `print("[ KivyGlopsWindow ] scene.camera_glop._r_ins_y.angle:` and line after that (comments)
  - `*` at `if "bumpable_name" in result:` and 3 lines after that and one before (comments).
  - `*` at `Process the item event so selected inventory slot`
  - `*` at `bump loop is done in update` (comment)
  - `*` at `if thisTextureFileName is not None:`
  - `*` at `target.projectile_dict =` in `copy_as_subclass`
  - `*` at `RenderContext(compute_normal_mat=True)`, `rotated in update_glsl`, `to hide` in testingkivy3d.py
  (comments)
  - `*` at `ok since adding it below` in wobjfile.py (comment)
  - `*` Move comments to docstring for `give_item_by_keyword_to_player_number`.
  - `*` Move comments to docstring for `give_item_index_to_player_number`.
  - `*` Move comments to docstring for `def CAMERA_*`.
  - `*` Move comments to docstring for `set_gravity`.
  - `*` wrap `give_item_by_keyword_to_player_number`, `give_item_index_to_player_number` to reduce line length.
  - `*` "aka" to "a.k.a." in ishadereditor.py
- `*` (already correct in stable) `....to_string()` where `str(...)` should be used because hitbox became a dict at `bumpable is not in bumper's hitbox`
- `*` (already correct in stable) `axes_index` to `axis_index`
- `*` (done in staging) `hide seem` to `hide seam`
