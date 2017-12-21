* formerly from kivyglops.py, but (PROBABLY) not needed since pyglops.py version of this method checks for type(self) instead of PyGlops now:
```
def get_dict_deepcopy_with_my_type(self, old_dict, copy_my_type_by_reference_enable=False):
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
                if copy_my_type_by_reference_enable:
                    if isinstance(new_dict, dict):
                        new_dict[this_key] = old_dict[this_key]
                    else:
                        new_dict.append(old_dict[this_key])
                else:
                    copy_of_var = None
                    if self.material is not None:
                        copy_of_var = old_dict[this_key].copy(self.new_glop, self.material.new_material)
                    else:
                        copy_of_var = old_dict[this_key].copy(self.new_glop, None)
                    if isinstance(new_dict, dict):
                        new_dict[this_key] = copy_of_var
                    else:
                        new_dict.append(copy_of_var)
            #TODO?: elif isinstance(old_dict[this_key], KivyGlopsMaterial)
            elif isinstance(old_dict[this_key], list):
                new_dict[this_key] = get_dict_deepcopy_with_my_type(old_dict[this_key], copy_my_type_by_reference_enable)
            else:
                new_dict[this_key] = copy.deepcopy(old_dict[this_key])
        return new_dict
``` 

* formerly from __init__ in KivyGlops (formerly in KivyGlopsWindow)
```
        self.camera_ax = 0
        self.camera_ay = 0
```

* instead, use new_glop method (never use `= PyGlop(`) to avoid needing this
```
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
    this_kivyglop.x_velocity = this_pyglop.x_velocity
    this_kivyglop.y_velocity = this_pyglop.y_velocity
    this_kivyglop.z_velocity = this_pyglop.z_velocity
    this_kivyglop._cached_floor_y = this_pyglop._cached_floor_y
    this_kivyglop.infinite_inventory_enable = this_pyglop.infinite_inventory_enable
    this_kivyglop.bump_sounds = this_pyglop.bump_sounds
    this_kivyglop.look_target_glop = this_pyglop.look_target_glop
    this_kivyglop.hitbox = this_pyglop.hitbox
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
```
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
