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




class WMaterial:

    name = None
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
def append_dump_as_yaml_array(thisList, thisName, sourceList, tabStringMinimum):
    tabString="  "
    thisList.append(tabStringMinimum+thisName+":")
    for i in range(0,len(sourceList)):
        thisList.append(tabStringMinimum+tabString+"- "+str(sourceList[i]))


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
    parameter_space_vertices = None  #only for curves--not really implemented, just loaded from obj
    mtl_filename = None
    material_name = None
    vertices = None  # v
    texcoords = None  # vt (uv point in texture where each coord is from 0.0 to 1.0); aka vertex_uvs
    normals = None  # vn
    faces = None  # f; vertex#/texcoord#/normal# were *# is a counting number starting at 0 (BUT saved as 1)-- only vertex# is required (but // is used if texcoord# is not present but normal# is).
    wmaterial = None
    name = None

    _opening_comments = None

    def __init__(self, name=None):
        self.name = name

    def append_opening_comment(self, text):
        if self._opening_comments is None:
            self._opening_comments = list()
        self._opening_comments.append(text)

    def append_dump(self, thisList, tabStringMinimum):
        if self.obj_path is not None:
            thisList.append(tabStringMinimum+tabString+"obj_path: "+self.obj_path)
        thisList = append_dump_as_yaml_array(thisList, "vertices",self.vertices,tabStringMinimum+tabString)
        thisList = append_dump_as_yaml_array(thisList, "texcoords",self.texcoords,tabStringMinimum+tabString)
        thisList = append_dump_as_yaml_array(thisList, "normals",self.normals,tabStringMinimum+tabString)
        thisList = append_dump_as_yaml_array(thisList, "_vertex_strings",self._vertex_strings,tabStringMinimum+tabString)
        thisList = append_dump_as_yaml_array(thisList, "parameter_space_vertices",self.parameter_space_vertices,tabStringMinimum+tabString)
        thisList = append_dump_as_yaml_array(thisList, "faces",self.faces,tabStringMinimum+tabString)


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
                if (len(line_strip)>0) and (line_strip[0]!="#"):
                    space_index = line_strip.find(" ")
                    if space_index>-1:
                        args_string = ""
                        if len(line_strip) >= (space_index+1):  #TODO: audit this weird check
                            args_string = line_strip[space_index+1:].strip()
                        if len(args_string)>0:
                            command = line_strip[:space_index].strip()
                            if (this_mtl_name is not None) or (command == "newmtl"):
                                badspace="\t"
                                badspace_index = args_string.find(badspace)
                                while badspace_index > -1:
                                    args_string = replace(args_string, badspace, " ")
                                    badspace_index = args_string.find(badspace)

                                badspace="  "
                                badspace_index = args_string.find(badspace)
                                while badspace_index > -1:
                                    args_string = replace(args_string, badspace, " ")
                                    badspace_index = args_string.find(badspace)

                                params = args_string.split(" ")  # line_strip[space_index+1:].strip()
                                if command=="newmtl":
                                    this_mtl_name = args_string
                                    if this_mtl_name not in results.keys():
                                        results[this_mtl_name] = WMaterial(name=this_mtl_name)
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

class WObjFile:
    wobjects = None
    
    def load(self, filename):
        self.wobjects = self.get_wobjects_list(filename)

    def get_wobjects_list(self, filename):  # formerly import_obj formerly get_wobjects_from_obj    
        global texcoords_not_2_warning_enable
        results = None
        try:
            if os.path.exists(filename):
                results = list()
                result_index = -1
                comments = list()
                this_object = None
                line_counting_number = 1
                this_mtl_filename = None
                materials = None
                smoothing_group = None
                #start offsets at 1 since obj file uses counting numbers
                v_offset = 1
                vt_offset = 1
                vn_offset = 1
                for line in open(filename, "r"):
                    line_strip = line.strip()
                    nonstandard_o_signal_string = "# object "
                    if line_strip[0:len(nonstandard_o_signal_string)]==nonstandard_o_signal_string:
                        line_strip = "o "+line_strip[len(nonstandard_o_signal_string):]
                    if (len(line_strip)>0) and (line_strip[0]!="#"):
                        space_index = line_strip.find(" ")
                        if space_index>-1:
                            args_string = ""
                            if len(line_strip) >= (space_index+1):  #TODO: audit this weird check
                                args_string = line_strip[space_index+1:].strip()
                            if len(args_string)>0:
                                command = line_strip[:space_index]
                                params = args_string.split(" ")  # line_strip[space_index+1:].strip()
                                if command=="mtllib":
                                    this_mtl_filename = args_string
                                    materials = get_wmaterial_dict_from_mtl(this_mtl_filename)
                                elif command=="o":
                                    if this_object is not None:
                                        results.append(this_object)
                                        result_index += 1  # ok since starts at -1
                                        this_object = None
                                        #v_offset += len(this_object.vertices)
                                        #vt_offset += len(this_object.texcoords)
                                        #vn_offset += len(this_object.normals)
                                    smoothing_group = None
                                    this_object = WObject(name=args_string)
                                    this_object.mtl_filename = this_mtl_filename
                                    if len(comments)>0:
                                        for i in range(0,len(comments)):
                                            this_object.append_opening_comment(comments[i])
                                        #comments[:] = []
                                        del comments[:]
                                        #comments.clear()  # requires python 3.3 or later
                                elif this_object is not None:
                                    if command=="v":
                                        #NOTE: references a v by vertex# are relative to file instead of 'o', but this is detected & fixed at end of this method (for each object discovered) since file may not match spec
                                        if this_object.vertices is None:
                                            this_object.vertices = list()
                                        args = args_string.split(" ")
                                        if len(args)>=7:
                                            this_object.vertices.append(get_fvec7(args))  #allow nonstandard x,y,z,r,g,b,a format
                                        elif len(args)>=6:
                                            this_object.vertices.append(get_fvec6(args))  #allow nonstandard x,y,z,r,g,b format
                                        elif len(args)>=3:
                                            this_object.vertices.append(get_fvec3(args))
                                        if len(args)!=3 and len(args)!=6 and len(args)!=7:
                                            print(filename+" ("+str(line_counting_number)+",0): (INPUT WARNING) vertex must have 3 total coordinate values (or 3 followed by 3 to 4 color channels for 6 to 7 total): '"+args_string+"'")
                                        v_offset += 1
                                    elif command=="vt":
                                        if this_object.texcoords is None:
                                            this_object.texcoords = list()
                                        args = args_string.split(" ")
                                        if len(args)>=2:
                                            this_object.texcoords.append(get_fvec2(args))
                                        if (texcoords_not_2_warning_enable):
                                            if (len(args)<2):
                                                print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) texcoord missing coordinate (expected u v after vt but only got one param) so texture may not be applied correctly: '"+args_string+"'")
                                            elif len(args)!=2:
                                                if len(args)!=3:
                                                    print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) texcoords must have 2 (vt u v) or 3 (vt u v w) coordinates: '"+args_string+"'")
                                                else:
                                                    print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) texcoord with 3 coordinates (vt u v w) so w may be ignored: '"+args_string+"'")
                                            texcoords_not_2_warning_enable = False
                                                
                                        #still increment since is reference to index obj file:
                                        vt_offset += 1
                                        
                                    elif command=="vn":
                                        #NOTE: presence of normals supercedes smoothing groups
                                        if this_object.normals is None:
                                            this_object.normals = list()
                                        args = args_string.split(" ")
                                        if len(args)>=3:
                                            this_object.normals.append(get_fvec3(args))
                                        if len(args)!=3:
                                            print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) normal must have 3 coordinates: '"+args_string+"'")
                                        vn_offset += 1
                                    elif command=="f":
                                        if this_object.faces is None:
                                            this_object.faces = list()
                                        args = args_string.split(" ")
                                        this_face = list()
                                        for i in range(0,len(args)):
                                            vertex_number = None
                                            texcoord_number = None
                                            normal_number = None
                                            values = args[i].split("/")
                                            #subtract offsets from values since obj file not only uses counting numbers but also numbers unique in entire file (as opposed to starting over for each object):
                                            if len(values)>=1:
                                                values[FACE_V] = values[FACE_V].strip()
                                                if len(values[FACE_V])>0:  # if not blank string
                                                    vertex_number = int(values[FACE_V])-v_offset
                                            if len(values)>=2:
                                                values[FACE_TC] = values[FACE_TC].strip()
                                                if len(values[FACE_TC])>0:  # if not blank string
                                                    texcoord_number = int(values[FACE_TC])-vt_offset
                                            if len(values)>=3:
                                                values[FACE_VN] = values[FACE_VN].strip()
                                                if len(values[FACE_VN])>0:  # if not blank string
                                                    normal_number = int(values[FACE_VN])-vn_offset
                                            this_face.append([vertex_number,texcoord_number,normal_number])
                                        this_object.faces.append( this_face )
                                    elif command=="usemtl":
                                        if materials is not None:
                                            if args_string in materials.keys():
                                                this_object.wmaterial = materials[args_string]  # get_by_name(materials,args_string)
                                                if this_object.wmaterial is None:
                                                    print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) wmaterial named '"+args_string+"' is None")
                                            else:
                                                print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) unknown wmaterial name '"+args_string+"'")
                                        else:
                                            print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) usemtl '"+args_string+"' is impossible since a material was not loaded with mtllib command first.")
                                    elif command=="s":
                                        if args_string=="off":
                                            smoothing_group = None
                                        else:
                                            smoothing_group = args_string
                                        print(filename+" ("+str(line_counting_number)+",0): (NOT YET IMPLEMENTED) smoothing group command '"+command+"'")
                                        #NOTE: vertex normals supercede smoothing groups (which are based on faces) according to the obj format spec
                                    else:
                                        print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) unknown object command '"+command+"'")
                                else:
                                    print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) object command before 'o'")
                            else:
                                print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) no arguments after command")
                        else:
                            print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) no space after command")
                    else:
                        if len(line_strip)>0:
                            comment_notag = line_strip[1:].strip()
                            if len(comment_notag) > 0:
                                if this_object is not None:
                                    this_object.append_opening_comment(comment_notag)
                                else:
                                    comments.append(comment_notag)
                    line_counting_number += 1
                #end for lines in file
                #NOTE: "finalize_obj" code is no longer needed since offsets were already applied above and original format is kept intact (indices instead of opengl-style vertex info array)
                if this_object is not None:
                    results.append(this_object)
                    this_object = None
            else:
                print("ERROR in get_wobjects_from_obj: missing file or cannot access '"+filename+"'")
        except:
            print("Could not finish get_wobjects_from_obj '"+filename+"':")
            view_traceback()
        return results




