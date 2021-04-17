#!/usr/bin/env python
import sys
import os
import re

try_path = os.path.join("..", "..")
modules = os.realpath(try_path)
if os.path.isdir(os.path.join(modules, "pycodetool"))
sys.path.append(modules)

from pycodetool.parsing import (
    assertEqual,
    assertAllEqual,
    # quoted_slices,
    # set_verbose,
    # get_quoted_slices_error,
    # which_slice,
    # END_BEFORE_QUOTE_ERR,
    # in_any_slice,
)

class MTTFile:
    verbosity = 2
    readonly = True

    def isLangIdentifier(self, s):
        '''
        This is calls s.isidentifier() (using Python identifier
        specifications) unless you override it.
        '''
        return s.isidentifier()

    def __init__(self, path, msg_prefix="    - ", tab_size=4,
                 msg_tab_size=4, lines=None):
        '''
        Sequential arguments:
        path -- This file will be loaded into memory immediately in text
                mode. Upon saving, the file will be saved here unless
                save_as is called instead.

        Keyword arguments:
        msg_prefix -- Display this before messages such as to make messages
                  appear under a specific branch in a tree structure on
                  the screen.
        tab_size -- This many spaces represent tabs when when converting
                    between space and tab indents in the file.
        msg_tab_size -- Display a tab character using this many spaces
                        within a message on the screen (doesn't affect
                        file view/load/save).
        lines -- If not None, don't touch the file yet, just use the
                 given lines.
        '''
        self.path = path
        self.changed = False
        self.lastChanges = 0
        self.msg_prefix = msg_prefix
        self.tab_size = tab_size
        self.msg_tab_size = msg_tab_size
        if lines is None:
            self.lines = []
            with open(path, 'r') as ins:
                for line in ins:
                    line = line.rstrip("\n\r")
                    self.lines.append(line)
        else:
            self.lines = lines
        print("{}loaded {} line(s)".format(msg_prefix, self.lines))

    def save_as(self, path, rename=False):
        if rename:
            shutil.move(self.path, path)
        self.path = path
        self.save()

    def save(self):
        if self.changed:
            if MTTFile.readonly:
                print("{}\"{}\" didn't save because the software is"
                      " using MTTFile in readonly mode"
                      "".format(self.msg_prefix, self.path))
                return
            with open(self.path, 'w') as outs:
                for line in lines:
                    outs.write(line + "\n")
                self.changed = False

    def generate_msg_indent(self):
        msg_tab_size = self.msg_tab_size
        tmp = self.msg_prefix.replace("\t", " "*msg_tab_size)
        return " " * len(tmp)

    def replace_all(self, old, new, identifier=False):
        self.lastChanges = 0
        if identifier:
            if not self.isLangIdentifier(old):
                raise ValueError("The identifier search was enabled but"
                                 " the old value \"{}\" is not an"
                                 " identifier.")
            if not self.isLangIdentifier(new):
                raise ValueError("The identifier search was enabled but"
                                 " the new value \"{}\" is not an"
                                 " identifier.")
        for i in range(len(self.lines)):
            row = i + 1
            line = self.lines[i]
            oldLine = line
            start = 0
            ll = len(line)
            ol = len(old)
            nl = len(new)
            changed = False
            col = 0
            msg_indent = self.generate_msg_indent()
            while start < ll:
                found = line.find(old, start)
                if found >= 0:
                    change = True
                    if identifier:
                        if self.is_identifier(line[found-1]):
                            change = False
                        elif self.is_identifier(line[found+ol]):
                            change = False
                    if change:
                        if col == 0:
                            col = found + 1
                        line = line[:found] + new + line[found+ol:]
                        changed = True
                        start = found + nl
                        self.lastChanges += 1
                else:
                    break
            if changed:
                if MTTFile.verbosity > 1:
                    print("{}  {}:{}:{}: `{}` became `{}`"
                          "".format(msg_indent, self.path, row, col,
                                    oldLine, line))
                self.lines[i] = line
                self.changed = True
            elif line != self.lines[i]:
                raise RuntimeError(
                    "{}  {}:{}:{}: `{}` became `{}` but wasn't marked"
                    " changed for saving"
                    "".format(msg_indent, self.path, row, col,
                              oldLine, line)
                )
        return self.lastChanges

    def replace_ends(self, oldFuzzyStr, newFuzzyStr):
        self.lastChanges = 0
        olds = oldFuzzyStr.split("*")
        news = newFuzzyStr.split("*")
        params_msg_d = {
            "basis for the search": olds,
            "new value": news,
        }
        params_msg_orig_d = {
            "basis for the search": oldFuzzyStr,
            "new value": newFuzzyStr,
        }
        for key, parts in params_msg_d.items():
            orig = params_msg_orig_d[key]
            if len(olds) != 2:
                raise ValueError("{}The {} in"
                                 " replace_ends mode must contain one"
                                 " and only one '*' but is \"{}\""
                                 "".format(self.msg_prefix, key, orig))
            for i in range(len(parts)):
                part = parts[i]
                if len(part) == 0:
                raise ValueError("{}The {} in"
                                 " replace_ends mode must have a"
                                 " character at each side of '*'"
                                 " but is \"{}\""
                                 "".format(self.msg_prefix, key, orig))

        for i in range(len(self.lines)):
            row = i + 1
            line = self.lines[i]
            oldLine = line
            start = 0
            ll = len(line)
            o0l = len(olds[0])
            n0l = len(news[0])
            o1l = len(olds[1])
            n1l = len(news[1])
            changed = False
            col = 0
            msg_indent = self.generate_msg_indent()
            while start < ll:
                o0i = line.find(olds[0], start)
                if o0i < 0:
                    break
                col = o0i + 1
                o1i = line.find(olds[1], start+o0l)
                if o1i < 0:
                    print("{} {}:{}:{}: WARNING: The line has a \"{}\""
                          " that doesn't close with \"{}\""
                          "".format(msg_indent, self.path, row, col,
                                    olds[0], olds[1]))
                    break

                line = line[:o0i] + news[0] + line[o0i+o0l:o1i] + news[1] + line[o1i+o1l:]
                changed = True
                self.lastChanges += 1
                start = o1i + n1l
            if changed:
                if MTTFile.verbosity > 1:
                    print("{}  {}:{}:{}: `{}` became `{}`"
                          "".format(msg_indent, self.path, row, col,
                                    oldLine, line))
                self.lines[i] = line
                self.changed = True
            elif line != self.lines[i]:
                raise RuntimeError(
                    "{}  {}:{}:{}: `{}` became `{}` but wasn't marked"
                    " changed for saving"
                    "".format(msg_indent, self.path, row, col,
                              oldLine, line)
                )
        return self.lastChanges

    def replace_all_regex(self, old, new, keep_ends=None):
        '''
        Sequential arguments:
        new -- Change old to this (See also keep_ends).

        Keyword arguments:
        keep_ends -- Keep this many characters on each end of
                     the match. It must be a 2-long iterable where the
                     first element is the count to keep at the start
                     and the second element is the count to keep at the
                     end. This is for matches such
                     as 's="hi"'. For example, to add spaces around
                     that but not remove the 's' nor '"' nor transform
                     "==" to "= =", set the regex to
                     r"[a-zA-Z0-9_\"'\]]{}[a-zA-Z0-9_\"'\]]" and set
                     keep_ends to (1, 1)
        '''
        self.lastChanges = 0
        for i in range(len(self.lines)):
            row = i + 1
            line = self.lines[i]
            oldLine = line
            start = 0
            ll = len(line)
            ol = len(old)
            nl = len(new)
            changed = False
            col = 0
            msg_indent = self.generate_msg_indent()
            start = 0
            buildLine = ""
            for m in re.finditer(old, line):
                change = True
                # m.group(0) is the 1st regex group
                groupI = 0
                groups = []
                while True:
                    try:
                        groups.append(m.group(groupI))
                        groupI += 1
                    except IndexError:
                        break
                if len(groups) > 0:
                    raise ValueError("Multiple groups is not supported"
                                     " by MTTFile replace_all_regex,"
                                     " but the regex \"{}\""
                                     " found {}".format(old, groups))
                chunk = line[m.start():m.end()]
                if keep_ends is not None:
                    chunk = chunk[
                else:
                    chunk = new
                buildLine += chunk


            '''
            while start < ll:
                found = line.find(old, start)
                if found >= 0:
                    change = True
                    if identifier:
                        if self.is_identifier(line[found-1]):
                            change = False
                        elif self.is_identifier(line[found+ol]):
                            change = False
                    if change:
                        if col == 0:
                            col = found + 1
                        line = line[:found] + new + line[found+ol:]
                        changed = True
                        start = found + nl
                        self.lastChanges += 1
                else:
                    break
            '''
            if changed:
                if MTTFile.verbosity > 1:
                    print("{}  {}:{}:{}: `{}` became `{}`"
                          "".format(msg_indent, self.path, row, col,
                                    oldLine, line))
                self.lines[i] = line
                self.changed = True
            elif line != self.lines[i]:
                raise RuntimeError(
                    "{}  {}:{}:{}: `{}` became `{}` but wasn't marked"
                    " changed for saving"
                    "".format(msg_indent, self.path, row, col,
                              oldLine, line)
                )
        return self.lastChanges


class MTTProject:
    def __init__(self, path, allowed_extensions, exclusions=None):
        self.path = path
        self.files = []
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
        print("[ModThatTextProject] using \"{}\" as project"
              "".format(path))
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
                        relDir = relDir.replace(os.sep, "/")
                    if (relDir != "") and (not relDir.startswith("/")):
                        raise RuntimeError("Exclusions will not work"
                                           " because relDir \"{}\""
                                           " does not start with '{}'"
                                           "".format(relDir,
                                                     os.sep))
                    if relDir == "":
                        relDir = "/"
                    exclusion = self.get_exclusion(relDir)
                    if exclusion is not None:
                        print("- (excluded by \"{}\") {}"
                              "".format(exclusion, relDir))
                    else:
                        print("- {} (in {})"
                              "".format(relDir, self.path))
                exclusion = self.get_exclusion(relDir)
                relPath = os.path.join(relDir, name)
                if exclusion is None:
                    exclusion = self.get_exclusion(relPath)
                if exclusion is not None:
                    print("  - (excluded by \"{}\") {}"
                          "".format(exclusion, name))
                    continue
                print("  - {}".format(name))
                sub = os.path.join(root, name)
                newFile = MTTFile(sub)
                self.files.append(newFile)
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
        fullPath = None
        if not relPath[:1] == "/":
            raise ValueError("relPath must start with '/' (to represent"
                             " the project root) but is \"{}\""
                             "".format(relPath))
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
            isAbsEx = False
            if exclusion.startswith("/"):
                isAbsEx = True
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

    def replace_all(self, old, new, identifier=False):
        count = 0
        for f in self.files:
            # print("* checking \"{}\"".format(f.path))
            count += f.replace_all(old, new, identifier=identifier)

    def replace_ends(self, old, new):
        count = 0
        for f in self.files:
            # print("* checking \"{}\"".format(f.path))
            count += f.replace_ends(old, new)
        return count

    def replace_all_regex(self, old, new, new_ends=None,
                          keep_ends=None):
        count = 0
        for f in self.files:
            # print("* checking \"{}\"".format(f.path))
            count += f.replace_all_regex(old, new, new_ends=new_ends,
                                         keep_ends=keep_ends)
        return count

    def save(self):
        for f in self.files:
            print("* saving \"{}\"".format(f.path))
            f.save()


def tests():
    lines = [
        'if (a =="a") and (b=="b"):',
        "if (c =='c') and (d=='d'):",
        "if (e == 'e'):",
        "if (f==6):",
        "if (f==f):",
        "if (g ==7):",
        "if (h == 8):",
        "i='i'",
        "j ='j'",
        "k = 'k'",
        "l >= 'l'",
        "m>='m'",
    ]
    goodLines = {
        '=': [
            'if (a =="a") and (b=="b"):',
            "if (c =='c') and (d=='d'):",
            "if (e == 'e'):",
            "if (f==6):",
            "if (f==f):",
            "if (g ==7):",
            "if (h == 8):",
            "i = 'i'",
            "j ='j'",
            "k = 'k'",
            "k >= 'k'",
            "k>='k'",
        ],
        '==': [
            'if (a =="a") and (b == "b"):',
            "if (c =='c') and (d == 'd'):",
            "if (e == 'e'):",
            "if (f == 6):",
            "if (f == f):",
            "if (g ==7):",
            "if (h == 8):",
            "i='i'",
            "j ='j'",
            "k = 'k'",
            "l >= 'm'",
            "m>='m'",
        ],
        '>=': [
            'if (a =="a") and (b=="b"):',
            "if (c =='c') and (d=='d'):",
            "if (e == 'e'):",
            "if (f==6):",
            "if (f==f):",
            "if (g ==7):",
            "if (h == 8):",
            "i='i'",
            "j ='j'",
            "k = 'k'",
            "l >= 'l'",
            "m >= 'm'",
        ],
    }
    keep_ends = (1, 1)  # 1,1: Keep the first and last character.
    for part, expectations in goodLines.items():
        f = MTTFile(None, lines=lines)
        count = f.replace_all_regex(
            # "[a-zA-Z0-9_\"'\\]]{}[a-zA-Z0-9_\"'\\]]".format(part),
            (r"[a-zA-Z0-9_\"'\]]{}[a-zA-Z0-9_\"'\]]"
             "".format(part, keep_ends=keep_ends)),
             # ^ r avoids all escape sequences except for the quote used
            " {} ".format(part),
            keep_ends=True,
        )
        for i in range(len(lines)):
            assertEqual(f.lines[i], expectations[i],
                        tbs="using \"{}\"".format(part))
    print("All tests passed.")


if __name__ == "__main__":
    tests()
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
        project.replace_all(k, v, identifier=True)
    project.replace_ends('["*"]', "['*']")
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
        project.replace_all(k, v, identifier=False)
    crunchedParts = [">=", "<=", "==", "!=", "<", ">"]
    keep_ends = (1, 1)  # 1,1: Keep the first and last character.
    for part in crunchedParts:
        # literal tested regex: [a-zA-Z0-9_"'\]]==[a-zA-Z0-9_"'\]]
        project.replace_all_regex(
            # "[a-zA-Z0-9_\"'\\]]{}[a-zA-Z0-9_\"'\\]]".format(part),
            (r"[a-zA-Z0-9_\"'\]]{}[a-zA-Z0-9_\"'\]]"
             "".format(part, new_ends=new_ends, keep_ends=keep_ends)),
             # ^ r avoids all escape sequences except for the quote used
            ' {} '.format(part),
            keep_ends=True,
        )
    project.save()
