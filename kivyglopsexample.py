
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
        pass


class KivyGlopsExampleApp(App):
    def build(self):
        mainform = MainForm()
        return mainform


if __name__ == "__main__":
    KivyGlopsExampleApp().run()
