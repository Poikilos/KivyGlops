#!/usr/bin/env python
import os


class MTTProject:
    def __init__(self, path, allowed_extensions, exclusions=None):
        self.path = path
        if exclusions is None:
            exclusions = []
        giPath = os.path.join(path, ".gitignore")
        if os.path.isfile(giPath):
            print("* Adding exclusions from \"{}\"".format(giPath))
            with open(giPath, 'r') as ins:
                for rawLine in ins:
                    line = rawLine.strip()
                    # Inline comments are consideres comments by git
                    # itself, so only check the first character:
                    if line.startswith("#"):
                        continue
                    if "*" in line:
                        print("WARNING: '*' is not implemented"
                              " ({}) contained the line \"{}\""
                              "".format(giPath, rawLine.rstrip()))
                        # such as `*.py`
                        continue
                    if "[" in line:
                        print("WARNING: '[' is not implemented"
                              " ({}) contained the line \"{}\""
                              "".format(giPath, rawLine.rstrip()))
                        # such as `*.py[cod]`
                        continue
                    if "!" in line:
                        print("WARNING: '!' is not implemented"
                              " ({}) contained the line \"{}\""
                              "".format(giPath, rawLine))
                        continue
                    if "#" in line:
                        print("WARNING: '#' is not implemented"
                              " ({}) contained the line \"{}\""
                              "".format(giPath, rawLine))
                        continue
                    exclusions.append(line)


        self.exclusions = exclusions
        print("[ModThatTextProject] Using \"{}\"".format(path))
        self.paths = []
        prev_root = None
        lowerExts = []
        for dotExt in allowed_extensions:
            if not dotExt.startswith("."):
                raise ValueError("Start extensions with dot to be"
                                 " pythonic (as per splitext)")
            de = dotExt.lower()
            if dotExt !=  de:
                print("WARNING: Extensions are case insensive and you"
                      " used capitals. They will be matched regardless"
                      " of case.")
            lowerExts.append(de)
        relDir = None
        for root, dirs, files in os.walk(self.path, topdown=False):
            for name in files:
                if name.startswith("."):
                    continue
                if os.path.splitext(name)[-1] not in lowerExts:
                    continue
                if root != prev_root:
                    if not root.startswith(self.path):
                        raise RuntimeError("\"{}\" doesn't start with"
                                           " \"{}\""
                                           "".format(root, self.path))
                    prev_root = root
                    relDir = root[len(self.path):]
                    if os.sep != "/":
                        relDir.replace(os.sep, "/")
                    if (relDir != "") and (not relDir.startswith("/")):
                        raise RuntimeError("Exclusions will not work"
                                           " because relDir \"{}\""
                                           " does not start with '{}'"
                                           "".format(relDir,
                                                     os.sep))
                    exclusion = self.get_exclusion(relDir)
                    if exclusion is not None:
                        print("  - (excluded by \"{}\") {}"
                              "".format(exclusion, relDir))
                    else:
                        print("  - {} (in {})"
                              "".format(relDir, self.path))
                exclusion = self.get_exclusion(relDir)
                relPath = os.path.join(relDir, name)
                if exclusion is None:
                    exclusion = self.get_exclusion(relPath)
                if exclusion is not None:
                    print("    - (excluded by \"{}\") {}"
                          "".format(exclusion, name))
                    continue
                print("    - {}".format(name))
                sub = os.path.join(root, name)
            # for name in dirs:
            #     if name.startswith("."):
            #         continue
            #     print(os.path.join(root, name))

    def get_exclusion(self, relPath):
        '''
        Check whether a relative path is excluded using self.exclusions
        the same way git would.

        Sequential arguments:
        relPath -- The path or file to check. It must start with a
                   slash, where everything before the slash would be the
                   project or repository directory.
        '''
        if not relPath[:1] == "/":
            raise ValueError("relPath must start with '/' but is"
                             " \"{}\"".format(relPath))
        fullPath = os.path.join(self.path, relPath[1:])
        # ^ :1 to skip leading slash, otherwise join gives relPath only!
        if not os.path.exists(fullPath):
            raise ValueError("relPath \"{}\" must be in the project"
                             " (\"{}\") but does not exist (as \"{}\")"
                             "".format(relPath, self.path, fullPath))
        if "\\" in relPath:
            raise RuntimeError("Backslashes are not handled here."
                               " If and only if os.sep is '\\',"
                               " The program should replace them"
                               " before calling excluded.")
        for exclusion in self.exclusions:
            if exclusion == "/":
                raise ValueError("You excluded the whole project with"
                                 " '/'")
            isDirEx = False
            # ^ is directory exclusion (as opposed to file exclusion)
            if exclusion.endswith("/"):
                isDirEx = True
                exclusion = exclusion[:-1]

            if not exclusion.startswith("/"):
                # Any part can match, not just relDir as a whole.
                if "/" in exclusion:
                    raise ValueError("If a git-style exclusion doesn't"
                                     " start with a slash (\"{}\"),"
                                     " it should not contain a slash"
                                     " at all except for at the end to"
                                     " denote a directory."
                                     "".format(exclusion))
                parts = relPath[1:].split("/")
                # ^ start at 1 to avoid leading slash
                for i in range(len(parts)):
                    part = parts[i]
                    if part == exclusion:
                        exRel = os.path.join(*parts[:i])
                        # ^ Use splat ('*') since join takes multiple
                        #   params not a list.
                        # ^ Only go to :i since that is the one that
                        #   matched in this sub-loop!
                        exPath = os.path.join(self.path, exRel)
                        print("   (excluded rel \"{}\""
                              "".format(exRel))
                        print("   abs \"{}\"):"
                              "".format(exPath))
                        return exclusion
            elif relPath.startswith(exclusion):
                if relPath == exclusion:
                    return exclusion
                elif relPath[len(exclusion)] == "/":
                    if relPath[:len(exclusion)] == exclusion:
                        return exclusion
        return None

    def replace_all(self, old, new, word=False):
        for path in self.paths:
            print("* checking \"{}\"".format(path))

    def replace_all_ends(self, old, new):
        for path in self.paths:
            pass
            # print("* checking \"{}\"".format(path))

    def replace_all_regex(self, old, new, keep_ends=False):
        for path in self.paths:
            pass
            # print("* checking \"{}\"".format(path))

if __name__ == "__main__":
    exclusions = [
        "/doc/",
        "/etc/",
        "kivyglopsexampleblank.py",
    ]
    project = MTTProject(os.getcwd(), [".py"], exclusions=exclusions)
    wholeWordChanges = {}
    wholeWordChanges['show_next_no_mesh_warning_enable'] = 'no_mesh_warning_enable'
    wholeWordChanges['_rotate_instruction_x'] = '_r_ins_x'
    wholeWordChanges['_rotate_instruction_y'] = '_r_ins_y'
    wholeWordChanges['_rotate_instruction_z'] = '_r_ins_z'
    wholeWordChanges['_translate_instruction'] = '_t_ins'
    wholeWordChanges['_scale_instruction'] = '_s_ins'
    wholeWordChanges['_on_change_scale_instruction'] = '_on_change_s_ins'

    wholeWordChanges['emit_debug_to_dict'] = 'debug_to'
    wholeWordChanges['new_glop'] = 'new_glop_method'
    wholeWordChanges['dat'] = 'state'
    # ^ wobjfile standard_emit_yaml has a dat param but changing that
    #   won't matter.
    wholeWordChanges['get_angle_between_points'] = 'get_angle_vec2'
    wholeWordChanges['PointSegmentDistanceSquared'] = 'get_nearest_vec3_on_vec3line_using_xz'
    # ^ PointSegmentDistanceSquared changed to
    #   get_nearest_vec3_on_vec3line_using_xz early on (before 3a66898)
    # wholeWordChanges['get_nearest_vec3_on_vec3line_using_xz'] = 'get_near_line_info_xz'
    # ^ Don't do this! The function is different, so keep it in old versions for now
    #   and add the new function manually.
    wholeWordChanges['pt'] = 'pos'
    # ^ for PointInTriangle
    wholeWordChanges[' expertmm'] = ' Poikilos'
    wholeWordChanges['copy_verts_by_ref_enable'] = 'ref_my_verts_enable'
    wholeWordChanges['copy_my_type_by_reference_enable'] = 'ref_my_type_enable'
    wholeWordChanges['ancestor_list'] = 'ancestors'
    wholeWordChanges['process_ai'] = 'on_process_ai'
    wholeWordChanges['owner_index'] = 'owner_key'
    wholeWordChanges['select_next_inventory_slot'] = 'sel_next_inv_slot'

    wholeWordChanges['walk_units_per_frame'] = 'lupf'
    # ^ walk_units_per_frame changed to land_units_per_frame from
    #   3a66898 to 9f43bc3
    wholeWordChanges['land_units_per_frame'] = 'lupf'
    wholeWordChanges['get_index_by_name'] = 'find_by_name'
    # wholeWordChanges['true_like_strings'] = 'truthies'
    # wholeWordChanges['set_true_like_strings'] = 'set_truthies'
    # ^ See plainReplacements below instead.
    wholeWordChanges['pivot_to_geometry_enable'] = 'pivot_to_g_enable'
    wholeWordChanges['bumper_index_index'] = 'bumper_i_i'
    # wholeWordChanges['select_item_event_dict'] = 'sied'
    # TODO: ^ except when used as an argument def or argument
    wholeWordChanges['axisIndex'] = 'axI' # was a_i in master in one loop, and axisIndex in 2 other loops
    wholeWordChanges['killed_glop'] = 'on_killed_glop'
    wholeWordChanges['attacked_glop'] = 'on_attacked_glop'
    wholeWordChanges['obtain_glop_at'] = 'on_obtain_glop'

    for k, v in wholeWordChanges.items():
        project.replace_all(k, v, word=True)
    project.replace_all_ends('["*"]', "['*']")
    plainReplacements = {}
    plainReplacements['expertmm'] = 'poikilos'
    plainReplacements[' depth=0, skip_my_type_enable=False, ancestors=[]'] = '\n                              ancestors=[], depth=0,\n                              skip_my_type_enable=False'
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
    for k, v in plainReplacements.items():
        project.replace_all(k, v, word=False)
    crunchedParts = [">=", "<=", "==", "!=", "<", ">"]
    for part in crunchedParts:
        # literal tested regex: [a-zA-Z0-9_"'\]]==[a-zA-Z0-9_"'\]]
        project.replace_all_regex(
            "[a-zA-Z0-9_\"'\\]]{}[a-zA-Z0-9_\"'\\]]".format(part),
            ' == ',
            keep_ends=True,
        )
