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

#these are needed since in python 3, int is no longer bounded:
MIN_INDEX = -9223372036854775807
MAX_INDEX = 9223372036854775808

FACE_V = 0  # index of vertex index in the face which is a list
FACE_TC = 1  # index of vertex index in the face which is a list
FACE_VN = 2  # index of vertex index in the face which is a list

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
    return (float(values[start_index]), float(values[start_index+1]), float(values[start_index+1]))

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
    
    def set_from_illumination_model_number(number):
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

class WColorArgInfo():
    _param = None
    _value_min_count = None
    _value_max_count = None
    _description = None
    _value_descriptions = None
    
    def __init__(param, description, value_min_count, value_max_count, value_descriptions):
        self._param = param
        self._description = description
        self._value_min_count = value_min_count
        self._value_max_count = value_max_count


#http://paulbourke.net/dataformats/mtl/ says:
#To specify the ambient reflectivity of the current material, you can 
#use the "Ka" statement, the "Ka spectral" statement, or the "Ka xyz" 
#statement. Tip	These statements are mutually exclusive.
color_arg_type_strings = list()
color_arg_type_strings.append(WColorArgInfo("type","type",1,1,["type, such as type of reflection"]))
color_arg_type_strings.append(WColorArgInfo("spectral","spectral curve",1,2,["filename","factor"]))
color_arg_type_strings.append(WColorArgInfo("xyz","specifies that the values are in CIEXYZ colorspace",3,3,["X for CIEXYZ","Y for CIEXYZ","Z for CIEXYZ"]))
color_arg_type_strings.append(WColorArgInfo("blendu","blend U in map",1,1,["on|off"]))
color_arg_type_strings.append(WColorArgInfo("blendv","blend V in map",1,1,["on|off"]))
color_arg_type_strings.append(WColorArgInfo("clamp","clamp to 0-1 in UV range",1,1,["on|off"]))
color_arg_type_strings.append(WColorArgInfo("cc","color correction (only for map_Ka, map_Kd, and map_Ks)",1,1,["on|off"]))
color_arg_type_strings.append(WColorArgInfo("mm","base gain",2,2,["black level"|"white level (processed before black level, so acts as range)"]))
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
# 	-blendu on | off
# 	-blendv on | off
# 	-cc on | off
# 	-clamp on | off
# 	-mm base gain
# 	-o u v w
# 	-s u v w
# 	-t u v w
# 	-texres value


def find_by_name(object_list, needle):
    result = None
    for i in range(0,len(object_list)):
        try:
            if object_list[i].name == needle:
                result = object_list[i]
                break
        except:
            e = sys.exc_info()[0]
            print("Could not finish find_by_name:" + str(e))
    return result


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
    
    _map_ambient_filename = None  # map_Ka
    _map_diffuse_filename = None  # map_Kd
    _map_specular_color_filename = None    # map_Ks
    _map_specular_highlight_filename = None    # map_Ns --just a regular image, but used as gray (values for exponent)
    _map_transparency_filename = None  # map_d
    _map_bump_filename = None  # map_bump or bump: use luminance
    _map_displacement = None  # disp
    _map_decal = None # decal: stencil; defaults to 'matte' channel of image
    _map_reflection = None  # refl; can be -type sphere
    
    
    def __init__(name=None):
        self.name = name
        self._opacity = 1.0
        
    def append_opening_comment(self, text):
        if self._opening_comments is None:
            self._opening_comments = list()
        self._opening_comments.append(text)


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
    #endregion raw OBJ data
    mtl_filename = None
    material_name = None
    vertices = None  # v
    texcoords = None  # vt (uv point in texture from 0.0 to 1.0); aka vertex_uvs
    normals = None  # vn
    faces = None  # f; vertex#/texcoord#/normal# were *# is a counting number starting at 1 -- only vertex# is required (but // is used if texcoord# is not present but normal# is).

    _opening_comments = None
    
    def __init__(name=None):
        self._name = name
        
    def append_opening_comment(self, text):
        if self._opening_comments is None:
            self._opening_comments = list()
        self._opening_comments.append(text)


def get_wmaterials_from_mtl(filename):
    results = None
    try:
        if os.path.exists(filename):
            results = list()
            comments = list()
            this_material = None
            line_counting_number = 1
            for line in open(filename, "r"):
                line_strip = line.strip()
                if (len(line_strip)>0) and (line_strip[0]!="#"):
                    space_index = line_strip.find(" ")
                    if space_index>-1:
                        if len(line_strip) => (space_index+1):
                            args_string = line_strip[space_index+1].strip()
                        if len(args_string)>0:
                            command = line_strip[:space_index]
                            if (this_material is not None) or (command == "newmtl"):
                                params = line_strip[space_index+1:]
                                if command=="newmtl":
                                    this_material = WMaterial(name=args_string)
                                    results.append(this_material)
                                elif command=="illum":
                                    this_illum = WIlluminationModel()
                                    result=this_illum.set_from_illumination_model_number(int(args_string))
                                    if result:
                                        this_material._illumination_model = this_illum
                                    else:
                                        print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) unknown illumination model number '"+args_string+"'")
                                elif command=="d":
                                    halo_string = " -halo "
                                    if len(args_string)>=halo_string:
                                        if args_string[:len(halo_string)]==halo_string:
                                            #TODO: halo formula: dissolve = 1.0 - (N*v)(1.0-factor)
                                            args_string=args_string[len(halo_string):]
                                            print(filename+" ("+str(line_counting_number)+",0): (NOT YET IMPLEMENTED) halo, so using next value as plain opacity value instead")
                                    this_opacity = float(args_string)
                                    if (this_opacity>=0.0) and (this_opacity<=1.0):
                                        this_material._opacity = this_opacity
                                    else:
                                        print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) invalid opacity '"+args_string+"' so using '"+str(this_material._opacity)+"' instead")
                                elif command=="Tr":
                                    this_transparency = float(args_string)
                                    if (this_transparency>=0.0) and (this_transparency<=1.0):
                                        this_material._opacity = 1.0-this_transparency
                                    else:
                                        print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) invalid transparency '"+args_string+"' so using '"+str(this_material._opacity)+"' instead")
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
                                            this_material._diffuse_color = [float(diffuse_color[len(diffuse_color)-3]), float(diffuse_color[len(diffuse_color)-2]), float(diffuse_color[len(diffuse_color)-1])]
                                        else:
                                            print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) color must have 3 values (r g b): '"+command+"'")
                                elif command=="map_Kd":
                                    this_material._map_diffuse_filename = args_string
                                    #TODO: see if starts with '-' then arg
                                    #args = args_string.split(" ")
                                    #this_material._map_diffuse_filename = args[len(args)-1]
                                    #if len(args)>1:
                                    #    print(filename+" ("+str(line_counting_number)+",0): (NOT YET IMPLEMENTED) map arguments were ignored (except filename): '"+args_string+"'")
                                else:
                                    print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) unknown material command '"+command+"'")
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
                            if this_material is not None:
                                this_material.append_opening_comment(comment_notag)
                            else:
                                comments.append(comment_notag)
                line_counting_number += 1
            #end for lines in file
        else:
            print("ERROR in get_wmaterials_from_mtl: missing file or cannot access '"+filename+"'")
    except:
        e = sys.exc_info()[0]
        print("Could not finish get_materials_from_mtl:" + str(e))
    return results


def get_wobjects_from_obj(filename):
    results = None
    try:
        if os.path.exists(filename):
            results = list()
            comments = list()
            this_object = None
            line_counting_number = 1
            this_mtl_filename = None
            materials = None
            smoothing_group = None
            for line in open(filename, "r"):
                line_strip = line.strip()
                if (len(line_strip)>0) and (line_strip[0]!="#"):
                    space_index = line_strip.find(" ")
                    if space_index>-1:
                        args_string = ""
                        if len(line_strip) => (space_index+1):
                            args_string = line_strip[space_index+1].strip()
                        if len(args_string)>0:
                            command = line_strip[:space_index]
                            params = line_strip[space_index+1:]
                            if command=="mtllib":
                                this_mtl_filename = args_string
                                materials = get_wmaterials_from_mtl(this_mtl_filename)
                            elif command=="o":
                                smoothing_group = None
                                this_object = WObject(name=args_string)
                                this_object.mtl_filename = this_mtl_filename
                                if len(comments)>0:
                                    for i in range(0,len(comments)):
                                        this_object.append_opening_comment(comments[i])
                                    #comments[:] = []
                                    del comments[:]
                                    #comments.clear()  # requires python 3.3 or later
                                results.append(this_object)
                            elif this_object is not None:
                                if command=="v":
                                    #NOTE: references a v by vertex# are relative to file instead of 'o', but this is detected & fixed at end of this method (for each object discovered) since file may not match spec
                                    if this_object.vertices is None:
                                        this_object.vertices = list()
                                    args = args_string.split(" ")
                                    if len(args)>=3:
                                        this_object.vertices.append(get_fvec3(args))
                                    if len(args)!=3:
                                        print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) vertex must have 3 coordinates: '"+args_string+"'")
                                elif command=="vt":
                                    if this_object.texcoords is None:
                                        this_object.texcoords = list()
                                    args = args_string.split(" ")
                                    if len(args)>=2:
                                        this_object.texcoords.append(get_fvec2(args))
                                    if len(args)!=2:
                                        print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) texcoords must have 2 coordinates: '"+args_string+"'")
                                elif command=="vn":
                                    #NOTE: presence of normals supercedes smoothing groups
                                    if this_object.normals is None:
                                        this_object.normals = list()
                                    args = args_string.split(" ")
                                    if len(args)>=3:
                                        this_object.normals.append(get_fvec3(args))
                                    if len(args)!=3:
                                        print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) normal must have 3 coordinates: '"+args_string+"'")
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
                                        if len(values)>=1:
                                            if len(values[FACE_V])>0:
                                                vertex_number = int(values[FACE_V])-1
                                        if len(values)>=2:
                                            if len(values[FACE_TC])>0:
                                                texcoord_number = int(values[FACE_TC])-1
                                        if len(values)>=3:
                                            if len(values[FACE_VN])>0:
                                                normal_number = int(values[FACE_VN])-1
                                        this_object.faces.append( [vertex_number,texcoord_number,normal_number] )
                                elif command=="usemtl":
                                    this_object.material = find_by_name(args_string)
                                    if this_object.material is None:
                                        print(filename+" ("+str(line_counting_number)+",0): (INPUT ERROR) unknown material '"+args_string+"'")
                                elif command=="s":
                                    if args_string=="off":
                                        smoothing_group = None
                                    else:
                                        smoothing_group = args_string
                                    print(filename+" ("+str(line_counting_number)+",0): (NOT YET IMPLEMENTED) smoothing group command '"+command+"'")
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
            vertex_count = 0
            for result_index in range(0,len(results)):
                this_object = results[result_index]
                vertex_count += len(this_object.vertices)
                texcoord_count += len(this_object.texcoords)
                normal_count += len(this_object.normals)
                if result_index>0:
                    #Intentionally use max for min and the reverse, so that actual min/max can be found by comparison:
                    min_v_index = MAX_INDEX
                    max_v_index = MIN_INDEX
                    min_vt_index = MAX_INDEX
                    max_vt_index = MIN_INDEX
                    min_vn_index = MAX_INDEX
                    max_vn_index = MIN_INDEX
                    for face_index in range(0,this_object.faces):
                        #NOTE: 1 was already subtracted from each index upon conversion to int above
                        this_face = this_object.faces[face_index]
                        if this_face[FACE_V] is not None
                            if this_face[FACE_V] > max_v_index:
                                max_v_index = this_face[FACE_V]
                            if this_face[FACE_V] < min_v_index:
                                min_v_index = this_face[FACE_V]
                        if this_face[FACE_VT] is not None
                            if this_face[FACE_VT] > max_vt_index:
                                max_vt_index = this_face[FACE_VT]
                            if this_face[FACE_VT] < min_vt_index:
                                min_vt_index = this_face[FACE_VT]
                        if this_face[FACE_VN] is not None
                            if this_face[FACE_VN] > max_vn_index:
                                max_vn_index = this_face[FACE_VN]
                            if this_face[FACE_VN] < min_vn_index:
                                min_vn_index = this_face[FACE_VN]
                    #debug assumes
                    for face_index in range(0,this_object.faces):
                
        else:
            print("ERROR in get_wobjects_from_obj: missing file or cannot access '"+filename+"'")
    return results


ILLUMINATIONMODEL_DESCRIPTION_STRINGS = ["Color on and Ambient off","Color on and Ambient on","Highlight on","Reflection on and Ray trace on","Transparency: Glass on, Reflection: Ray trace on","Reflection: Fresnel on and Ray trace on","Transparency: Refraction on, Reflection: Fresnel off and Ray trace on","Transparency: Refraction on, Reflection: Fresnel on and Ray trace on","Reflection on and Ray trace off","Transparency: Glass on, Reflection: Ray trace off","Casts shadows onto invisible surfaces"]

def get_illumination_model_description(illuminationModelIndex):
    #global ILLUMINATIONMODEL_DESCRIPTION_STRINGS
    resultString = None
    if (illuminationModelIndex>=0) and (illuminationModelIndex<len(ILLUMINATIONMODEL_DESCRIPTION_STRINGS)):
        ILLUMINATIONMODEL_DESCRIPTION_STRINGS[illuminationModelIndex]
    return resultString


