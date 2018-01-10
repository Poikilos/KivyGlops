#!/usr/bin/env python3
import os
import sys
import shutil

profile_path = os.environ["HOME"]
verbose_enable = False

student_rm_list = ["testing.py", "testingkivy3d.py", "kivyglopsexample.py", "kivyglops.py.bak", "example_hud.png"]

original_project_name = "KivyGlops"
documents_path = os.path.join(profile_path, "Documents")
projects_path = os.path.join(documents_path, "GitHub")
try_path = os.path.join(profile_path, "GitHub")
if os.path.isdir(try_path):
    projects_path = try_path
original_project_path = os.path.join(projects_path, original_project_name)

#if not os.path.isdir(original_project_path):
try_path = os.path.join(os.path.join("..", ".."), original_project_name)
if os.path.isdir(try_path):
    original_project_path = try_path

print("original_project_path: " + original_project_path)

target_path = None

def is_like_any(target, patterns, case_sensitive_enable=True):
    result = False
    for wildcard in patterns:
        if is_like(target, wildcard, case_sensitive_enable=case_sensitive_enable):
            result = True
            break
    return result

def is_like(target, wildcard, case_sensitive_enable=True):
    result = False
    if not case_sensitive_enable:
        target = target.lower()
        wildcard = wildcard.lower()
    if "*" in wildcard:
        if "**" in wildcard:
            print("    WARNING: is_like removing duplicate wildcard in '" + wildcard + "'")
            while "**" in wildcard:
                wildcard = wildcard.replace("**", "*")
        if wildcard == "*":
            result = True
            print("    (verbose message) '*' wildcard found (always True)")
        else:
            if (len(wildcard)<2) or (not ("*" in wildcard[1:-1])):
                if wildcard[:1] == "*" and wildcard[-1:] == "*":
                    if wildcard[1:-1] in target:
                        result = True
                elif wildcard[:1] == "*":
                    if target[-len(wildcard[1:]):] == wildcard[1:]:
                        result = True
                    #else:
                        #print(target[-len(wildcard[1:]):] + " is not " + wildcard[1:])
                elif wildcard[-1:] == "*":
                    if target[:len(wildcard[:-1])] == wildcard[:-1]:
                        result = True
                    #else:
                        #print(target[:len(wildcard[:-1])] + " is not " + wildcard[:-1])
                        #print("len(wildcard[-1:]) is " + str(len(wildcard[:-1])))
            else:
                w_i = wildcard.find("*")
                if not ( ("*" in wildcard[:w_i]) or ("*" in wildcard[w_i+1:])):
                    if len(target) >= len(wildcard) - 1:
                        if target[:w_i] == wildcard[:w_i] and \
                           target[-len(wildcard[w_i+1:]):] == wildcard[w_i+1:]:
                               result = True
                else:
                    print("    WARNING: is_like can't use full wildcard " + \
                          "syntax, so '" + wildcard + "' will always match" + \
                          " as False")
    else:
        if target==wildcard:
            result = True
    return result

def usage():
    print("")
    print("")
    print("* This program DELETES all of your " + original_project_name + " files so you can")
    print("  separate them from files included with " + original_project_name + ".")
    print("* This program does NOT keep any files you changed if they")
    print("  have the same name as files that are in")
    if target_path is not None:
        print("  '" + target_path + "'!")
    else:
        print("  the target path!")
    print("")
    print("Usage:")
    print("  python3 kivyglopsdelta.py <target_path>")
    print("  ")
    print("  such as:")
    print("  python3 kivyglopsdelta.py path/to/your/modified/copy/of/" + original_project_name)
    print("")
    if verbose_enable:
        print(".gitignore is partially supported")
        print("  * begin ignore line with '/' for specifying path instead of name")
        print("  * the following wildcards work (below are tests of included is_like):")
        print("    abc == abc (" + str(is_like("abc", "abc")) + ")")
        print("    abc == xyz (" + str(is_like("abc", "xyz")) + ")")
        print("    abc == ab* (" + str(is_like("abc", "ab*")) + ")")
        print("    abc == xy* (" + str(is_like("abc", "xy*")) + ")")
        print("    abc == *bc (" + str(is_like("abc", "*bc")) + ")")
        print("    abc == *yz (" + str(is_like("abc", "*yz")) + ")")
        print("    abc == *b* (" + str(is_like("abc", "*b*")) + ")")
        print("    abc == *y* (" + str(is_like("abc", "*y*")) + ")")
        print("    abc == a*c (" + str(is_like("abc", "a*c")) + ")")
        print("    abc == x*z (" + str(is_like("abc", "x*z")) + ")")
        print("  * the following usages are unsupported (will get wrong answer):")
        print("    abcde == a*c*e (" + str(is_like("abcde", "a*c*e")) + ")")
        print("    abcde == x*z*b (" + str(is_like("abcde", "x*z*b")) + ")")
        print("")
    print("")

force_mode = None
gi_path = os.path.join(original_project_path, ".gitignore")
file_ignore_paths = []
file_ignore_patterns = []
dir_ignore_paths = []
dir_ignore_patterns = []

if os.path.isfile(gi_path):
    print("Using .gitignore")
    ins = open(gi_path, 'r')
    line = True
    while line:
        line = ins.readline()
        if line:
            line_strip = line.strip()
            if line_strip[:1] != "#":
                if line_strip[-1:] == "/":  # in .gitignore, dir if end slash
                    line_strip = line_strip[:-1]
                    if line_strip[:1] == "/":
                        dir_ignore_paths.append(line_strip)
                    else:
                        dir_ignore_patterns.append(line_strip)
                else:
                    if line_strip[:1] == "/":
                        file_ignore_paths.append(line_strip)
                    else:
                        file_ignore_patterns.append(line_strip)
    ins.close()
else:
    print("WARNING: not using .gitignore since not in '" + \
          original_project_path + "'")

if (sys.argv is not None) and (len(sys.argv)>0):
    for i in range(0, len(sys.argv)):
        if sys.argv[i] == __file__:
            #print("(running " + __file__ + ")")
            pass
        elif sys.argv[i][0:2]=="--":
            if sys.argv[i][2:] == "clear":
                force_mode = "clear"
            elif sys.argv[i][2:] == "force":
                force_mode = "force"
            else:
                print("STOPPED before processing since found unknown option " + sys.argv[i])
                usage()
                exit(1)
        else:
            if target_path is None:
                target_path = sys.argv[i]

class SyncOptions:
    def __init__(self):
        self.scan_dot_folders_enable = True
        self.mode = "force"
        self.copied_count = 0
        self.removed_count = 0
        self.leave_out_dot_git_enable = True
        self.verbose_enable = verbose_enable
        self.ignore_caches_enable = True
        self.removed_cache_files_count = 0
        
cache_names = ["__pycache__"]

def sync_recursively(master_path, target_path, options):
    if ((options.mode=="force") or (options.mode=="update") or \
        (options.mode=="clear")):
        for cache_name in cache_names:
            try_path = os.path.join(target_path, cache_name)
            if os.path.isdir(try_path):
                for try_name in os.listdir(try_path):
                    sub_path = os.path.join(try_path, try_name)
                    os.remove(sub_path)
                    options.removed_cache_files_count += 1
                try:
                    os.rmdir(try_path)
                except:
                    print("  WARNING: could not remove '" + try_path + "'")
    if os.path.isdir(master_path):
        for master_name in os.listdir(master_path):
            my_path = os.path.join(master_path, master_name)
            try_path = os.path.join(target_path, master_name)
            my_gitlike_path = my_path.replace(original_project_path, "")
            if os.path.isfile(my_path):
                if not ( (is_like_any(my_gitlike_path, file_ignore_paths)) or \
                         (is_like_any(master_name, file_ignore_patterns)) ):
                    master_mtime = os.path.getmtime(my_path)
                    try_mtime = None
                    if os.path.isfile(try_path):
                        try_mtime = os.path.getmtime(try_path)
                    if ((options.mode=="force") and ((try_mtime==None)or(try_mtime!=master_mtime)))  or \
                       ((options.mode=="update") and ((try_mtime==None)or(try_mtime<master_mtime))):
                        if try_mtime is not None:
                            if try_mtime>=master_mtime:
                                if options.verbose_enable:
                                    print('#override "'+try_path+'"')
                            else:
                                if options.verbose_enable:
                                    print('#update "'+try_path+'"')
                        else:
                            if options.verbose_enable:
                                print('#add "'+try_path+'"')
                        if not os.path.isdir(target_path):
                            os.makedirs(target_path)
                        shutil.copy2(my_path, try_path)
                        print("copied '" + master_name + "'")
                        options.copied_count += 1
                    if options.mode=="clear":
                        if try_mtime is not None:
                            if options.verbose_enable:
                                print('rm "'+try_path+'"')
                            os.remove(try_path)
                            options.removed_count += 1
                #else ignored by .gitignore
            else:  # isdir
                if not ( (is_like_any(my_gitlike_path, dir_ignore_paths)) or \
                         (is_like_any(master_name, dir_ignore_patterns)) ):
                    if options.scan_dot_folders_enable or (master_name[:1]!="."):
                        if (options.mode=="clear") or ((not options.ignore_caches_enable) or (master_name not in cache_names)):
                            if (options.mode=="clear") or not (options.leave_out_dot_git_enable and (master_name==".git")):
                                sync_recursively(my_path, try_path, options)
                    if options.mode=="clear":
                        if os.path.isdir(try_path):
                            if len(os.listdir(try_path)) < 1:  # if empty
                                os.rmdir(try_path)
                #else ignored by .gitignore
            #else:
                #print("(verbose message) ignored '" + my_path  + "'")
    else:
        print("ERROR: non-directory sent to sync_recursively: '"+master_path+"'")

if target_path is not None:
    print("target_path: " + target_path)
    if os.path.isdir(target_path):
        options = SyncOptions()
        if force_mode is not None:
            options.mode = force_mode
        sync_recursively(original_project_path, target_path, options)
        print("sync_recursively ("+options.mode+") result:")
        print("  copied: "+str(options.copied_count))
        print("  removed: "+str(options.removed_count))
        print("  removed_cache_files_count: "+str(options.removed_cache_files_count))
    else:
        print("STOPPED before processing since missing target path.")
        usage()
else:
    print("target_path must be specified as command line parameter.")
    usage()
    exit(2)
    
