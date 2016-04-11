
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

import math
import os


class MainForm(KivyGlopsWindow):
    
    #def __init__(self, **kwargs):
    def glops_load(self):
        #super(Renderer, self).__init__(**kwargs)
        #self.scene.load_obj(resource_find("barrels triangulated (Costinus at turbosquid).obj"))
        #self.scene.load_obj(resource_find("barrel.obj"))
        #self.scene.load_obj(resource_find("KivyGlopsDemoScene.obj"))
        #self.scene.load_obj(resource_find("WarehouseOfFruit_by_Expertmm.obj"))
        #self.scene.load_obj(resource_find("pyramid.obj"))
        #self.scene.load_obj(resource_find("testnurbs-all-textured.obj"))
        #self.scene.load_obj(resource_find("orion.obj"))
        #self.scene.load_obj(resource_find("testnurbs-all-textured.obj"))
        self.load_obj(resource_find("testnurbs-all-textured.obj"))
        #pass

class KivyGlopsExampleApp(App):
    def build(self):
        mainform = MainForm()
        return mainform

if __name__ == "__main__":
    KivyGlopsExampleApp().run()
