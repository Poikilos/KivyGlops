# Deprecated

* PyGlopMaterial was converted to a dict and replaced by *_material functions
```python
class PyGlopMaterial:
    #update copy constructor if adding/changing copyable members
    properties = None
    name = None
    mtl_path = None
        # mtl file path (only if based on WMaterial of WObject)

    # region vars based on OpenGL ES 1.1
    ambient_color = None  # vec4
    diffuse_color = None  # vec4
    specular_color = None  # vec4
    emissive_color = None  # vec4
    specular_exponent = None  # float
    # endregion vars based on OpenGL ES 1.1

    def __init__(self):
        self.properties = {}
        self.ambient_color = (0.0, 0.0, 0.0, 1.0)
        self.diffuse_color = (1.0, 1.0, 1.0, 1.0)
        self.specular_color = (1.0, 1.0, 1.0, 1.0)
        self.emissive_color = (0.0, 0.0, 0.0, 1.0)
        self.specular_exponent = 1.0

    def get_is_glop_material(self, o):
        result = False
        try:
            result = o._get_is_glop_material()
        except:
            pass
        return result

    def get_class_name(self):
        return "PyGlopMaterial"

    def _get_is_glop_material(self):
        # use this for duck-typing (try, and if exception, not glop)
        return True

    def new_material_method(self):
        return PyGlopMaterial()

    # copy should have override in subclass that calls copy_as_subclass
    # then adds subclass-specific values to that result
    def copy(self, depth=0):
        return copy_as_subclass(self.new_material_method, depth=depth+1)

    def copy_as_subclass(self, new_material_method, ancestors=[],
            depth=0):
        target = new_material_method()
        material_enable = False
        self_class_name = self.get_class_name()
        target_class_name = "unknown"
        try:
            target_class_name = target.get_class_name()
            material_enable = (target_class_name == self_class_name)
        except:
            pass
        if not material_enable:
            print("[ PyGlopMaterial ] WARNING: target "
                  + target_class_name + " is not self type "
                  + self_class_name)
        if self.properties is not None:
            if get_verbose_enable():
                print("[ PyGlopMaterial ] " + "  " * depth
                      + "calling get_dict_deepcopy")
            target.properties = get_dict_deepcopy(
                self.properties, depth=depth+1)
        target.name = self.name
        target.mtl_path = self.mtl_path
        target.ambient_color = self.ambient_color
        target.diffuse_color = self.diffuse_color
        target.specular_color = self.specular_color
        target.emissive_color = self.emissive_color
        target.specular_exponent = self.specular_exponent
        return target

    def emit_yaml(self, lines, min_tab_string):
        #lines.append(min_tab_string+this_name+":")
        if self.name is not None:
            lines.append(min_tab_string + "name: " + \
                         get_yaml_from_literal_value(self.name))
        if self.mtl_path is not None:
            lines.append(min_tab_string + "mtl_path: " + \
                         get_yaml_from_literal_value(self.mtl_path))
        for k,v in sorted(self.properties.items()):
            lines.append(min_tab_string + k + ": " + \
                         get_yaml_from_literal_value(v))
```
  * which also deprecates the related methods of PyGlop:
```python
    def get_is_glop_hitbox(self, o):
        result = False
        try:
            result = o._get_is_glop_hitbox()
        except:
            pass
        return result

    def get_is_glop_material(self, o):
        result = False
        try:
            result = o._get_is_glop_material()
        except:
            pass
        return result

```
  * and deprecates the following from kivyglops.py:
```python

class KivyGlopMaterial(PyGlopMaterial):

    def __init__(self):
        super(KivyGlopMaterial, self).__init__()

    def new_material_method(self):
        return KivyGlopMaterial()

    def get_class_name(self):
        return "KivyGlopMaterial"

    def copy(self, depth=0):
        target = None
        try:
            target = self.copy_as_subclass(depth=depth+1)
        except:
            print("[ KivyGlopMaterial ] ERROR--could not finish" +
                  " self.copy_as_subclass:")
            view_traceback()
        return target
```

* this was converted to a dict and replaced by *_hitbox functions
```python
class PyGlopHitBox:
    minimums = None
    maximums = None

    def __init__(self):
        self.minimums = [-0.25, -0.25, -0.25]
        self.maximums = [0.25, 0.25, 0.25]

    def copy(self, depth=0):
        target = PyGlopHitBox()
        target.minimums = copy.deepcopy(self.minimums)
        target.maximums = copy.deepcopy(self.maximums)
        return target

    def get_is_glop_hitbox(self, o):
        result = False
        try:
            o._get_is_glop_hitbox()
        except:
            pass
        return result

    # for duck-typing
    def _get_is_glop_hitbox(self):
        return True

    def get_class_name(self):
        return "PyGlopHitBox"

    def contains_vec3(self, pos):
        return pos[0]>=self.minimums[0] and pos[0]<=self.maximums[0] \
            and pos[1]>=self.minimums[1] and pos[1]<=self.maximums[1] \
            and pos[2]>=self.minimums[2] and pos[2]<=self.maximums[2]

    def __str__(self):
        return (str(self.minimums[0]) + " to " + str(self.maximums[0])
                + ",  " + str(self.minimums[1]) + " to "
                + str(self.maximums[1])
                + ",  " + str(self.minimums[2]) + " to "
                + str(self.maximums[2])
        )

    def emit_yaml(lines, min_tab_string):
        lines.append(min_tab_string + "minimums: "
                     + standard_emit_yaml(lines,
                                          min_tab_string+tab_string,
                                          self.minimums)
        )
        lines.append(min_tab_string + "maximums: "
                     + standard_emit_yaml(lines,
                                          min_tab_string+tab_string,
                                          self.maximums)
        )
```

* this was tacked onto the end of the else case (else keys is None) in deepcopy_with_my_type:
```python
                # try:
                    # if get_verbose_enable():
                        # print("[ PyGlop ] Calling copy.deepcopy on "
                              # + str(type(od)))
                    # new_dict = copy.deepcopy(od)
                # except:
                    # try:
                        # if isinstance(od, type(self)) and \
                                # depth >= 2:
                            # new_dict = None
                            # print("[ PyGlop ] deepcopy_with_my_type
                                  # + "manually avoided infinite"
                                  # + " recursion by refusing to copy"
                                  # + " a " + str(type(self)) + " at"
                                  # + " recursion depth " + str(depth))
                        # else:
                            # new_dict = od.copy()
                        # print("[ PyGlop ] (verbose message in"
                              # + " deepcopy_with_my_type) using"
                              # + " '.copy()' for "
                              # + str(type(od)))
                    # except:
                        # new_dict = od
                        # if get_verbose_enable():
                            # print("[ PyGlop ] (verbose message in "
                                  # + "deepcopy_with_my_type) using "
                                  # + "'=' for " + str(type(od)))

```

* formerly in set_as_actor_at (not needed since now actor_dict is overlayed onto defaults:
```python
            if a_glop.hit_radius is None:
                if "hit_radius" in actor_dict:
                    a_glop.hit_radius = actor_dict["hit_radius"]
                else:
                    a_glop.hit_radius = .5
            if "throw_speed" not in a_glop.actor_dict:
                a_glop.actor_dict["throw_speed"] = 15.
                # ignored if item has projectile_speed
            if "target_index" not in a_glop.actor_dict:
                a_glop.actor_dict["target_index"] = None
            if "moveto_index" not in a_glop.actor_dict:
                a_glop.actor_dict["moveto_index"] = None
            if "target_pos" not in a_glop.actor_dict:
                a_glop.actor_dict["target_pos"] = None
            if "land_units_per_second" not in a_glop.actor_dict:
                a_glop.actor_dict["land_units_per_second"] = 12.5
                    # since 45 KMh is average (45/60/60*1000)
            if "ranges" not in a_glop.actor_dict:
                a_glop.actor_dict["ranges"] = {}
            if "melee" not in a_glop.actor_dict["ranges"]:
                a_glop.actor_dict["ranges"]["melee"] = 0.5
            if "throw_arc" not in a_glop.actor_dict["ranges"]:
                a_glop.actor_dict["ranges"]["throw_arc"] = 10.
            if "inventory_index" not in a_glop.actor_dict:
                a_glop.actor_dict["inventory_index"] = -1
            if "inventory_items" not in a_glop.actor_dict:
                a_glop.actor_dict["inventory_items"] = []
            if "unarmed_melee_enable" not in a_glop.actor_dict:
                a_glop.actor_dict["unarmed_melee_enable"] = False
            if "clip_enable" in a_glop.actor_dict:
                a_glop.properties["clip_enable"] = clip_enable
                del a_glop.actor_dict["clip_enable"]
            else:
                a_glop.properties["clip_enable"] = True

```
* formerly in update_glsl when item hits ground and has projectile_dict:
```python
if self.glops[bumpable_index].item_dict is not None and ("as_projectile" not in self.glops[bumpable_index].item_dict):
    #save projectile settings before setting projectile_dict to None:
    self.glops[bumpable_index].item_dict["as_projectile"] = self.glops[bumpable_index].projectile_dict
```

* formerly append_wobject under setting this_face_list
```python
                        if this_face_list is not None:
                            #get offset
                            for faceIndex in range(0,len(this_face_list)):
                                for componentIndex in range(0,len(this_face_list[faceIndex])):
                                    #print("found face "+str(faceIndex)+" component "+str(componentIndex)+": "+str(this_face_list[faceIndex][componentIndex]))
                                    #print(str(this_face_list[faceIndex][vertexIndex]))
                                    #if (len(this_face_list[faceIndex][componentIndex])>=FACE_V):
                                    #TODO: audit this code:
                                    for vertexIndex in range(0,len(this_face_list[faceIndex][componentIndex])):
                                        #calculate new offsets, in case obj file was botched (for correct obj format, wobjfile.py changes indices so they are relative to wobject ('o' command) instead of file
                                        if componentIndex==FACE_V:
                                            thisVertexIndex = this_face_list[faceIndex][componentIndex][vertexIndex]
                                            #if vertices_offset is None or thisVertexIndex<vertices_offset:
                                                #vertices_offset = thisVertexIndex
                                        #if (len(this_face_list[faceIndex][componentIndex])>=FACE_TC):
                                        elif componentIndex==FACE_TC:
                                            thisTexCoordIndex = this_face_list[faceIndex][componentIndex][vertexIndex]
                                            #if texcoords_offset is None or thisTexCoordIndex<texcoords_offset:
                                                #texcoords_offset = thisTexCoordIndex
                                        #if (len(this_face_list[faceIndex][componentIndex])>=FACE_VN):
                                        elif componentIndex==FACE_VN:
                                            thisNormalIndex = this_face_list[faceIndex][componentIndex][vertexIndex]
                                            #if normals_offset is None or thisNormalIndex<normals_offset:
                                                #normals_offset = thisNormalIndex
                            #if vertices_offset is not None:
                                #print("detected vertices_offset:"+str(vertices_offset))
                            #if texcoords_offset is not None:
                                #print("detected texcoords_offset:"+str(texcoords_offset))
                            #if normals_offset is not None:
                                #print("detected normals_offset:"+str(normals_offset))
                #obj format stores faces like (quads are allowed such as in following examples):
                #this_wobject_this_face 1399/1619 1373/1593 1376/1596 1400/1620
                #format is:
                #this_wobject_this_face VERTEX_I VERTEX_I VERTEX_I VERTEX_I
                #or
                #this_wobject_this_face VERTEX_I/TEXCOORDSINDEX VERTEX_I/TEXCOORDSINDEX VERTEX_I/TEXCOORDSINDEX VERTEX_I/TEXCOORDSINDEX
                #or
                #this_wobject_this_face VERTEX_I/TEXCOORDSINDEX/NORMALINDEX VERTEX_I/TEXCOORDSINDEX/NORMALINDEX VERTEX_I/TEXCOORDSINDEX/NORMALINDEX VERTEX_I/TEXCOORDSINDEX/NORMALINDEX
                #where *I are integers starting at 0 (stored starting at 1)
                #FACE_VERTEX_COMPONENT_VERTEX_INDEX = 0
                #FACE_VERTEX_COMPONENT_TEXCOORDS_INDEX = 1
                #FACE_VERTEX_COMPONENT_NORMAL_INDEX = 2
                #NOTE: in obj format, TEXCOORDS_INDEX is optional

                #FACE_VERTEX_COMPONENT_VERTEX_INDEX = 0
                #FACE_VERTEX_COMPONENT_TEXCOORDS_INDEX = 1
                #FACE_VERTEX_COMPONENT_NORMAL_INDEX = 2

                #nskrypnik put them in a different order than obj format (0,1,2) for some reason so do this order instead ONLY if using his obj loader:
                #FACE_VERTEX_COMPONENT_VERTEX_INDEX = 0
                #FACE_VERTEX_COMPONENT_TEXCOORDS_INDEX = 2
                #FACE_VERTEX_COMPONENT_NORMAL_INDEX = 1

                #use the following globals from wobjfile.py instead of assuming any FACE_VERTEX_COMPONENT values:
                #FACE_V  # index of vertex index in the face (since face is a list)
                #FACE_TC  # index of tc0 index in the face (since face is a list)
                #FACE_VN  # index of normal index in the face (since face is a list)
```

* changed to dicts (formerly in wobjfile.py):
```python

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
        self.face_group_type = None  # `g` or `s` or `s off`

    def emit_yaml(self, lines, min_tab_string):
        #lines.append(min_tab_string+this_list_name+":")
        name_line = "name: "
        if self.name is not None:
            name_line += self.name
        else:
            name_line += "~"
        lines.append(min_tab_string+name_line)
        if self.faces is not None:
            lines.append(min_tab_string+"faces:")
            for face in faces:
                lines.append(min_tab_string+tab_string+"- ")
                for vertex_i in face:
                    lines.append(min_tab_string+tab_string+tab_string+"- "+str(vertex_i))
        else:
            lines.append(min_tab_string+"faces: ~")


#use dict instead of this class
#see full spec at http://paulbourke.net/dataformats/mtl/
class WMaterial:

    name = None
    file_path = None  # for finding texture images more easily later
    _opening_comments = None
    _illumination_model = None
    _opacity = None # d (or 1.0-Tr)
    _ambient_color = None  # Ka
    _diffuse_color = None  # Kd
    _specular_color = None  # Ks; black is 'off' (same as None)
    _specular_exponent = None  # Ns (0 to 1000) "specular highlight component" ('hardness')

    # TODO: "sharpness" command specified sharpness of reflection 0 to 1000 default 60
    # where higher is more clear. "Sharpness values greater than 100 map
    # introduce aliasing effects in flat surfaces that are viewed at a sharp angle" - Ramey

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

```


* formerly part of class WObject in wobjfile.py:
```python
    #region raw OBJ data (as per nskrypnik)
    _name = None
    _vertex_strings = None
    _obj_cache_vertices = None
    _pivot_point = None
    _min_coords = None  #bounding cube minimums in local coordinates
    _max_coords = None  #bounding cube maximums in local coordinates
    texcoords = None
    normals = None
    parameter_space_vertices = None  #only for curves--not really implemented, just loaded from obj
    faces = None
    #endregion raw OBJ data (as per nskrypnik)
```

* formerly from kivyglops.py, but (PROBABLY) not needed since pyglops.py version of this method checks for type(self) instead of PyGlops now:
```python
def get_dict_deepcopy_with_my_type(self, old_dict, ref_my_type_enable=False):
        new_dict = None
        #if type(old_dict) is dict:
        new_dict = None
        keys = None
        if isinstance(old_dict, list):
            new_dict = []
            keys = range(0, len(old_dict))
        elif isinstance(old_dict, dict):
            new_dict = {}
            keys = old_dict.keys()
        #if keys is not None:
        #will fail if neither dict nor list (let it fail)
        for this_key in keys:
            if isinstance(old_dict[this_key], KivyGlop):
                if ref_my_type_enable:
                    if isinstance(new_dict, dict):
                        new_dict[this_key] = old_dict[this_key]
                    else:
                        new_dict.append(old_dict[this_key])
                else:
                    copy_of_var = None
                    if self.material is not None:
                        copy_of_var = old_dict[this_key].copy(self.new_glop_method, self.material.new_material_method)
                    else:
                        copy_of_var = old_dict[this_key].copy(self.new_glop_method, None)
                    if isinstance(new_dict, dict):
                        new_dict[this_key] = copy_of_var
                    else:
                        new_dict.append(copy_of_var)
            #TODO?: elif isinstance(old_dict[this_key], KivyGlopsMaterial)
            elif isinstance(old_dict[this_key], list):
                new_dict[this_key] = get_dict_deepcopy_with_my_type(old_dict[this_key], ref_my_type_enable)
            else:
                new_dict[this_key] = get_dict_deepcopy(old_dict[this_key])
        return new_dict
```

* formerly from __init__ in KivyGlops (formerly in KivyGlopsWindow)
```python
        self.camera_ax = 0
        self.camera_ay = 0
```

* instead, use new_glop_method method (never use `= PyGlop(`) to avoid needing this
```python
def get_kivyglop_from_pyglop(this_pyglop):
    this_kivyglop = KivyGlop()
    this_kivyglop.name = this_pyglop.name
    this_kivyglop.source_path = this_pyglop.source_path
    this_kivyglop.properties = this_pyglop.properties
    this_kivyglop.vertex_depth = this_pyglop.vertex_depth
    this_kivyglop.material = this_pyglop.material
    this_kivyglop._min_coords = this_pyglop._min_coords
    this_kivyglop._max_coords = this_pyglop._max_coords
    this_kivyglop._pivot_point = this_pyglop._pivot_point
    this_kivyglop.eye_height = this_pyglop.eye_height
    this_kivyglop.hit_radius = this_pyglop.hit_radius
    this_kivyglop.item_dict = this_pyglop.item_dict
    this_kivyglop.projectile_dict = this_pyglop.projectile_dict
    this_kivyglop.actor_dict = this_pyglop.actor_dict
    this_kivyglop.bump_enable = this_pyglop.bump_enable
    this_kivyglop.reach_radius = this_pyglop.reach_radius
    this_kivyglop.is_out_of_range = this_pyglop.is_out_of_range
    this_kivyglop.physics_enable = this_pyglop.physics_enable
    this_kivyglop.velocity[0] = this_pyglop.velocity[0]
    this_kivyglop.velocity[1] = this_pyglop.velocity[1]
    this_kivyglop.velocity[2] = this_pyglop.velocity[2]
    this_kivyglop._cached_floor_y = this_pyglop._cached_floor_y
    this_kivyglop.infinite_inventory_enable = this_pyglop.infinite_inventory_enable
    this_kivyglop.bump_sounds = this_pyglop.bump_sounds
    this_kivyglop.look_target_glop = this_pyglop.look_target_glop
    if this_pyglop.hitbox is not None:
        this_kivyglop.hitbox = this_pyglop.hitbox.copy()
    this_kivyglop.visible_enable = this_pyglop.visible_enable

    this_kivyglop.vertex_format = this_pyglop.vertex_format
    this_kivyglop.vertices = this_pyglop.vertices
    this_kivyglop.indices = this_pyglop.indices
    this_kivyglop.look_target_glop = this_pyglop.look_target_glop
    #region vars moved to material
    #this_kivyglop.ambient_color = this_pyglop.ambient_color
    #this_kivyglop.diffuse_color = this_pyglop.diffuse_color
    #this_kivyglop.specular_color = this_pyglop.specular_color
    ##emissive_color = None  # vec4
    #this_kivyglop.specular_coefficent = this_pyglop.specular_coefficent
    #endregion vars moved to material
    #this_kivyglop.opacity = this_pyglop.opacity # use diffuse color 4th channel instead

    return this_kivyglop
```

* no longer needed
(replaced by get_wmaterial_dict_from_mtl)
```python
def get_wmaterial_list_from_mtl(filename):
    print("get_wmaterial_list_from_mtl (formerly get_wmaterials_from_mtl) IS DEPRECTATED: use get_wmaterial_dict_from_mtl instead)")
    results = None
    try:
        if os.path.exists(filename):
            results = list()  #TODO: Make this a dict
            comments = list()
            this_material = None
            line_counting_number = 1
            for line in open(filename, "r"):
                line_strip = line.strip()
                if (len(line_strip)>0) and (line_strip[0]!="#"):
                    space_index = line_strip.find(" ")
                    if space_index>-1:
                        if len(line_strip) >= (space_index+1):  #TODO: audit this weird check
                            args_string = line_strip[space_index+1:].strip()
                        if len(args_string)>0:
                            command = line_strip[:space_index].strip()
                            if (this_material is not None) or (command == "newmtl"):
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
                                    if this_material is not None:
                                        results.append(this_material)
                                        this_material = None
                                    this_material = WMaterial(name=args_string)
                                elif command=="illum":
                                    this_illum = WIlluminationModel()
                                    result=this_illum.set_from_illumination_model_number(int(args_string))
                                    if result:
                                        this_material._illumination_model = this_illum
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
                                elif len(command)>4 and (command[:4]=="map_"):
                                    if len(args_string)>0 and args_string[0]=="-":
                                        #TODO: load OBJ map params
                                        this_material._map_filename_dict[command] = params[len(params)-1]
                                        this_material._map_params_dict = params[:len(params)-1]
                                        #this_material._map_diffuse_filename = params[len(params)-1]
                                        #args = args_string.split(" ")
                                        #this_material._map_diffuse_filename = args[len(args)-1]
                                        #if len(args)>1:
                                        #    print(filename+" ("+str(line_counting_number)+",0): (NOT YET IMPLEMENTED) map arguments were ignored (except filename): '"+args_string+"'")

                                    else:
                                        #process as string in case filename has spaces (works only if no params)
                                        this_material._map_filename_dict[command] = args_string
                                        # (no params)
                                        #this_material._map_diffuse_filename = args_string
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
            if this_material is not None:
                results.append(this_material)
                this_material = None
        else:
            print("ERROR in get_wmaterial_list_from_mtl: missing file or cannot access '"+filename+"'")
    except:
        #e = sys.exc_info()[0]
        #print("Could not finish get_materials_from_mtl:" + str(e))
        print("Could not finish get_wmaterial_list_from_mtl:")
        view_traceback()
    return results
```
