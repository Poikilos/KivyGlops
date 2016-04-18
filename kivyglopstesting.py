
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.resources import resource_find
from kivy.logger import Logger
from kivy.vector import Vector
from kivy.core.image import Image
from kivy.core.window import Keyboard
#from kivy.graphics.transformation import Matrix
#from kivy.graphics.opengl import *
#from kivy.graphics import *
#from objloader import ObjFile
#from pyrealtime import *
#from kivy.clock import Clock
from kivy.input.providers.mouse import MouseMotionEvent


from kivyglops import *
#from common import *

import math
import os


class MainForm(KivyGlopsWindow):
    
    #def __init__(self, **kwargs):
    def load_glops(self):
        #super(Renderer, self).__init__(**kwargs)
        #self.load_obj("barrels triangulated (Costinus at turbosquid).obj")
        #self.load_obj("barrel.obj")
        #self.load_obj("WarehouseOfFruit_by_Expertmm.obj")
        #self.load_obj("pyramid.obj")
        #self.load_obj("testnurbs-all-textured.obj")
        #self.load_obj("orion.obj")
        #self.load_obj("KivyForest.obj")
        #self.load_obj("testnurbs-all-textured.obj")
        self.load_obj("pedestal-suzanne.obj")
    
            
    def update_glops(self):
        if self.get_pressed("j"):
            self.selected_glop.rotate_y_relative(-1)
        elif self.get_pressed("l"):
            self.selected_glop.rotate_y_relative(1)
            
        #this_index = get_index_by_name(self.scene.glops, "Suzanne")
        #if this_index>-1:
        #    if self.get_pressed("j"):
        #        self.scene.glops[this_index].rotate_y_relative(-1)
        #    elif self.get_pressed("l"):
        #        self.scene.glops[this_index].rotate_y_relative(1)
        #else:
        #    print("Object not found.")
        #this_index = get_index_by_name(self.scene.glops, "Suzanne")
        #if this_index > -1:
        #    self.scene.glops[this_index].rotate_z_relative(1)
        #    print("using index "+str(this_index))
        #else:
        #    print("Not found.")
        
        #this_glop = get_by_name(self.scene.glops, "Suzanne")
        #if this_glop is not None:
        #    this_glop.rotate_z_relative(1)
        #else:
        #    print("Not found.")
        

class KivyGlopsExampleApp(App):
    def build(self):
        mainform = MainForm()
        return mainform

if __name__ == "__main__":
    KivyGlopsExampleApp().run()
