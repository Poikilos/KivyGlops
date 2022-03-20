#!/usr/bin/env python
"""
This submodule provides simple dependency-free access to OBJ files and
certain 3D math operations.

The class WObjFile most accurately represents the obj
file format. Indices start at 0 but are saved starting at 1.
WObjFile contains a list of WObjects. Each WObject has only the
material it needs from the mtl file.
"""
__author__ = 'Jake Gustafson'

import os
import sys  # exception etc
import math
import traceback
import uuid


# from common import view_traceback
# from common import get_by_name
from kivyglops.common import (
    get_yaml_from_literal_value,
    view_traceback,
    # get_by_name,
)

tab_string = "  "

# These are necessary since in Python 3 int is no longer bounded:
MIN_INDEX = -9223372036854775807
MAX_INDEX = 9223372036854775808


'''
def get_int_list(values):
    results=list()
    for i in range(0,len(values)):
        results.append(int(values[i]))
    return results


def get_float_list(values):
    results=list()
    for i in range(0,len(values)):
        results.append(float(values[i]))
    return results
'''


def get_fvec2(values, start_index=0):
    return (float(values[start_index]),
            float(values[start_index+1]))


def get_fvec3(values, start_index=0):
    return (float(values[start_index]),
            float(values[start_index+1]),
            float(values[start_index+2]))

'''
def get_fvec4(values,start_index=0):
    result = None
    if len(values)-start_index>=4:
        result = (float(values[start_index]),
                  float(values[start_index+1]),
                  float(values[start_index+2]),
                  float(values[start_index+3]))
    else:
        result = (float(values[start_index]),
                  float(values[start_index+1]),
                  float(values[start_index+2]), 1.0)
    return result
'''


def get_fvec6(values, start_index=0):
    return (float(values[start_index]),
            float(values[start_index+1]),
            float(values[start_index+2]),
            float(values[start_index+3]),
            float(values[start_index+4]),
            float(values[start_index+5]))


def get_fvec7(values, start_index=0):
    return (float(values[start_index]),
            float(values[start_index+1]),
            float(values[start_index+2]),
            float(values[start_index+3]),
            float(values[start_index+4]),
            float(values[start_index+5]),
            float(values[start_index+6]))


class WIlluminationModel:
    '''
    Illumination models (as per OBJ format standard):
    0. Color on and Ambient off
    1. Color on and Ambient on [binary:0001]
    2. Highlight on [binary:0010]
    3. Reflection on and Ray trace on [binary:0011]
    4. Transparency: Glass on, Reflection: Ray trace on [binary:0100]
    5. Reflection: Fresnel on and Ray trace on [binary:0101]
    6. Transparency: Refraction on, Reflection: Fresnel off and Ray
       trace on [binary:0110]
    7. Transparency: Refraction on, Reflection: Fresnel on and Ray trace
       on [binary:0111]
    8. Reflection on and Ray trace off [binary:1000]
    9. Transparency: Glass on, Reflection: Ray trace off [binary:1001]
    10. Casts shadows onto invisible surfaces [binary:1010]
    '''
    number = None
    is_color = None
    is_ambient = None
    is_highlight = None
    is_reflection = None
    is_transparency = None
    is_transparency_glass = None
    is_transparency_refraction = None
    is_transparency_raytrace = None
    is_reflection_fresnel = None
    is_reflection_raytrace = None
    is_shadow_cast_onto_invisible_surfaces = None

    def __init__(self, number):
        self.set_from_illumination_model_number(number)

    def set_from_illumination_model_number(self, number):
        result = True
        self.number = number
        # ^ changed to None below if invalid
        if number == 0:
            self.is_color = True
            self.is_ambient = False
        elif number == 1:
            self.is_color = True
            self.is_ambient = True
        elif number == 2:
            self.is_highlight = True
        elif number == 3:
            self.is_reflection = True
        elif number == 4:
            self.is_transparency = True
            self.is_transparency_glass = True
            self.is_reflection = True
            self.is_reflection_raytrace = True
        elif number == 5:
            self.is_reflection = True
            self.is_reflection_fresnel = True
            self.is_reflection_raytrace = True
        elif number == 6:
            self.is_transparency = True
            self.is_transparency_refraction = True
            self.is_reflection = True
            self.is_reflection_fresnel = False
            self.is_reflection_raytrace = True
        elif number == 7:
            self.is_transparency = True
            self.is_transparency_refraction = True
            self.is_reflection = True
            self.is_reflection_fresnel = True
            self.is_reflection_raytrace = True
        elif number == 8:
            self.is_reflection = True
            self.is_reflection_raytrace = False
        elif number == 9:
            self.is_transparency = True
            self.is_transparency_glass = True
            self.is_reflection = True
            self.is_reflection_raytrace = False
        elif number == 10:
            self.is_shadow_cast_onto_invisible_surfaces = True
        else:
            result = False
            self.number = None
        return result


class WColorArgInfo:
    '''
    This is not for unique data. It is just a spec (use sub dict in
    material dict instead)
    '''

    _param = None
    _value_min_count = None
    _value_max_count = None
    _description = None
    _value_descriptions = None

    def __init__(self, param, description, value_min_count,
                 value_max_count, value_descriptions):
        self._param = param
        self._description = description
        self._value_min_count = value_min_count
        self._value_max_count = value_max_count


# http://paulbourke.net/dataformats/mtl/ says:
# To specify the ambient reflectivity of the current material, you can
# use the "Ka" statement, the "Ka spectral" statement, or the "Ka xyz"
# statement. Tip These statements are mutually exclusive.
color_arg_type_strings = list()
color_arg_type_strings.append(WColorArgInfo(
    "type",
    "type",
    1,
    1,
    ["type, such as type of reflection"]
))
color_arg_type_strings.append(WColorArgInfo(
    "spectral",
    "spectral curve",
    1,
    2,
    ["filename", "factor"]
))
color_arg_type_strings.append(WColorArgInfo(
    "xyz",
    "specifies that the values are in CIEXYZ colorspace",
    3,
    3,
    ["X as in CIEXYZ", "Y as in CIEXYZ", "Z as in CIEXYZ"]
))
color_arg_type_strings.append(WColorArgInfo(
    "blendu",
    "blend U in map",
    1,
    1,
    ["on|off"]
))
color_arg_type_strings.append(WColorArgInfo(
    "blendv",
    "blend V in map",
    1,
    1,
    ["on|off"]
))
color_arg_type_strings.append(WColorArgInfo(
    "clamp",
    "clamp to 0-1 in UV range",
    1,
    1,
    ["on|off"]
))
color_arg_type_strings.append(WColorArgInfo(
    "cc",
    "color correction (only for map_Ka, map_Kd, and map_Ks)",
    1,
    1,
    ["on|off"]
))
color_arg_type_strings.append(WColorArgInfo(
    "mm",
    "base gain",
    2,
    2,
    [("black level|white level (processed before black level, so acts"
      " as range)")]
))
color_arg_type_strings.append(WColorArgInfo(
    "t",
    "turbulence (post-processes tiled textures to hide seem)",
    2,
    3,
    ["u", "v", "w"]
))
color_arg_type_strings.append(WColorArgInfo(
    "texres",
    ("resizes texture before using, such as for NPOT textures; if used,"
     " image is forced to a square"),
    2,
    3,
    ["pixel count"]
))


# see also override in pyglops.py and kivyglops.py; formerly dumpAsYAMLArray
def standard_emit_yaml(lines, min_tab_string, dat):
    emit_yaml_or_None = getattr(dat, "emit_yaml", None)  # never throws if has 3rd param
    if callable(emit_yaml_or_None):
        dat.emit_yaml(lines, min_tab_string)
    elif isinstance(dat, list):
        for key in range(0, len(dat)):
            if isinstance(dat[key], list) or isinstance(dat[key], dict):
                lines.append(min_tab_string + "-")
                standard_emit_yaml(lines, min_tab_string+tab_string, dat[key])
            else:
                lines.append(min_tab_string+"- "+get_yaml_from_literal_value(dat[key]))
    elif isinstance(dat, dict):
        for key in dat:
            if isinstance(dat[key], list) or isinstance(dat[key], dict):
                lines.append(min_tab_string + key + ":")
                standard_emit_yaml(lines, min_tab_string+tab_string, dat[key])
            else:
                lines.append(min_tab_string+key+": "+get_yaml_from_literal_value(dat[key]))
    else:
        # print("WARNING in standard_emit_yaml: type '" + type(dat)
        #       + "' was not implemented and so was converted by plain"
        #       " str function")
        lines.append(min_tab_string+get_yaml_from_literal_value(dat))


class WObject:

    def __init__(self, name=None):
        self.source_path = None
        self.parameter_space_vertices = None
        # ^ only for curves--not really implemented, just loaded from
        # obj
        self.mtl_filename = None
        self.material_name = None
        self.vertices = None  # v
        self.texcoords = None
        # ^ vt (uv point in texture where each coord is from 0.0 to
        # 1.0); aka vertex_uvs
        self.normals = None  # vn
        self.face_groups = None
        # ^ is a dict where key is face group name, and value is list of
        # indices, where each index refers to a list of faces in
        # face_lists; f; vertex#/texcoord#/normal# were *# is a counting
        # number starting at 0 (BUT saved as 1)-- only vertex# is
        # required (but // is used if texcoord# is not present but
        # normal# is).
        self.face_dicts = None
        # ^ dict of dicts where key is smoothing group number or a UUID
        # and each value is a dict that has "s" ("on" or "off" or None)
        # and 'faces' (list of faces, where each face is a vertex index
        # list)
        self.wmaterial = None
        self.name = None
        self.has_any_data_enable = None
        self.polylines = None  # l; followed by vertex indices
        self._opening_comments = None

        self.name = name
        self.has_any_data_enable = False

    def preComment(self, text):
        if self._opening_comments is None:
            self._opening_comments = list()
        self._opening_comments.append(text)

    def emit_yaml(self, lines, min_tab_string):
        if self.source_path is not None:
            lines.append(min_tab_string+"source_path: "+self.source_path)
        lines.append(min_tab_string+"vertices:")
        standard_emit_yaml(lines, min_tab_string+tab_string, self.vertices)
        lines.append(min_tab_string+"texcoords:")
        standard_emit_yaml(lines, min_tab_string+tab_string, self.texcoords)
        lines.append(min_tab_string+"normals:")
        standard_emit_yaml(lines, min_tab_string+tab_string, self.normals)
        lines.append(min_tab_string+"_vertex_strings:")
        standard_emit_yaml(lines, min_tab_string+tab_string, self._vertex_strings)
        lines.append(min_tab_string+"parameter_space_vertices:")
        standard_emit_yaml(lines, min_tab_string+tab_string, self.parameter_space_vertices)
        lines.append(min_tab_string+"face_groups:")
        for key in self.face_groups:
            lines.append(min_tab_string+tab_string+key+":")
            standard_emit_yaml(lines, min_tab_string+tab_string+tab_string, self.face_groups[key])
        lines.append(min_tab_string+"face_dicts:")
        for key in self.face_dicts:
            lines.append(min_tab_string+tab_string+key+":")
            standard_emit_yaml(lines, min_tab_string+tab_string+tab_string, self.face_dicts[key])

    def _get_unused_face_list_key(self):
        # key = None
        # while True:
        #     key = "untitled_face_list_" + str(self.untitled_number)
        #     self.untitled_number += 1
        #     if this_o_name not in self.wobjects:
        #         break
        # return key

        return str(uuid.uuid4())


TP_REFR_ON_STR = "Transparency: Refraction on"
ILLUMINATIONMODEL_DESCRIPTION_STRINGS = [
    "Color on and Ambient off",
    "Color on and Ambient on",
    "Highlight on",
    "Reflection on and Ray trace on",
    "Transparency: Glass on, Reflection: Ray trace on",
    "Reflection: Fresnel on and Ray trace on",
    TP_REFR_ON_STR + ", Reflection: Fresnel off and Ray trace on",
    TP_REFR_ON_STR + ", Reflection: Fresnel on and Ray trace on",
    "Reflection on and Ray trace off",
    "Transparency: Glass on, Reflection: Ray trace off",
    "Casts shadows onto invisible surfaces"
]


def get_illumination_model_description(illuminationModelIndex):
    # global ILLUMINATIONMODEL_DESCRIPTION_STRINGS
    resultString = None
    if ((illuminationModelIndex >= 0)
            and (illuminationModelIndex < len(ILLUMINATIONMODEL_DESCRIPTION_STRINGS))):
        ILLUMINATIONMODEL_DESCRIPTION_STRINGS[illuminationModelIndex]
    return resultString


def fetch_wmaterial(filename):
    '''
    Get a wmaterial dict from an mtl file.
    '''
    wmaterials = None
    # try:
    if not os.path.exists(filename):
        print("ERROR in fetch_wmaterial: missing file or cannot access '"+filename+"'")
        return None
    wmaterials = {}
    comments = None  # list added as materials['#'] when done
    lineN = 0  # += 1 is done below before use
    m_name = None
    with open(filename, 'r') as ins:
        for line in ins.readlines():
            lineN += 1
            line_strip = line.strip()
            while ("\t" in line_strip):
                line_strip = line_strip.replace("\t", " ")
            while ("  " in line_strip):
                line_strip = line_strip.replace("  ", " ")
            if len(line_strip) < 1:
                continue
            elif line_strip[0] == "#":
                comment_notag = line_strip[1:].strip()
                if len(comment_notag) > 0:
                    if m_name is not None:
                        if wmaterials[m_name] is not None:
                            if "#" not in wmaterials[m_name]:
                                wmaterials[m_name]["#"] = []
                            wmaterials[m_name]['#'].append(
                                comment_notag
                            )
                        else:
                            if comments is None:
                                comments = []
                            comments.append(comment_notag)
                    else:
                        if comments is None:
                            comments = []
                        comments.append(comment_notag)
                continue

            space_index = line_strip.find(" ")
            if space_index < 0:
                print("{} ({},0): (INPUT ERROR)"
                      " no space after command"
                      "".format(filename, lineN))
                continue
            chunks_string = ""
            if len(line_strip) >= (space_index+1):
                # Prevent an out of range exception if
                # nothing is after the space.
                chunks_string = line_strip[space_index+1:].strip()
            if len(chunks_string) < 1:
                print("{} ({},0): (INPUT ERROR)"
                      " no arguments after command"
                      "".format(filename, lineN))
                continue

            command = line_strip[:space_index].strip()

            if (m_name is None) and (command != "newmtl"):
                print("{} ({},0): (INPUT ERROR)"
                      " material command before 'newmtl'"
                      "".format(filename, lineN))
                continue

            badspace = "\t"
            badspace_index = chunks_string.find(badspace)
            while badspace_index > -1:
                chunks_string = chunks_string.replace(badspace, " ")
                badspace_index = chunks_string.find(badspace)

            badspace = "  "
            badspace_index = chunks_string.find(badspace)
            while badspace_index > -1:
                chunks_string = chunks_string.replace(badspace, " ")
                badspace_index = chunks_string.find(badspace)

            chunks = chunks_string.split(" ")  # line_strip[space_index+1:].strip()
            if command == "newmtl":
                m_name = chunks_string
                if m_name not in wmaterials.keys():
                    wmaterials[m_name] = {}
                    # Store locations for later using relative texture
                    # paths in mtl file:
                    mtl_fname = filename
                    if (mtl_fname[:2] == "./") or (mtl_fname[:2] == ".\\"):
                        mtl_fname = mtl_fname[2:]
                    wmaterials[m_name]["tmp"] = {}
                    wmaterials[m_name]["tmp"]["file_path"] = mtl_fname
                    wmaterials[m_name]["tmp"]["directory"] = None
                    if os.path.dirname(mtl_fname) != "":
                        wmaterials[m_name]["tmp"]["directory"] = os.path.dirname(mtl_fname)
                    if (wmaterials[m_name]["tmp"]["directory"] is None) or \
                       (not os.path.isdir(wmaterials[m_name]["tmp"]["directory"])):
                        wmaterials[m_name]["tmp"]["directory"] = os.path.dirname(os.path.abspath(mtl_fname))
                    if not os.path.isdir(wmaterials[m_name]["tmp"]["directory"]):
                        print("[ WObjFile ] WARNING: could not find directory for relative paths in '" + filename + "' so using '" + str(os.path.isdir(wmaterials[m_name]["tmp"]["directory"]) + "'"))
                    # mesh_dir = os.path.dirname(os.path.abspath(filename))
                    # mtl_path = mtl_fname
                    # if (len(mesh_dir) > 0):
                    #     mtl_path = os.path.join(mesh_dir, mtl_fname)
                    # wmaterials[m_name].file_path = mtl_path
                    # ^ to make finding texture images easier later
                else:
                    print("[ WObjFile ] INPUT ERROR: newmtl already exists: '"+m_name+"' was referenced more than once in '" + filename + "' which is out of spec and not loadable")
            else:
                if len(chunks) > 0:
                    value_enables = [True] * len(chunks)
                    # ^ whether the values are
                    # values of the command (false
                    # if already used as arg or
                    # value of arg); start as None
                    # so they will not all be the
                    # same reference?
                    # veLen = len(value_enables)
                    # for i in range(veLen):
                    #    value_enables = True
                    # NOTE: values after arg are
                    # part of arg UNLESS at end,
                    # such as in "d -halo 0.6600"
                    # where 0.66 is a value for the
                    # command (of d)
                    # so first grab args and values
                    # of args:
                    option_key = None
                    debug_offset = len(command) + 1
                    if len(chunks) >= 2:
                        if chunks[0] == "-type":
                            # multiple refl commands
                            # may be present, which
                            # is an exception to the
                            # rule of having <=1
                            # instances of a
                            # command, so compensate
                            # via:
                            command += " -type " + chunks[1]
                            value_enables[0] = False
                            value_enables[1] = False
                    elif len(chunks) >= 1:
                        if chunks[0] == "spectral":
                            command += " spectral"
                            value_enables[0] = False
                        elif chunks[0] == "xyz":
                            command += " xyz"
                            value_enables[0] = False

                    wmaterials[m_name][command] = {}
                    wmaterials[m_name][command]["values"] = []

                    for i in range(len(chunks)):
                        # certain keywords are
                        # treated as part of the
                        # command for the statement
                        # (See
                        # <http://paulbourke.net/
                        # dataformats/mtl/>)
                        if value_enables[i]:
                            if chunks[i][:1] == "-":
                                option_key = chunks[i][1:]
                                wmaterials[m_name][command][option_key] = []
                                value_enables[i] = False
                                if i == (len(chunks)-1):
                                    print(filename + " (" + str(lineN) + "," + str(debug_offset) + "): (INPUT ERROR) material statement should end with value, not hyphen* argument")
                            elif i < (len(chunks)-1):
                                if option_key is not None:
                                    wmaterials[m_name][command][option_key].append(chunks[i])
                                    value_enables[i] = False
                        debug_offset += 1 + len(chunks[i])
                    for i in range(len(chunks)):
                        # remaining values are part of statement directly (as opposed to being options or option args):
                        if value_enables[i]:
                            wmaterials[m_name][command]["values"].append(chunks[i])
                else:
                    wmaterials[m_name]["values"] = []
                    print(filename + " (" + str(lineN) + "," + str(len(command)) + "): (INPUT ERROR) value(s) are expected after command ('" + command + "')")

            # end for lines in file
    # except:
    #     print("ERROR in fetch_wmaterial (could not finish):")
    #     view_traceback()
    return wmaterials


def show_object_faces_msg(this_object, msg_filename):
    faces_msg = "...WARNING: got None for this_object.face_groups!"
    if this_object.face_dicts is not None:
        key_count = 0
        face_count = 0
        faces_msg = "...WARNING: this_object face dicts contain 0 faces!"
        group_err = None
        for key in this_object.face_dicts:
            if this_object.face_dicts[key] is not None:
                if this_object.face_dicts[key]['faces'] is not None:
                    face_count += len(this_object.face_dicts[key]['faces'])
                else:
                    print(msg_filename + " ERROR: object named '" + str(this_object.name) + "' resulted in a group with a faces list that is None")
            else:
                print(msg_filename + " ERROR: object named '" + str(this_object.name) + "' resulted in a group that is None")
            key_count += 1
        if face_count == 0:
            faces_msg = "...WARNING: 0 FACES!"
        else:
            faces_msg = "..."+str(face_count)+" face(s)"
    print(msg_filename + ": object named " + str(this_object.name) + "" + faces_msg)


class WObjFile:

    STATIC_HELP = {
        'FACE_V': "index of vertex index in the face (face is a list)",
        'FACE_TC': "index of tc0 index in the face (face is a list)",
        'FACE_VN': "index of normal index in the face (face is a list)",
    }
    FACE_V = 0
    FACE_TC = 1
    FACE_VN = 2

    def __init__(self):
        self.filename = None
        self.wobjects = None
        self.wmaterials = None
        self.texcoords_not_2_warning_enable = True
        # self.NYI_s_enable = True
        self.short_name_in_messages_enable = True

    def load(self, filename):
        FACE_V = WObjFile.FACE_V
        FACE_TC = WObjFile.FACE_TC
        FACE_VN = WObjFile.FACE_VN
        f_name = "load"
        if (self.filename is not None):
            print("[ WObjFile ] WARNING in load: WObjFile already "
                  "loaded; loading '" + filename + "' in place of '"
                  + str(self.filename) + "'")
        if (self.wobjects is not None):
            print("[ WObjFile ] WARNING in load: WObjFile already "
                  "initialized; overriding from '" + filename + "'")
        self.filename = filename
        self.wobjects = {}
        self.wmaterials = None  # will be loaded using another method
        added_face_msg_enable = True
        msg_filename = filename
        if self.short_name_in_messages_enable:
            msg_filename = os.path.basename(os.path.normpath(filename))
        texcoord_number_warning_enable = True
        # try:
        if not os.path.exists(filename):
            print("[ WObjFile ] ERROR in {}:"
                  " missing file or cannot access '{}'"
                  "".format(f_name, msg_filename))
            return
        command = None
        prev_command = None
        prev_usable_command = None
        comments = list()
        this_object = None
        lineN = 0  # += 1 below before used
        mtl_fname = None
        # start offsets at 1 since obj file uses counting
        # numbers
        # v_offset = 1
        # vt_offset = 1
        # vn_offset = 1
        this_wobject_v_count = 0
        this_wobject_vt_count = 0
        this_wobject_vn_count = 0
        absolute_v_list = list()  # vertex
        absolute_vt_list = list()  # texcoord
        absolute_vn_list = list()  # normal
        absolute_v_count = 0
        absolute_vt_count = 0
        absolute_vn_count = 0
        individuated_v_count = 0
        v_map = None
        vt_map = None
        vn_map = None
        this_o_name = None
        # this_face_group = None
        group_names = ["default"]  # formerly this_face_group_name
        smoothing_param = None
        # this_face_group_key = None
        for line in open(filename, "r"):
            lineN += 1
            line_strip = line.strip()
            while ("\t" in line_strip):
                line_strip = line_strip.replace("\t", " ")
            while ("  " in line):
                line = line.replace("  ", " ")
            if len(line_strip) < 1:
                continue
            elif line_strip[0] == "#":
                comment_notag = line_strip[1:].strip()
                if len(comment_notag) > 0:
                    if this_object is not None:
                        this_object.preComment(comment_notag)
                    else:
                        comments.append(comment_notag)
                    words = comment_notag.split(" ")
                    if ((words is not None)
                            and (len(words) > 1)):
                        if words[0].lower() == "object":
                            if this_o_name is None:
                                this_o_name = words[1]
                            else:
                                print("NOTICE: skipping non-standard"
                                      " commented name '" + words[1]
                                      + "' since was already specified"
                                      " as '" + this_o_name + "'")
                prev_command = None
                continue

            if this_object is not None:
                this_object.has_any_data_enable = True
            space_index = line_strip.find(" ")
            args_string = ""
            if space_index > -1:
                command = line_strip[:space_index]
                if len(line_strip) >= (space_index+1):
                    # There is text after the first space,
                    # so it must be arguments.
                    args_string = line_strip[space_index+1:].strip()
            else:
                command = line_strip
            if len(args_string) > 0:
                params = args_string.split(" ")
                # line_strip[space_index+1:].strip()
            else:
                params = []
            if command == "mtllib":
                mtl_fname = args_string
                if (mtl_fname[:2] == "./") or (mtl_fname[:2] == ".\\"):
                    mtl_fname = mtl_fname[2:]
                mesh_dir = os.path.dirname(os.path.abspath(filename))
                mtl_path = mtl_fname
                if not os.path.isfile(mtl_path):
                    if len(mesh_dir) > 0:
                        mtl_path = os.path.join(mesh_dir, mtl_fname)
                        if not os.path.isfile(mtl_path):
                            mtl_path = None
                            print("[ WObjFile ] INPUT"
                                  " ERROR: missing '"
                                  + mtl_fname
                                  + "' in '"
                                  + mesh_dir
                                  + "'")
                    else:
                        mtl_path = None
                        print("[ WObjFile ] INPUT ERROR: missing '"
                              + mtl_fname + "' in mesh's folder or"
                              " current directory '" + os.getcwd()
                              + "'")
                if self.wmaterials is not None:
                    print("[ WObjFile ] WARNING: wmaterial"
                          " already initialized; overriding"
                          " from '" + mtl_path + "'")
                self.wmaterials = fetch_wmaterial(mtl_path)
            elif command == "o":
                if len(params) > 0:
                    this_o_name = params[0]
                    # ^ this_object.name = params[0]
            elif command == "g":
                if len(params) > 0:
                    group_names = params
                else:
                    group_names = ["default"]  # as per spec
            elif command == "v":
                if prev_usable_command != command:
                    # this is non-spec to account for
                    # non-spec v commands that aren't
                    # preceded by `o` command
                    if this_object is not None:
                        # NOTE: this_object.name is guaranteed
                        self.wobjects[this_object.name] = \
                            this_object
                        show_object_faces_msg(this_object,
                                              msg_filename)
                        this_object = None
                        # v_offset \
                        # += len(this_object.vertices)
                        # vt_offset \
                        # += len(this_object.texcoords)
                        # vn_offset \
                        # += len(this_object.normals)
                    if this_o_name is None:
                        # do AFTER using name as key for
                        # adding previous object to
                        # self.wobjects
                        this_o_name = self._get_unused_wobject_key()
                        print("{} ({},0): (INPUT ERROR)"
                              " `o` command should precede `v` command"
                              "--compensating for out-of-spec obj file"
                              " by using generated name '{}'"
                              "".format(msg_filename,
                                        lineN,
                                        this_o_name))
                    v_map = dict()
                    vt_map = dict()
                    vn_map = dict()
                    this_object = WObject()
                    this_object.name = this_o_name
                    this_o_name = None  # consume it
                    this_vertex_group_type = None
                    this_object.source_path = filename
                    this_object.mtl_filename = mtl_fname
                    this_wobject_v_count = 0
                    this_wobject_vt_count = 0
                    this_wobject_vn_count = 0
                    if len(comments) > 0:
                        for i in range(0, len(comments)):
                            this_object.preComment(comments[i])
                        # comments[:] = []
                        del comments[:]
                        # comments.clear()
                        # ^ requires python 3.3 or later
                # NOTE: references a v by vertex# are relative to file
                # instead of 'o', but this is detected & fixed at end of
                # this method (for each object discovered) since file
                # may not match spec
                if this_object.vertices is None:
                    this_object.vertices = list()
                args = args_string.split(" ")
                result_v = (0.0, 0.0, 0.0)
                if len(args) >= 7:
                    result_v = get_fvec7(args)
                    # ^ allow nonstandard x,y,z,r,g,b,a
                    # (position then color) format
                elif len(args) >= 6:
                    result_v = get_fvec6(args)
                    # ^ allow nonstandard x,y,z,r,g,b
                    # (position then color) format
                elif len(args) >= 3:
                    result_v = get_fvec3(args)
                if ((len(args) != 3) and (len(args) != 6)
                        and (len(args) != 7)):
                    print("{} ({},0): (INPUT WARNING) vertex must have"
                          " 3 total coordinate values (or 3 followed by"
                          " 3 to 4 color channels for 6 to 7 total):"
                          " '{}'".format(msg_filename,
                                         lineN,
                                         args_string))
                    if len(args) >= 2:
                        result_v = get_fvec3((args[0], 0.0, args[1]))
                        # ^ assume x,z for 2d vert
                    if len(args) >= 1:
                        result_v = get_fvec3((args[0], 0.0, 0.0))
                        # ^ assume x,z for 2d vert
                # this_object.vertices.append(result_v)
                absolute_v_list.append(result_v)
                absolute_v_count += 1
                # v_offset += 1
            elif this_object is not None:
                if command == "vt":
                    args = args_string.split(" ")
                    result_vt = (0.0, 0.0)
                    if len(args) >= 2:
                        result_vt = get_fvec2(args)
                    if (self.texcoords_not_2_warning_enable):
                        if (len(args) != 2):
                            if (len(args) < 2):
                                print("{} ({},0): (INPUT ERROR)"
                                      " texcoord missing coordinate"
                                      " (expected u v after vt but only"
                                      " got one param) so texture may"
                                      " not be applied correctly: '{}'"
                                      "".format(msg_filename,
                                                lineN,
                                                args_string))
                            else:
                                if len(args) != 3:
                                    print("{} ({},0): (INPUT ERROR)"
                                          " texcoords must have 2"
                                          " (vt u v) or 3 (vt u v w)"
                                          " coordinates: '{}'"
                                          "".format(msg_filename,
                                                    lineN,
                                                    args_string))
                                else:
                                    print("{} ({},0): (INPUT WARNING /"
                                          " NOT YET IMPLEMENTED)"
                                          " texcoord with 3 coordinates"
                                          " (vt u v w)"
                                          " so w may be ignored: '{}'"
                                          "".format(msg_filename,
                                                    lineN,
                                                    args_string))
                            print("(this is the last texcoords input"
                                  " warning that will be shown)")
                            print("")
                            self.texcoords_not_2_warning_enable = False
                    # this_object.texcoords.append(result_vt)
                    absolute_vt_list.append(result_vt)
                    absolute_vt_count += 1
                    # Still increment since is reference to index obj
                    #   file:
                    # vt_offset += 1

                elif command == "vn":
                    # NOTE: presence of normals supercedes
                    # smoothing groups
                    args = args_string.split(" ")
                    result_vn = (0.0, 0.0, 0.0)
                    if len(args) >= 3:
                        result_vn = get_fvec3(args)
                    if len(args) != 3:
                        print("{} ({},0): (INPUT ERROR)"
                              " normal must have 3 coordinates: '{}'"
                              "".format(msg_filename,
                                        lineN,
                                        args_string))
                    # this_object.normals.append(result_vn)
                    absolute_vn_list.append(result_vn)
                    absolute_vn_count += 1
                    # vn_offset += 1
                elif command == "l":
                    # polyline
                    if this_object.polylines is None:
                        this_object.polylines = []
                    args = args_string.split(" ")
                    this_polyline = []
                    for i in range(len(args)):
                        absolute_v_index = None
                        stated_v_number = int(args[i])
                        if stated_v_number >= 1:
                            absolute_v_index = stated_v_number - 1
                            vertex_number = this_wobject_v_count
                            # ^ ok since adding it below
                        elif stated_v_number < 0:
                            # ^ negative index is relative in the spec
                            absolute_v_index = (absolute_v_count
                                                + stated_v_number)
                            # ^ + since negative
                            vertex_number = this_wobject_v_count
                            # ^ ok since adding it below
                        else:
                            print("{} ({},0): (INPUT ERROR)"
                                  " line vertex number 0 in obj is"
                                  " nonstandard and will be skipped"
                                  "".format(msg_filename,
                                            lineN))
                        if absolute_v_index is not None:
                            abs_v_i_s = str(absolute_v_index)
                            if abs_v_i_s in v_map:
                                absolute_v_index = None
                                # ^ prevents copying same one to wobject
                                #   again below
                                vertex_number = v_map[abs_v_i_s]
                            else:
                                v_map[abs_v_i_s] = vertex_number
                        if absolute_v_index is not None:
                            if this_object.vertices is None:
                                this_object.vertices = list()
                            v_num_s = str(vertex_number)
                            this_object.vertices.append(
                                absolute_v_list[absolute_v_index]
                            )
                            individuated_v_count += 1
                            this_wobject_v_count += 1
                            this_polyline.append(int(args[i]) - 1)
                    if len(this_polyline) > 0:
                        this_object.polylines.append(this_polyline)
                    else:
                        print("{} ({},0): (INPUT ERROR)"
                              " bad polyline skipped (should have"
                              " absolute counting number of"
                              " existing vertex from 'v' command"
                              " in file)"
                              "".format(msg_filename,
                                        lineN))
                elif command == "f":
                    if prev_usable_command != command:
                        if group_names is None:
                            group_names = ["default"]
                        if this_object.face_groups is None:
                            this_object.face_groups = {}
                        smoothing_key = smoothing_param
                        smoothing_mode = None
                        if smoothing_param is None or \
                           smoothing_param == "on" or \
                           smoothing_param == "off":
                            smoothing_key = \
                                this_object._get_unused_face_list_key()
                            smoothing_mode = smoothing_param
                        else:
                            smoothing_mode = "on"

                        if this_object.face_dicts is None:
                            this_object.face_dicts = {}
                        if smoothing_key not in this_object.face_dicts:
                            this_object.face_dicts[smoothing_key] = {}
                        this_object.face_dicts[smoothing_key]['s'] = \
                            smoothing_mode
                        this_object.face_dicts[smoothing_key]['faces'] = []
                        for group_name in group_names:
                            if group_name not in this_object.face_groups:
                                this_object.face_groups[group_name] = \
                                    []
                            if smoothing_key not in this_object.face_groups[group_name]:
                                this_object.face_groups[group_name].append(smoothing_key)

                    args = args_string.split(" ")
                    this_face = []
                    for i in range(0, len(args)):
                        absolute_v_index = None
                        absolute_vt_index = None
                        absolute_vn_index = None
                        vertex_number = None
                        texcoord_number = None
                        normal_number = None
                        values = args[i].split("/")
                        # subtract offsets from values since
                        # obj file not only uses counting
                        # numbers but also numbers unique in
                        # entire file (as opposed to
                        # starting over for each object):
                        if len(values) >= 1:
                            values[FACE_V] = values[FACE_V].strip()
                            if len(values[FACE_V]) > 0:
                                # ^ if not blank string
                                stated_v_number = int(values[FACE_V])
                                if stated_v_number >= 1:
                                    absolute_v_index = (stated_v_number
                                                        - 1)
                                    vertex_number = this_wobject_v_count
                                    # ^ ok since adding it below
                                elif stated_v_number < 0:
                                    # ^ negative index is relative as
                                    #   per the spec
                                    absolute_v_index = (absolute_v_count
                                                        + stated_v_number)
                                    # ^ + since negative
                                    vertex_number = this_wobject_v_count
                                    # ^ ok since adding it below
                                else:
                                    print("{} ({},0): (INPUT ERROR)"
                                          " vertex number 0 in obj is"
                                          " nonstandard and will be"
                                          " skipped"
                                          "".format(msg_filename,
                                                    lineN))
                                if absolute_v_index is not None:
                                    abs_v_i_s = str(absolute_v_index)
                                    if abs_v_i_s in v_map:
                                        absolute_v_index = None
                                        # ^ prevents copying same one to
                                        #   wobject again below
                                        vertex_number = v_map[abs_v_i_s]
                                    else:
                                        v_map[abs_v_i_s] = vertex_number
                        if len(values) >= 2:
                            values[FACE_TC] = values[FACE_TC].strip()
                            if len(values[FACE_TC]) > 0:
                                # ^ if not blank string
                                # texcoord_number = \
                                #     int(values[FACE_TC])-vt_offset
                                stated_texcoord_number = int(values[FACE_TC])
                                if stated_texcoord_number >= 1:
                                    absolute_vt_index = stated_texcoord_number - 1
                                    texcoord_number = this_wobject_vt_count
                                    # ^ ok since adding it below
                                elif stated_texcoord_number < 0:
                                    # ^ negative index is relative in
                                    #   the spec
                                    absolute_vt_index = (absolute_v_count
                                                         + stated_v_number)
                                    # ^ + since negative
                                    texcoord_number = this_wobject_vt_count
                                    # ^ ok since adding it below
                                else:
                                    print("{} ({},0): (PARSER WARNING)"
                                          " texcoord number 0 on obj is"
                                          " nonstandard and will be"
                                          " skipped"
                                          "".format(msg_filename,
                                                    lineN))
                                if absolute_vt_index is not None:
                                    abs_vt_i_s = str(absolute_vt_index)
                                    if abs_vt_i_s in vt_map:
                                        absolute_vt_index = None
                                        # ^ prevents copying same one to
                                        #   wobject again below
                                        texcoord_number = vt_map[abs_vt_i_s]
                                    else:
                                        vt_map[abs_vt_i_s] = texcoord_number
                        if len(values) >= 3:
                            values[FACE_VN] = values[FACE_VN].strip()
                            if len(values[FACE_VN]) > 0:
                                # ^ if not blank string

                                # normal_number = (int(values[FACE_VN])
                                #                  - vn_offset)
                                stated_normal_number = int(
                                    values[FACE_VN]
                                )
                                if stated_normal_number >= 1:
                                    absolute_vn_index = \
                                        stated_normal_number - 1
                                    normal_number = \
                                        this_wobject_vn_count
                                    # ^ ok since adding it below
                                elif stated_normal_number < 0:
                                    # ^ negative index is relative in
                                    #   the spec
                                    absolute_vn_index = \
                                        (absolute_vn_count
                                         + stated_normal_number)
                                    # ^ + since negative
                                    normal_number = this_wobject_vn_count
                                    # ^ ok since adding it below
                                else:
                                    print("{} ({},0): (PARSER WARNING)"
                                          " normal number 0 on obj is"
                                          " nonstandard and will be"
                                          " skipped"
                                          "".format(msg_filename,
                                                    lineN))
                                if absolute_vn_index is not None:
                                    abs_vn_i_s = str(absolute_vn_index)
                                    if abs_vn_i_s in vn_map:
                                        absolute_vn_index = None
                                        # ^ prevents copying same one to
                                        #   wobject again below
                                        normal_number = \
                                            vn_map[abs_vn_i_s]
                                    else:
                                        vn_map[abs_vn_i_s] = \
                                            normal_number
                        if absolute_v_index is not None:
                            if this_object.vertices is None:
                                this_object.vertices = list()
                            v_num_s = str(vertex_number)
                            this_object.vertices.append(
                                absolute_v_list[absolute_v_index]
                            )
                            individuated_v_count += 1
                            this_wobject_v_count += 1
                        if absolute_vt_index is not None:
                            if this_object.texcoords is None:
                                this_object.texcoords = list()
                            vt_num_s = str(texcoord_number)
                            this_object.texcoords.append(
                                absolute_vt_list[absolute_vt_index]
                            )
                            this_wobject_vt_count += 1
                        if absolute_vn_index is not None:
                            if this_object.normals is None:
                                this_object.normals = list()
                            vn_num_s = str(normal_number)
                            this_object.normals.append(
                                absolute_vn_list[absolute_vn_index]
                            )
                            this_wobject_vn_count += 1
                        if texcoord_number_warning_enable:
                            if texcoord_number is None:
                                print("{} ({},0): (PARSER WARNING)"
                                      " vertex texcoord_number is None"
                                      " when adding to face"
                                      "".format(msg_filename,
                                                lineN))
                                print("(this is the last texcoord"
                                      "_number warning that will be"
                                      " shown for this input file)")
                                print("")
                                texcoord_number_warning_enable = False
                        this_face.append([
                            vertex_number,
                            texcoord_number,
                            normal_number
                        ])
                        # ^ this is OBJ vertex_format
                    this_object.face_dicts[smoothing_key]['faces'].append(this_face)
                    if added_face_msg_enable:
                        # FIXME: This misses some meshes (or another
                        #       part of this code does)
                        print("added face to '{}' face list key '{}':"
                              " {}".format(this_object.name,
                                           smoothing_key, this_face))
                        added_face_msg_enable = False
                        if not added_face_msg_enable:
                            # print("(this is the last face message"
                            #       " that will be shown for this input"
                            #       " file)")
                            # print("")
                            pass
                elif command == "usemtl":
                    if self.wmaterials is not None:
                        if args_string in self.wmaterials.keys():
                            this_object.wmaterial = \
                                self.wmaterials[args_string]
                            # get_by_name(wmaterials, args_string)
                            if this_object.wmaterial is None:
                                print("{} ({},0): (INPUT ERROR)"
                                      " material named '{}' is None"
                                      "".format(msg_filename,
                                                lineN,
                                                args_string))
                        else:
                            print("{} ({},0): (INPUT ERROR)"
                                  " unknown material name '{}'"
                                  "".format(msg_filename,
                                            lineN,
                                            args_string))
                    else:
                        print("{} ({},0): (INPUT ERROR)"
                              " usemtl '{}' is impossible since a"
                              " material was not loaded"
                              " with mtllib command first."
                              "".format(msg_filename,
                                        lineN,
                                        args_string))
                elif command == "s":
                    if args_string == "off":
                        smoothing_param = "off"
                    elif args_string == "0":
                        # ^ 0==off in spec
                        smoothing_param = "off"
                    else:
                        smoothing_param = args_string
                else:
                    print("{} ({},0): (INPUT ERROR)"
                          " unknown OBJ object command '{}'"
                          "".format(msg_filename,
                                    lineN,
                                    command))
            else:
                print("{} ({},0): (INPUT ERROR)"
                      " OBJ object command '{}' before 'o'"
                      "".format(msg_filename,
                                lineN,
                                command))
            '''
            else:
                print("{} ({},0): (INPUT ERROR)"
                      " no arguments after command"
                      "".format(msg_filename, lineN))
            else:
                print("{} ({},0): (INPUT ERROR)"
                      " no space after command"
                      "".format(msg_filename, lineN))
            '''
            prev_command = command
            prev_usable_command = command

        # end for lines in file
        # NOTE: "finalize_obj" code is no longer needed since offsets were already applied above and original format is kept intact (indices instead of opengl-style vertex info array)
        if this_object is not None:
            # NOTE: this_object.name is guaranteed
            self.wobjects[this_object.name] = this_object
            show_object_faces_msg(this_object, msg_filename)
            print("[ WObjFile ] '" + msg_filename + "' has a total of "
                  + str(len(absolute_v_list)) + " vertices loaded as "
                  + str(individuated_v_count) + " vertices")
            this_object = None
        else:
            if len(self.wobjects) > 0:
                print("[ WObjFile ] ERROR in " + f_name + ": '"
                      + msg_filename + "' did not have any vertex data"
                      " after last 'o' statement")
            else:
                print("[ WObjFile ] ERROR in " + f_name + ": '"
                      + msg_filename + "' did not have any vertex data"
                      " (self.wobjects remains empty)")
        if self.wobjects is not None:
            if len(self.wobjects) < 1:
                print("[ WObjFile ] WARNING: " + f_name
                      + " got 0 objects from '" + msg_filename + "'")
        # else ignore since already has file does not exist error

    def _get_unused_wobject_key(self):
        # this_o_name = None
        # while True:
        #     this_o_name = ("untitled_wobject_"
        #                    + str(self.untitled_number))
        #     self.untitled_number += 1
        #     if this_o_name not in self.wobjects:
        #         break
        # return this_o_name
        return str(uuid.uuid4())

