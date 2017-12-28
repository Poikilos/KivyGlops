import sys
import traceback
import copy

verbose_enable = False
debug_dict = dict()  # constantly-changing variables, for visual debug

#from  github.com/expertmm/minetest/chunkymap/expertmm.py, but modified for python2
def get_dict_deepcopy(old_dict):
    new_dict = None
    if type(old_dict) is dict:
        new_dict = {}
        for this_key in old_dict.keys():
            new_dict[this_key] = copy.deepcopy(old_dict[this_key])
    return new_dict


def view_traceback():
    ex_type, ex, tb = sys.exc_info()
    print(str(ex_type)+" "+str(ex)+": ")
    traceback.print_tb(tb)
    del tb
    print("")

def get_by_name(object_list, needle):  # formerly find_by_name
    result = None
    for i in range(0,len(object_list)):
        try:
            if object_list[i].name == needle:
                result = object_list[i]
                break
        except:
            #e = sys.exc_info()[0]
            #print("Could not finish get_by_name:" + str(e))
            print("Could not finish get_by_name:")
            view_traceback()
    return result

def get_index_by_name(object_list, needle):
    result = -1
    for i in range(0,len(object_list)):
        try:
            if object_list[i].name == needle:
                result = i
                break
        except:
            #e = sys.exc_info()[0]
            #print("Could not finish get_by_name:" + str(e))
            print("Could not finish get_index_by_name:")
            view_traceback()
    return result

def push_yaml_text(yaml, name, val, indent):
    if type(val) is dict:
        for key in val.keys():
            yaml = push_yaml_text(yaml, key, val[key], indent+"  ")
    else: #if val is None:
        #if yaml is not None:
        #    if len(yaml)>0:
        #        yaml += "\n"
        #else:
        #    yaml = ""
        if yaml is None:
            yaml = ""
        if val is None:
            yaml += indent + name + ": ~"
        else:
            yaml += indent + name + ": " + str(val)
        yaml += "\n"
    return yaml
