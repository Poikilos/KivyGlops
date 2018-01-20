import sys
import traceback
import copy
import string

verbose_enable = False
debug_dict = dict()  # constantly-changing variables, for visual debug

def get_verbose_enable():
    return verbose_enable

def set_verbose_enable(enable):
    global verbose_enable
    print("[ common.py ] NOTE: set verbose: " + str(enable))
    verbose_enable = enable

class ScopeInfo:
    indent = None
    name = None
    line_number = -1

def get_yaml_from_literal_value(val):
    # TODO: add yaml escape sequences (see expertmm MoneyForesight for example)
    if type(val).__name__ == "string":
        val = "\"" + val.replace("\"", "\\\"") + "\""
    else:
        val = str(val)
    return val

def get_literal_value_from_yaml(val):
    # TODO: process yaml escape sequences (see expertmm MoneyForesight for example)
    val=val.strip()
    if len(val)>2:
        if val[0:1]=="\"" and val[-1:]=="\"":
            val=val[1:-1]
    return val

#from  github.com/expertmm/minetest/chunkymap/expertmm.py, but modified for python2
def get_dict_deepcopy(old_dict, depth=0):
    new_dict = None
    if type(old_dict) is dict:
        new_dict = {}
        for this_key in old_dict.keys():
            try:
                new_dict[this_key] = copy.deepcopy(old_dict[this_key])
            except:
                try:
                    new_dict[this_key] = old_dict[this_key].copy(depth=depth+1)
                except:
                    try:
                        new_dict[this_key] = old_dict[this_key].copy()
                    except:
                        new_dict[this_key] = old_dict[this_key]
    return new_dict

valid_path_name_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
if verbose_enable:
    print("[ common.py ] (verbose message) Using valid_path_name_chars: '" + \
          valid_path_name_chars + "'")

def find_any_not(haystack, needles):
    result = -1
    for i in range(len(haystack)):
        if haystack[i:i+1] not in needles:
            result = i
            break
    return result

def good_path_name(try_path_name):
    result = ""
    if try_path_name is not None:
        for i in range(len(try_path_name)):
            if try_path_name[i:i+1] not in valid_path_name_chars:
                result += "_"
            else:
                result += try_path_name[i:i+1]
    else:
        result = None
    return result

# displays 2D array in fixed-width format as string result with
# newline characters in between each row
# (uses fixed_width function on each row)
def fixed_widths(val_lists, visible_width, spacing):
    result = ""
    delim = ""
    for vals in val_lists:
        result += fixed_width(vals, visible_width, spacing)
    delim = "\n"
    return result

# makes each column visible_width characters wide, sacrificing extra
# characters at end.
# spacing is added between columns
# so total width of each column plus spacing (except for last column)
# would be visible_width + len(spacing)
def fixed_width(vals, visible_width, spacing):
    result = ""
    fixed_width = visible_width + len(spacing)
    for original_val in vals:
        val = str(original_val)
        if result != "":
            result += spacing
        if len(val) < visible_width:
            val += " " * (visible_width - len(val))
        result += val[:fixed_width]
    return result

def view_traceback(indent=""):
    ex_type, ex, tb = sys.exc_info()
    print(indent + str(ex_type) + " " + str(ex) + ": ")
    traceback.print_tb(tb)
    del tb
    print("")

def get_traceback(indent=""):
    ex_type, ex, tb = sys.exc_info()
    result = indent + str(ex_type) + " " + str(ex) + ": " + "\n"
    #traceback.print_tb(tb)
    result += str(tb)
    del tb
    return result


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
            print("[ common.py ] ERROR--Could not finish get_by_name:")
            view_traceback()
    return result

def find_by_name(object_list, needle):
    result = -1
    for i in range(0,len(object_list)):
        try:
            if object_list[i].name == needle:
                result = i
                break
        except:
            #e = sys.exc_info()[0]
            #print("Could not finish get_by_name:" + str(e))
            print("[ common.py ] ERROR--Could not finish find_by_name:")
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

true_like_strings = ['true', 'yes', 'on', '1']

def set_true_like_strings(vals):
    global true_like_strings
    set_enable = True
    for tls in vals:
        if tls.lower() != tls:
            set_enable = False
            print("[ common.py ] ERROR: refusing to set true_like_strings" + \
                  " since an element contains uppercase characters")
            break
    if set_enable:
        true_like_strings = vals

# Only returns True if `is True`, `== 1`, or
# lower().strip() in true_like_strings
def is_true(val):
    result = False
    try:
        val_lower = None
        try:
            val_lower = val.lower()
        except:
            pass
        if val_lower is not None:  # is string
            val_lower = val_lower.strip()
            if val_lower in true_like_strings:
                result = True
        elif val_lower is True:
            result = True
        elif val == 1:
            result = True
    except:
        print("[ common.py ] ERROR--Could not finish is_true" + \
              " (returning false):")
        view_traceback()
    return result
