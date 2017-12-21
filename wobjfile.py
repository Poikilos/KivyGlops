"""
This provides simple dependency-free access to OBJ files and certain 3D math operations.
#Illumination models (as per OBJ format standard):
# 0. Color on and Ambient off
# 1. Color on and Ambient on [binary:0001]
# 2. Highlight on [binary:0010]
# 3. Reflection on and Ray trace on [binary:0011]
# 4. Transparency: Glass on, Reflection: Ray trace on [binary:0100]
# 5. Reflection: Fresnel on and Ray trace on [binary:0101]
# 6. Transparency: Refraction on, Reflection: Fresnel off and Ray trace on [binary:0110]
# 7. Transparency: Refraction on, Reflection: Fresnel on and Ray trace on [binary:0111]
# 8. Reflection on and Ray trace off [binary:1000]
# 9. Transparency: Glass on, Reflection: Ray trace off [binary:1001]
# 10. Casts shadows onto invisible surfaces [binary:1010]
"""

import os
import sys  # exception etc
import math
import traceback

tab_string = "  "

#from common import view_traceback
#from common import get_by_name
from common import *

#these are needed since in python 3, int is no longer bounded:
MIN_INDEX = -9223372036854775807
MAX_INDEX = 9223372036854775808

FACE_V = 0  # index of vertex index in the face (since face is a list)
FACE_TC = 1  # index of tc0 index in the face (since face is a list)
FACE_VN = 2  # index of normal index in the face (since face is a list)

#def get_int_list(values):
    #results=list()
    #for i in range(0,len(values)):
        #results.append(int(values[i]))
    #return results


#def get_float_list(values):
    #results=list()
    #for i in range(0,len(values)):
        #results.append(float(values[i]))
    #return results


def get_fvec2(values,start_index=0):
    return (float(values[start_index]), float(values[start_index+1]))


def get_fvec3(values,start_index=0):
    return (float(values[start_index]), float(values[start_index+1]), float(values[start_index+2]))

def get_fvec6(values,start_index=0):
    return (float(values[start_index]), float(values[start_index+1]), float(values[start_index+2]), float(values[start_index+3]), float(values[start_index+4]), float(values[start_index+5]))

def get_fvec7(values,start_index=0):
    return (float(values[start_index]), float(values[start_index+1]), float(values[start_index+2]), float(values[start_index+3]), float(values[start_index+4]), float(values[start_index+5]), float(values[start_index+6]))

#def get_fvec4(values,start_index=0):
    #result = None
    #if len(values)-start_index>=4:
        #result = (float(values[start_index]), float(values[start_index+1]), float(values[start_index+2]), float(values[start_index+3]))
    #else:
        #result = (float(values[start_index]), float(values[start_index+1]), float(values[start_index+2]), 1.0)
    #return result

#class WObjFile (see further down) most accurately represents the obj file format (except indices start at 0 in WObject instead of 1 which file uses). It contains a list of WObjects (each WObject has only the material it needs from the mtl file)

class WIlluminationModel:
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

    def set_from_illumination_model_number(self, number):
        result = True
        self.number = number  #changed to None below if invalid
        if number==0:
            self.is_color = True
            self.is_ambient = False
        elif number==1:
            self.is_color = True
            self.is_ambient = True
        elif number==2:
            self.is_highlight = True
        elif number==3:
            self.is_reflection = True
        elif number==4:
            self.is_transparency = True
            self.is_transparency_glass = True
            self.is_reflection = True
            self.is_reflection_raytrace = True
        elif number==5:
            self.is_reflection = True
            self.is_reflection_fresnel = True
            self.is_reflection_raytrace = True
        elif number==6:
            self.is_transparency = True
            self.is_transparency_refraction = True
            self.is_reflection = True
            self.is_reflection_fresnel = False
            self.is_reflection_raytrace = True
        elif number==7:
            self.is_transparency = True
            self.is_transparency_refraction = True
            self.is_reflection = True
            self.is_reflection_fresnel = True
            self.is_reflection_raytrace = True
        elif number==8:
            self.is_reflection = True
            self.is_reflection_raytrace = False
        elif number==9:
            self.is_transparency = True
            self.is_transparency_glass = True
            self.is_reflection = True
            self.is_reflection_raytrace = False
        elif number==10:
            self.is_shadow_cast_onto_invisible_surfaces = True
        else:
            result = False
            self.number = None
        return result

class WColorArgInfo:
    _param = None
    _value_min_count = None
    _value_max_count = None
    _description = None
    _value_descriptions = None

    def __init__(self, param, description, value_min_count, value_max_count, value_descriptions):
        self._param = param
        self._description = description
        self._value_min_count = value_min_count
        self._value_max_count = value_max_count


#http://paulbourke.net/dataformats/mtl/ says:
#To specify the ambient reflectivity of the current material, you can
#use the "Ka" statement, the "Ka spectral" statement, or the "Ka xyz"
#statement. Tip These statements are mutually exclusive.
color_arg_type_strings = list()
color_arg_type_strings.append(WColorArgInfo("type","type",1,1,["type, such as type of reflection"]))
color_arg_type_strings.append(WColorArgInfo("spectral","spectral curve",1,2,["filename","factor"]))
color_arg_type_strings.append(WColorArgInfo("xyz","specifies that the values are in CIEXYZ colorspace",3,3,["X as in CIEXYZ","Y as in CIEXYZ","Z as in CIEXYZ"]))
color_arg_type_strings.append(WColorArgInfo("blendu","blend U in map",1,1,["on|off"]))
color_arg_type_strings.append(WColorArgInfo("blendv","blend V in map",1,1,["on|off"]))
color_arg_type_strings.append(WColorArgInfo("clamp","clamp to 0-1 in UV range",1,1,["on|off"]))
color_arg_type_strings.append(WColorArgInfo("cc","color correction (only for map_Ka, map_Kd, and map_Ks)",1,1,["on|off"]))
color_arg_type_strings.append(WColorArgInfo("mm","base gain",2,2,["black level|white level (processed before black level, so acts as range)"]))
color_arg_type_strings.append(WColorArgInfo("t","turbulence (post-processes tiled textures to hide seem)",2,3,["u","v","w"]))
color_arg_type_strings.append(WColorArgInfo("texres","resizes texture before using, such as for NPOT textures; if used, image is forced to a square",2,3,["pixel count"]))

#types for refl map (need one texture if refl is -type sphere, but need six if cube:)
#refl -type cube_top
# refl -type cube_bottom
# refl -type cube_front
# refl -type cube_back
# refl -type cube_left
# refl -type cube_right

#http://paulbourke.net/dataformats/mtl/ says (similar or same for Kd etc):
#The options for the "map_Ka" statement are listed below.  These options
#are described in detail in "Options for texture map statements" on page
#5-18.
#   -blendu on | off
#   -blendv on | off
#   -cc on | off
#   -clamp on | off
#   -mm base gain
#   -o u v w
#   -s u v w
#   -t u v w
#   -texres value


class WFaceGroup:
    def __init__(self):
        self.faces = None
        #NOTE: no self.name since name is key, since WFaceGroup is in a dict (however, do not save g or s command [discard key] if self.face_group_type is None)
        self.face_group_type = None  # `g` or `s`
    
    def emit_yaml(self, thisList, min_tab_string):
        #thisList.append(min_tab_string+this_list_name+":")
        name_line = "name: "
        if self.name is not None:
            name_line += self.name
        else:
            name_line += "~"
        thisList.append(min_tab_string+name_line)
        if self.faces is not None:
            thisList.append(min_tab_string+"faces:")
            for face in faces:
                thisList.append(min_tab_string+tab_string+"- ")
                for vertex_i in face:
                    thisList.append(min_tab_string+tab_string+tab_string+"- "+str(vertex_i))
        else:
            thisList.append(min_tab_string+"faces: ~")


class WMaterial:

    name = None
    file_path = None  # for finding texture images more easily later
    _opening_comments = None
    _illumination_model = None
    _opacity = None # d (or 1.0-Tr)
    _ambient_color = None  # Ka
    _diffuse_color = None  # Kd
    _specular_color = None  # Ks; black is 'off' (same as None)
    _specular_exponent = None  # Ns (0 to 1000) "specular highlight component" ('hardness'?)

    #_transmission_color = None  # Tf; NOT YET IMPLEMENTED
    #_is_halo = None  # outer rim is fully opaque, inner part is based on _opacity
    # _sharpness = None  # sharpness; sharpness of reflections, 0 to 1000; NOT YET IMPLEMENTED
    # optical_density = None  #TODO: Ni; Index of Refraction; 0.001 to 10
    _map_filename_dict = None
    _map_params_dict = None
    #_map_ambient_filename = None  # map_Ka
    #_map_diffuse_filename = None  # map_Kd
    #_map_specular_color_filename = None    # map_Ks
    #_map_specular_highlight_filename = None    # map_Ns --just a regular image, but used as gray (values for exponent)
    #_map_transparency_filename = None  # map_d
    #_map_bump_filename = None  # map_bump or bump: use luminance
    #_map_displacement = None  # disp
    #_map_decal = None # decal: stencil; defaults to 'matte' channel of image
    #_map_reflection = None  # refl; can be -type sphere


    def __init__(self, name=None):
        self.name = name
        self._opacity = 1.0
        self._map_filename_dict = {}
        self._map_params_dict = {}

    def append_opening_comment(self, text):
        if self._opening_comments is None:
            self._opening_comments = list()
        self._opening_comments.append(text)


#Also in pyglops.py; formerly dumpAsYAMLArray
def standard_emit_yaml(thisList, min_tab_string, sourceList):
    if isinstance(sourceList, list):
        for key in range(0,len(sourceList)):
            if isinstance(sourceList[key], list) or isinstance(sourceList[key], dict):
                thisList.append(min_tab_string+"-")
                standard_emit_yaml(thisList, min_tab_string+tab_string, sourceList[key])
            else:
                thisList.append(min_tab_string+"- "+str(sourceList[key]))
    elif isinstance(sourceList, dict):
        for key in sourceList:
            if isinstance(sourceList[key], list) or isinstance(sourceList[key], dict):
                thisList.append(min_tab_string+key+":")
                standard_emit_yaml(thisList, min_tab_string+tab_string, sourceList[key])
            else:
                thisList.append(min_tab_string+key+": "+str(sourceList[key]))
    else:
        print("WARNING in standard_emit_yaml: type '" + type(sourceList) + "' was not implemented and so was converted by plain str function")
        thisList.append(min_tab_string+str(sourceList))


class WObject:
    #region raw OBJ data (as per nskrypnik)
    #_name = None
    #_vertex_strings = None
    #_obj_cache_vertices = None
    #_pivot_point = None
    #_min_coords = None  #bounding cube minimums in local coordinates
    #_max_coords = None  #bounding cube maximums in local coordinates
    #texcoords = None
    #normals = None
    #parameter_space_vertices = None  #only for curves--not really implemented, just loaded from obj
    #faces = None
    #endregion raw OBJ data (as per nskrypnik)
    source_path = None
    parameter_space_vertices = None  #only for curves--not really implemented, just loaded from obj
    mtl_filename = None
    material_name = None
    vertices = None  # v
    texcoords = None  # vt (uv point in texture where each coord is from 0.0 to 1.0); aka vertex_uvs
    normals = None  # vn
    face_groups = None  # f; vertex#/texcoord#/normal# were *# is a counting number starting at 0 (BUT saved as 1)-- only vertex# is required (but // is used if texcoord# is not present but normal# is).
    wmaterial = None
    name = None
    has_any_data_enable = None

    _opening_comments = None

    def __init__(self, name=None):
        self.name = name
        self.has_any_data_enable = False

    def append_opening_comment(self, text):
        if self._opening_comments is None:
            self._opening_comments = list()
        self._opening_comments.append(text)

    def emit_yaml(self, thisList, min_tab_string):
        if self.source_path is not None:
            thisList.append(min_tab_string+"source_path: "+self.source_path)
        thisList.append(min_tab_string+"vertices:")
        standard_emit_yaml(thisList, min_tab_string+tab_string, self.vertices)
        thisList.append(min_tab_string+"texcoords:")
        standard_emit_yaml(thisList, min_tab_string+tab_string, self.texcoords)
        thisList.append(min_tab_string+"normals:")
        standard_emit_yaml(thisList, min_tab_string+tab_string, self.normals)
        thisList.append(min_tab_string+"_vertex_strings:")
        standard_emit_yaml(thisList, min_tab_string+tab_string, self._vertex_strings)
        thisList.append(min_tab_string+"parameter_space_vertices:")
        standard_emit_yaml(thisList, min_tab_string+tab_string, self.parameter_space_vertices)
        thisList.append(min_tab_string+"face_groups:")
        for key in self.face_groups:
            thisList.append(min_tab_string+tab_string+"key:")
            self.face_groups[key].emit_yaml(thisList, min_tab_string+tab_string+tab_string)


ILLUMINATIONMODEL_DESCRIPTION_STRINGS = ["Color on and Ambient off","Color on and Ambient on","Highlight on","Reflection on and Ray trace on","Transparency: Glass on, Reflection: Ray trace on","Reflection: Fresnel on and Ray trace on","Transparency: Refraction on, Reflection: Fresnel off and Ray trace on","Transparency: Refraction on, Reflection: Fresnel on and Ray trace on","Reflection on and Ray trace off","Transparency: Glass on, Reflection: Ray trace off","Casts shadows onto invisible surfaces"]

def get_illumination_model_description(illuminationModelIndex):
    #global ILLUMINATIONMODEL_DESCRIPTION_STRINGS
    resultString = None
    if (illuminationModelIndex>=0) and (illuminationModelIndex<len(ILLUMINATIONMODEL_DESCRIPTION_STRINGS)):
        ILLUMINATIONMODEL_DESCRIPTION_STRINGS[illuminationModelIndex]
    return resultString


def get_wmaterial_dict_from_mtl(filename):
    results = None
    try:
        if os.path.exists(filename):
            results = dict()
            comments = list()
            line_counting_number = 1
            this_mtl_name = None
            for line in open(filename, "r"):
                line_strip = line.strip()
                while ("\t" in line_strip):
                    line_strip = line_strip.replace("\t", " ")
                while ("  " in line_strip):
                    line_strip = line_strip.replace("  ", " ")
                if (len(line_strip)>0) and (line_strip[0]!="#"):
                    space_index = line_strip.find(" ")
                    if space_index>-1:
                        args_string = ""
                        if len(line_strip) >= (space_index+1):  #prevent out of range exception if nothing after space
                            args_string = line_strip[space_index+1:].strip()
                        if len(args_string)>0:
                            command = line_strip[:space_index].strip()

                            if (this_mtl_name is not None) or (command == "newmtl"):
                                badspace="\t"
                                badspace_index = args_string.find(badspace)
                                while badspace_index > -1:
                                    args_string = args_string.replace(badspace, " ")
                                    badspace_index = args_string.find(badspace)

                                badspace="  "
                                badspace_index = args_string.find(badspace)
                                while badspace_index > -1:
                                    args_string = args_string.replace(badspace, " ")
                                    badspace_index = args_string.find(badspace)

                                params = args_string.split(" ")  # line_strip[space_index+1:].strip()
                                if command=="newmtl":
                                    this_mtl_name = args_string
                                    if this_mtl_name not in results.keys():
                                        results[this_mtl_name] = WMaterial(name=this_mtl_name)

                                        this_mtl_filename = filename
                                        if (this_mtl_filename[:2]=="./") or (this_mtl_filename[:2]==".\\"):
                                            this_mtl_filename = this_mtl_filename[2:]
                                        this_mesh_folder_path = os.path.dirname(os.path.abspath(filename))
                                        this_mtl_path = this_mtl_filename
                                        if (len(this_mesh_folder_path)>0):
                                            this_mtl_path = os.path.join(this_mesh_folder_path, this_mtl_filename)
                                        results[this_mtl_name].file_path = this_mtl_path  # to make finding texture images easier later
                                    else:
                                        print("WARNING: newmtl already exists: '"+this_mtl_name+"'")
                                elif command=="illum":
                                    this_illum = WIlluminationModel()
                                    result=this_illum.set_from_illumination_model_number(int(args_string))
                                    if result:
                                        results[this_mtl_name]._illumination_model = this_illum
                                    else:
                                        print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) unknown illumination model number '"+args_string+"'")
                                elif command=="d":
                                    halo_string = " -halo "
                                    if len(args_string)>=len(halo_string):
                                        if args_string[:len(halo_string)]==halo_string:
                                            #TODO: halo formula: dissolve = 1.0 - (N*v)(1.0-factor)  # makes center transparent
                                            args_string=args_string[len(halo_string):]
                                            print(filename+" ("+str(line_counting_number)+",0): (NOT YET IMPLEMENTED) halo, so using next value as plain opacity value instead")
                                    this_opacity = float(args_string)
                                    if (this_opacity>=0.0) and (this_opacity<=1.0):
                                        results[this_mtl_name]._opacity = this_opacity
                                    else:
                                        print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) invalid opacity '"+args_string+"' so using '"+str(results[this_mtl_name]._opacity)+"' instead")
                                elif command=="Tr":
                                    this_transparency = float(args_string)
                                    if (this_transparency>=0.0) and (this_transparency<=1.0):
                                        results[this_mtl_name]._opacity = 1.0-this_transparency
                                    else:
                                        print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) invalid transparency '"+args_string+"' so using '"+str(results[this_mtl_name]._opacity)+"' instead")
                                elif command=="Kd":
                                    is_args_ok = True
                                    value_start=3
                                    value_name="spectral"
                                    if args_string[value_start:value_start+len(value_name)]==value_name:
                                        print(filename+" ("+str(line_counting_number)+",0): (NOT YET IMPLEMENTED) spectral value for '"+command+"'")
                                        is_args_ok = False
                                    value_name="xyz"
                                    if args_string[value_start:value_start+len(value_name)]==value_name:
                                        print(filename+" ("+str(line_counting_number)+",0): (NOT YET IMPLEMENTED) CIEXYZ color for '"+command+"'")
                                        is_args_ok = False
                                    if is_args_ok:
                                        diffuse_color=args_string.split(" ")
                                        if len(diffuse_color)>=3:
                                            results[this_mtl_name]._diffuse_color = [float(diffuse_color[len(diffuse_color)-3]), float(diffuse_color[len(diffuse_color)-2]), float(diffuse_color[len(diffuse_color)-1])]
                                        else:
                                            print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) color must have 3 values (r g b): '"+command+"'")
                                elif len(command)>4 and (command[:4]=="map_"):
                                    if len(args_string)>0 and args_string[0]=="-":
                                        #TODO: load OBJ map params
                                        results[this_mtl_name]._map_filename_dict[command] = params[len(params)-1]
                                        results[this_mtl_name]._map_params_dict = params[:len(params)-1]
                                        #results[this_mtl_name]._map_diffuse_filename = params[len(params)-1]
                                        #args = args_string.split(" ")
                                        #results[this_mtl_name]._map_diffuse_filename = args[len(args)-1]
                                        #if len(args)>1:
                                        #    print(filename+" ("+str(line_counting_number)+",0): (NOT YET IMPLEMENTED) map arguments were ignored (except filename): '"+args_string+"'")

                                    else:
                                        #process as string in case filename has spaces (works only if no params)
                                        results[this_mtl_name]._map_filename_dict[command] = args_string
                                        # (no params)
                                        #results[this_mtl_name]._map_diffuse_filename = args_string
                                else:
                                    print(filename+" ("+str(line_counting_number)+",0): (NOT YET IMPLEMENTED) unknown material command '"+command+"'")
                            else:
                                print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) material command before 'newmtl'")
                        else:
                            print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) no arguments after command")
                    else:
                        print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) no space after command")
                else:
                    if len(line_strip)>0:
                        comment_notag = line_strip[1:].strip()
                        if len(comment_notag) > 0:
                            if this_mtl_name is not None:
                                if results[this_mtl_name] is not None:
                                    results[this_mtl_name].append_opening_comment(comment_notag)
                                else:
                                    comments.append(comment_notag)
                            else:
                                comments.append(comment_notag)
                line_counting_number += 1
            #end for lines in file
        else:
            print("ERROR in get_wmaterial_dict_from_mtl: missing file or cannot access '"+filename+"'")
    except:
        #e = sys.exc_info()[0]
        #print("Could not finish get_wmaterial_dict_from_mtl:" + str(e))
        print("Could not finish get_wmaterial_dict_from_mtl:")
        view_traceback()
    return results

texcoords_not_2_warning_enable = True
NYI_s_enable = True
short_name_in_messages_enable = True

def show_object_faces_msg(this_object, name_msg):
    faces_msg = "...WARNING: got None for this_object.face_groups!"
    if this_object.face_groups is not None:
        key_count = 0
        face_count = 0
        faces_msg = "...WARNING: this_object face groups contain 0 faces!"
        group_err = None
        for key in this_object.face_groups:
            if this_object.face_groups[key] != None:
                if this_object.face_groups[key].faces is not None:
                    face_count += len(this_object.face_groups[key].faces)
                else:
                    print(name_msg+" ERROR: object named '"+str(this_object.name)+"' resulted in a group with a faces list that is None")
            else:
                print(name_msg+" ERROR: object named '"+str(this_object.name)+"' resulted in a group that is None")
            key_count += 1
        if face_count == 0:
            faces_msg = "...WARNING: 0 FACES!"
        else:
            faces_msg = "..."+str(face_count)+" face(s)"
    print(name_msg+": object named "+str(this_object.name)+""+faces_msg)
    

class WObjFile:
    wobjects = None

    def load(self, filename):
        self.wobjects = self.get_wobjects_list(filename)

    def get_wobjects_list(self, filename):  # formerly import_obj formerly get_wobjects_from_obj
        added_face_msg_enable = True
        name_msg = filename
        if short_name_in_messages_enable:
            name_msg = os.path.basename(os.path.normpath(filename))
        texcoord_number_warning_enable = True
        global texcoords_not_2_warning_enable
        global NYI_s_enable
        results = None
        try:
            if os.path.exists(filename):
                command = None
                prev_command = None
                prev_usable_command = None
                results = list()
                result_index = -1
                comments = list()
                this_object = None
                line_counting_number = 1
                this_mtl_filename = None
                materials = None
                #start offsets at 1 since obj file uses counting numbers
                #v_offset = 1
                #vt_offset = 1
                #vn_offset = 1
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
                this_g_name = None
                this_o_name = None
                untitled_number = 1  # for non-spec objects that also have no non-spec name (such as `# object object_name`) specified
                unused_g_number = 1  # collisions should be detected before use
                g_names = []  # just for detecting duplicates
                this_face_group = None
                this_face_group_type = None  # s or g
                this_face_group_name = None  # name property of this_face_group
                this_face_group_key = None
                for line in open(filename, "r"):
                    line_strip = line.strip()
                    while ("\t" in line_strip):
                        line_strip = line_strip.replace("\t", " ")
                    while ("  " in line):
                        line = line.replace("  ", " ")
                    if (len(line_strip)>0) and (line_strip[0]!="#"):
                        if this_object is not None:
                            this_object.has_any_data_enable = True
                        space_index = line_strip.find(" ")
                        args_string = ""
                        if space_index>-1:
                            command = line_strip[:space_index]
                            if len(line_strip) >= (space_index+1):  #TODO: audit this weird check
                                args_string = line_strip[space_index+1:].strip()
                        else:
                            command = line_strip
                        if len(args_string)>0:
                            params = args_string.split(" ")  # line_strip[space_index+1:].strip()
                        else:
                            params = []
                        if command=="mtllib":
                            this_mtl_filename = args_string
                            if (this_mtl_filename[:2]=="./") or (this_mtl_filename[:2]==".\\"):
                                this_mtl_filename = this_mtl_filename[2:]
                            this_mesh_folder_path = os.path.dirname(os.path.abspath(filename))
                            this_mtl_path = this_mtl_filename
                            if (len(this_mesh_folder_path)>0):
                                this_mtl_path = os.path.join(this_mesh_folder_path, this_mtl_filename)
                            materials = get_wmaterial_dict_from_mtl(this_mtl_path)
                        elif command=="o":
                            if len(params) > 0:
                                this_o_name = params[0]  # this_object.name = params[0]
                        elif command=="g":
                            this_face_group_type = "g"
                            if len(params) > 0:
                                this_g_name = params[0]  # this_object.name = params[0]
                        elif command=="v":
                            if prev_usable_command != command:
                                #this is non-spec to account for non-spec v commands that aren't preceded by `o` command
                                if this_object is not None:
                                    results.append(this_object)
                                    show_object_faces_msg(this_object, name_msg)
                                    result_index += 1  # ok since starts at -1
                                    this_object = None
                                    #v_offset += len(this_object.vertices)
                                    #vt_offset += len(this_object.texcoords)
                                    #vn_offset += len(this_object.normals)
                                v_map = dict()
                                vt_map = dict()
                                vn_map = dict()
                                this_object = WObject()
                                if this_o_name is None:
                                    this_o_name = "untitled_" + str(untitled_number)
                                    untitled_number += 1
                                this_object.name = this_o_name
                                this_o_name = None
                                this_vertex_group_type = None
                                this_object.source_path = filename
                                this_object.mtl_filename = this_mtl_filename
                                this_wobject_v_count = 0
                                this_wobject_vt_count = 0
                                this_wobject_vn_count = 0
                                if len(comments)>0:
                                    for i in range(0,len(comments)):
                                        this_object.append_opening_comment(comments[i])
                                    #comments[:] = []
                                    del comments[:]
                                    #comments.clear()  # requires python 3.3 or later
                            #NOTE: references a v by vertex# are relative to file instead of 'o', but this is detected & fixed at end of this method (for each object discovered) since file may not match spec
                            if this_object.vertices is None:
                                this_object.vertices = list()
                            args = args_string.split(" ")
                            result_v = (0.0, 0.0, 0.0)
                            if len(args)>=7:
                                result_v = get_fvec7(args)  #allow nonstandard x,y,z,r,g,b,a (position then color) format
                            elif len(args)>=6:
                                result_v = get_fvec6(args)  #allow nonstandard x,y,z,r,g,b (position then color) format
                            elif len(args)>=3:
                                result_v = get_fvec3(args)
                            if len(args)!=3 and len(args)!=6 and len(args)!=7:
                                print(name_msg+" ("+str(line_counting_number)+",0): (INPUT WARNING) vertex must have 3 total coordinate values (or 3 followed by 3 to 4 color channels for 6 to 7 total): '"+args_string+"'")
                                if len(args)>=2:
                                    result_v = get_fvec3( (args[0], 0.0, args[1]) )  #assume x,z for 2d vert
                                if len(args)>=1:
                                    result_v = get_fvec3( (args[0], 0.0, 0.0) )  #assume x,z for 2d vert
                            #this_object.vertices.append(result_v)
                            absolute_v_list.append(result_v)
                            absolute_v_count += 1
                            #v_offset += 1                            
                        elif this_object is not None:
                            if command=="vt":
                                args = args_string.split(" ")
                                result_vt = (0.0, 0.0)
                                if len(args)>=2:
                                    result_vt = get_fvec2(args)
                                if (texcoords_not_2_warning_enable):
                                    if (len(args)!=2):
                                        if (len(args)<2):
                                            print(name_msg+" ("+str(line_counting_number)+",0): (INPUT ERROR) texcoord missing coordinate (expected u v after vt but only got one param) so texture may not be applied correctly: '"+args_string+"'")
                                        else:
                                            if len(args)!=3:
                                                print(name_msg+" ("+str(line_counting_number)+",0): (INPUT ERROR) texcoords must have 2 (vt u v) or 3 (vt u v w) coordinates: '"+args_string+"'")
                                            else:
                                                print(name_msg+" ("+str(line_counting_number)+",0): (INPUT WARNING / NOT YET IMPLEMENTED) texcoord with 3 coordinates (vt u v w) so w may be ignored: '"+args_string+"'")
                                        print("(this is the last texcoords input warning that will be shown)")
                                        print("")
                                        texcoords_not_2_warning_enable = False
                                #this_object.texcoords.append(result_vt)
                                absolute_vt_list.append(result_vt)
                                absolute_vt_count += 1
                                #still increment since is reference to index obj file:
                                #vt_offset += 1

                            elif command=="vn":
                                #NOTE: presence of normals supercedes smoothing groups
                                args = args_string.split(" ")
                                result_vn = (0.0, 0.0, 0.0)
                                if len(args)>=3:
                                    result_vn = get_fvec3(args)
                                if len(args)!=3:
                                    print(name_msg+" ("+str(line_counting_number)+",0): (INPUT ERROR) normal must have 3 coordinates: '"+args_string+"'")
                                #this_object.normals.append(result_vn)
                                absolute_vn_list.append(result_vn)
                                absolute_vn_count += 1
                                #vn_offset += 1
                            elif command=="f":
                                if prev_usable_command != command:
                                    #if this_object.faces is None:
                                    #    this_object.faces = []
                                    if this_object.face_groups is None:
                                        this_object.face_groups = {}
                                    this_face_group = WFaceGroup()
                                    this_face_group.faces = []
                                    if this_face_group_name is None:
                                        this_face_group_name = str(unused_g_number)
                                        while this_face_group_name in this_object.face_groups:
                                            unused_g_number += 1
                                            this_face_group_name = str(unused_g_number)
                                    this_face_group.face_group_type = this_face_group_type
                                    this_face_group_type = None
                                    this_object.face_groups[this_face_group_name] = this_face_group
                                    this_face_group_key = this_face_group_name
                                    this_face_group_name = None                                    
                                
                                args = args_string.split(" ")
                                this_face = []
                                for i in range(0,len(args)):
                                    absolute_v_index = None
                                    absolute_vt_index = None
                                    absolute_vn_index = None
                                    vertex_number = None
                                    texcoord_number = None
                                    normal_number = None
                                    values = args[i].split("/")
                                    #subtract offsets from values since obj file not only uses counting numbers but also numbers unique in entire file (as opposed to starting over for each object):
                                    if len(values)>=1:
                                        values[FACE_V] = values[FACE_V].strip()
                                        if len(values[FACE_V])>0:  # if not blank string
                                            stated_v_number = int(values[FACE_V])
                                            if stated_v_number>=1:
                                                absolute_v_index = stated_v_number - 1
                                                vertex_number = this_wobject_v_count  # ok since adding it below
                                            elif stated_v_number<0:  # negative index is relative in obj standard
                                                absolute_v_index = absolute_v_count + stated_v_number  # + since negative
                                                vertex_number = this_wobject_v_count  # ok since adding it below
                                            else:
                                                print("  WARNING: vertex number 0 on obj is nonstandard and will be skipped")
                                            if absolute_v_index is not None:
                                                abs_v_i_s = str(absolute_v_index)
                                                if abs_v_i_s in v_map:
                                                    absolute_v_index = None  # prevents copying same one to wobject again below
                                                    vertex_number = v_map[abs_v_i_s]
                                                else:
                                                    v_map[abs_v_i_s] = vertex_number
                                    if len(values)>=2:
                                        values[FACE_TC] = values[FACE_TC].strip()
                                        if len(values[FACE_TC])>0:  # if not blank string
                                            #texcoord_number = int(values[FACE_TC])-vt_offset
                                            stated_texcoord_number = int(values[FACE_TC])
                                            if stated_texcoord_number>=1:
                                                absolute_vt_index = stated_texcoord_number - 1
                                                texcoord_number = this_wobject_vt_count  # ok since adding it below
                                            elif stated_texcoord_number<0:  # negative index is relative in obj standard
                                                absolute_vt_index = absolute_v_count + stated_v_number  # + since negative
                                                texcoord_number = this_wobject_vt_count  # ok since adding it below
                                            else:
                                                print("  WARNING: texcoord number 0 on obj is nonstandard and will be skipped")
                                            if absolute_vt_index is not None:
                                                abs_vt_i_s = str(absolute_vt_index)
                                                if abs_vt_i_s in vt_map:
                                                    absolute_vt_index = None  # prevents copying same one to wobject again below
                                                    texcoord_number = vt_map[abs_vt_i_s]
                                                else:
                                                    vt_map[abs_vt_i_s] = texcoord_number
                                    if len(values)>=3:
                                        values[FACE_VN] = values[FACE_VN].strip()
                                        if len(values[FACE_VN])>0:  # if not blank string
                                            #normal_number = int(values[FACE_VN])-vn_offset
                                            stated_normal_number = int(values[FACE_VN])
                                            if stated_normal_number>=1:
                                                absolute_vn_index = stated_normal_number - 1
                                                normal_number = this_wobject_vn_count  # ok since adding it below
                                            elif stated_normal_number<0:  # negative index is relative in obj standard
                                                absolute_vn_index = absolute_vn_count + stated_normal_number  # + since negative
                                                normal_number = this_wobject_vn_count  # ok since adding it below
                                            else:
                                                print("  WARNING: normal number 0 on obj is nonstandard and will be skipped")
                                            if absolute_vn_index is not None:
                                                abs_vn_i_s = str(absolute_vn_index)
                                                if abs_vn_i_s in vn_map:
                                                    absolute_vn_index = None  # prevents copying same one to wobject again below
                                                    normal_number = vn_map[abs_vn_i_s]
                                                else:
                                                    vn_map[abs_vn_i_s] = normal_number
                                    if absolute_v_index is not None:
                                        if this_object.vertices is None:
                                            this_object.vertices = list()
                                        v_num_s = str(vertex_number)
                                        this_object.vertices.append(absolute_v_list[absolute_v_index])
                                        individuated_v_count += 1
                                        this_wobject_v_count += 1
                                    if absolute_vt_index is not None:
                                        if this_object.texcoords is None:
                                            this_object.texcoords = list()
                                        vt_num_s = str(texcoord_number)
                                        this_object.texcoords.append(absolute_vt_list[absolute_vt_index])
                                        this_wobject_vt_count += 1
                                    if absolute_vn_index is not None:
                                        if this_object.normals is None:
                                            this_object.normals = list()
                                        vn_num_s = str(normal_number)
                                        this_object.normals.append(absolute_vn_list[absolute_vn_index])
                                        this_wobject_vn_count += 1
                                    if texcoord_number_warning_enable:
                                        if texcoord_number is None:
                                            print(name_msg+" ("+str(line_counting_number)+",0): (PARSER WARNING) vertex texcoord_number is None when adding to face")
                                            print("(this is the last texcoord_number warning that will be shown for this input file)")
                                            print("")
                                            texcoord_number_warning_enable = False
                                    this_face.append([vertex_number,texcoord_number,normal_number])
                                this_object.face_groups[this_face_group_key].faces.append( this_face )
                                if added_face_msg_enable:
                                    #print("added face to '"+str(this_object.name)+"' group '"+this_face_group_key+"': "+str(this_face))
                                    #added_face_msg_enable = False  # commented for debug only
                                    if not added_face_msg_enable:
                                        print("(this is the last face message that will be shown for this input file)")
                                        print("")
                            elif command=="usemtl":
                                if materials is not None:
                                    if args_string in materials.keys():
                                        this_object.wmaterial = materials[args_string]  # get_by_name(materials,args_string)
                                        if this_object.wmaterial is None:
                                            print(name_msg+" ("+str(line_counting_number)+",0): (INPUT ERROR) wmaterial named '"+args_string+"' is None")
                                    else:
                                        print(name_msg+" ("+str(line_counting_number)+",0): (INPUT ERROR) unknown wmaterial name '"+args_string+"'")
                                else:
                                    print(name_msg+" ("+str(line_counting_number)+",0): (INPUT ERROR) usemtl '"+args_string+"' is impossible since a material was not loaded with mtllib command first.")
                            elif command=="s":
                                if args_string=="off":
                                    this_face_group_type = None
                                    this_face_group_name = None
                                else:
                                    this_face_group_type = "s"
                                    this_face_group_name = args_string
                            else:
                                print(name_msg+" ("+str(line_counting_number)+",0): (INPUT ERROR) unknown object command '"+command+"'")
                        else:
                            print(name_msg+" ("+str(line_counting_number)+",0): (INPUT ERROR) object command '"+command+"' before 'o'")
                        #else:
                        #    print(name_msg+" ("+str(line_counting_number)+",0): (INPUT ERROR) no arguments after command")
                        #else:
                        #    print(name_msg+" ("+str(line_counting_number)+",0): (INPUT ERROR) no space after command")
                        prev_command = command
                        prev_usable_command = command
                        
                    else:
                        if len(line_strip)>0:
                            comment_notag = line_strip[1:].strip()
                            if len(comment_notag) > 0:
                                if this_object is not None:
                                    this_object.append_opening_comment(comment_notag)
                                #if (this_object is None) or (not this_object.has_any_data_enable):
                                if this_o_name is None:
                                    chunks = comment_notag.split(" ")
                                    if (chunks is not None) and (len(chunks) > 1):
                                        if chunks[0].lower() == "object":
                                            if this_o_name is None:
                                                this_o_name = chunks[1]
                                            else:
                                                print("NOTICE: skipping non-standard commented name '"+chunks[1]+"' since object is already named '" + this_object.name + "'")
                                else:
                                    comments.append(comment_notag)
                        prev_command = None
                    line_counting_number += 1
                #end for lines in file
                #NOTE: "finalize_obj" code is no longer needed since offsets were already applied above and original format is kept intact (indices instead of opengl-style vertex info array)
                if this_object is not None:
                    results.append(this_object)
                    show_object_faces_msg(this_object, name_msg)
                    print(name_msg+": has a total of "+str(len(absolute_v_list))+" vertices loaded as "+str(individuated_v_count)+" vertices")
                    this_object = None
            else:
                print("ERROR in get_wobjects_from_obj: missing file or cannot access '"+filename+"'")
        except:
            print("ERROR: Could not finish get_wobjects_from_obj '"+filename+"':")
            view_traceback()
        if results is not None:
            if len(results)<1:
                print("WARNING: get_wobjects_list (usually called by wobjfile.load) got 0 objects from '" + filename + "'")
        #else ignore since already has file does not exist error
            
        return results




