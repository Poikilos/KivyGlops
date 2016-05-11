
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

import os
import math

# from kivyglops import KivyGlops
# from kivyglops import KivyGlop
from kivyglops import *

class MainForm(KivyGlopsWindow):

    def load_glops(self):
        #self.load_obj("medseaport1b-minimal.obj")
        self.load_obj("C:\\Users\\jgustafson\\ownCloud\\Meshes\\Environments,Outdoor-Manmade\\Medieval Kind of Seaport by tokabilitor (CC0)\\medseaport1b-minimal.obj")
        walkmesh_names = self.get_similar_names("floor")
        #self.load_obj("officeInterior.obj")
        for name in walkmesh_names:
            print("Found possible walkmesh: "+name)
            is_ok = self.use_walkmesh(name, hide=True)
            
        item_dict = dict()
        item_dict["name"] = "barrel"
        item_dict["bump"] = "hide; obtain"
        item_dict["use"] = "throw_arc"
        
        barrel_names = self.get_similar_names("barrels")
        for name in barrel_names:
            print("Preparing item: "+name)
            self.set_as_item(name, item_dict)


class KivyGlopsExampleApp(App):
    def build(self):
        mainform = MainForm()
        return mainform

if __name__ == "__main__":
    KivyGlopsExampleApp().run()
