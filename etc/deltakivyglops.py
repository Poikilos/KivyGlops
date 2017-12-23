#!/usr/bin/env python3
import os
import sys
import shutil

profile_path = os.environ["HOME"]

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
    print("")

force_mode = None

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
        self.verbose_enable = False
        self.ignore_caches_enable = True
        self.removed_cache_files_count = 0
        
cache_names = "__pycache__"

def sync_recursively(master_path, target_path, options):
    if ((options.mode=="force") or (options.mode=="update") or \
        (options.mode=="clear")):
        try_path = os.path.join(target_path, "__pycache__")
        if os.path.isdir(try_path):
            for try_name in os.listdir(try_path):
                sub_path = os.path.join(try_path, try_name)
                os.remove(sub_path)
                options.removed_cache_files_count += 1
    if os.path.isdir(master_path):
        for master_name in os.listdir(master_path):
            my_path = os.path.join(master_path, master_name)
            try_path = os.path.join(target_path, master_name)
            if os.path.isfile(my_path):
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
                    options.copied_count += 1
                if options.mode=="clear":
                    if try_mtime is not None:
                        if options.verbose_enable:
                            print('rm "'+try_path+'"')
                        os.remove(try_path)
                        options.removed_count += 1
            else:
                if options.scan_dot_folders_enable or (master_name[:1]!="."):
                    if (options.mode=="clear") or ((not options.ignore_caches_enable) or (master_name not in cache_names)):
                        if (options.mode=="clear") or not (options.leave_out_dot_git_enable and (master_name==".git")):
                            sync_recursively(my_path, try_path, options)
                if options.mode=="clear":
                    if os.path.isdir(try_path):
                        if len(os.listdir(try_path)) < 1:  # if empty
                            os.rmdir(try_path)
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
    
