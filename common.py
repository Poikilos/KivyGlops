import sys
import traceback

def view_traceback():
    ex_type, ex, tb = sys.exc_info()
    print(str(ex)+"("+str(ex_type)+"): ")
    traceback.print_tb(tb)
    del tb
