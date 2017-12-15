#!/usr/bin/env python3
import os
import sys


profile_path = os.environ["HOME"]

original_project_name = "KivyGlops"
documents_path = os.path.join(profile_path, "Documents")
projects_path = os.path.join(documents_path, "GitHub")
try_path = os.path.join(profile_path, "GitHub")
if os.path.isdir(try_path):
    projects_path = try_path
original_project_folder = os.path.join(projects_path, original_project_name)
print("original_project_folder: " + original_project_folder)

target_path = None

#mode = "delete"
#mode = "overwrite"

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


if (sys.argv is not None) and (len(sys.argv)>0):
    for i in range(0, len(sys.argv)):
        if sys.argv[i] == __file__:
            print("(running " + __file__ + ")")
        elif sys.argv[i][0:2]=="--":
            print("STOPPED before processing since found unknown option " + sys.argv[i])
            usage()
            exit(1)
        else:
            if target_path is None:
                target_path = sys.argv[i]
if target_path is not None:
    print("target_path: " + target_path)
    if os.path.isdir(target_path):
        
    else:
        print("STOPPED before processing since missing target path.")
        usage()
else:
    print("target_path must be specified as command line parameter.")
    usage()
    exit(2)
    
