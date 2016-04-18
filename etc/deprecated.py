

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
