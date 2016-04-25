
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
        #self.canvas.shader.source = resource_find('simple1b.glsl')
        #self.canvas.shader.source = resource_find('shade-normal-only.glsl') #partially working
        #self.canvas.shader.source = resource_find('shade-texture-only.glsl')
        self.canvas.shader.source = resource_find('shade-kivyglops-minimal.glsl')
        #self.canvas.shader.source = resource_find('fresnel.glsl')
        #super(MainForm, self).__init__(**kwargs)
        #self.load_obj("barrels triangulated (Costinus at turbosquid).obj")
        #self.load_obj("barrel.obj")
        #self.load_obj("WarehouseOfFruit_by_Expertmm.obj")
        #self.load_obj("pyramid.obj")
        #self.load_obj("testnurbs-all-textured.obj")
        #self.load_obj("orion.obj")
        #self.load_obj("etc/problematic mesh files/4 Gold Rings.obj")  # self.load_obj("4 Gold Rings.obj")
        #self.load_obj("KivyForest.obj")
        #self.load_obj("pedestal-suzanne.obj")
        self.load_obj("OfficeInterior.obj", centered=True)
    
    
    def update_glops(self):
        if self.selected_glop is not None:
            if self.get_pressed("j"):
                self.selected_glop.rotate_y_relative(1)
            elif self.get_pressed("l"):
                self.selected_glop.rotate_y_relative(-1)
            elif self.get_pressed("i"):
                self.selected_glop.rotate_x_relative(-1)
            elif self.get_pressed("k"):
                self.selected_glop.rotate_x_relative(1)
            elif self.get_pressed("u"):
                self.selected_glop.rotate_z_relative(1)
            elif self.get_pressed("o"):
                self.selected_glop.rotate_z_relative(-1)

            if self.get_pressed("left"):
                self.selected_glop.translate_x_relative(-.1)
            elif self.get_pressed("right"):
                self.selected_glop.translate_x_relative(.1)
            elif self.get_pressed("up"):
                self.selected_glop.translate_y_relative(.1)
            elif self.get_pressed("down"):
                self.selected_glop.translate_y_relative(-.1)
            elif self.get_pressed("-"):
                self.selected_glop.translate_z_relative(-.1)
            elif self.get_pressed("="):
                self.selected_glop.translate_z_relative(.1)

        #else:
            #print("No glop selected.")


            
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
