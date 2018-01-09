
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
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivyglops import *
#from common import *
import math
import os

profile_path = None
if 'USERPROFILE' in os.environ:  # if os_name=="windows":
    profile_path = os.environ['USERPROFILE']
else:
    profile_path = os.environ['HOME']


class MainScene(KivyGlops):

    def load_glops(self):
        self.load_obj("meshes/stadium,primitive.obj")

        walkmesh_names = self.get_similar_names("walkmesh")
        for name in walkmesh_names:
            print("Found possible walkmesh: "+name)
            is_ok = self.use_walkmesh(name, hide=True)

        #self.load_obj("player1.obj")


        item_dict = dict()
        item_dict["name"] = "rock"
        item_dict["bump"] = "hide; obtain"
        item_dict["use"] = "throw_arc"
        item_dict["cooldown"] = .7

        weapon = dict()
        weapon["hit_damage"] = .3

        item_dict["as_projectile"] = weapon

        rock_names = self.get_similar_names("rock")
        for name in rock_names:
            print("Preparing item: "+name)
            self.set_as_item(name, item_dict)

        self.set_background_cylmap("maps/sky-texture-seamless.jpg")

        human_info = dict()
        human_info["hp"] = 1.0

        player1_index = self.get_player_glop_index(1)
        self.set_as_actor_at(player1_index, human_info)

        chimp_info = dict()
        chimp_info["hp"] = 1.0

        enemy_indices = self.get_indices_of_similar_names("chimp")
        print("Found "+str(len(enemy_indices))+" chimp(s)")
        for i in range(0,len(enemy_indices)):
            index = enemy_indices[i]
            self.set_as_actor_at(index, chimp_info)

    def attacked_glop(self, attacked_index, attacker_index, weapon_dict):
        self.scene.glops[attacked_index].actor_dict["hp"] -= weapon_dict["hit_damage"]
        if self.scene.glops[attacked_index].actor_dict["hp"] <= 0:
            self.explode_glop_at(attacked_index, weapon_dict)
        print(self.scene.glops[attacked_index].name+"'s hp: "+str(self.scene.glops[attacked_index].actor_dict["hp"]))

    def obtain_glop(self, bumpable_name, bumper_name):
        #if "rock" in bumpable_name.lower():
        #    self.play_sound("sounds/rock-pickup.wav")
        pass

    def update_glops(self):
        pass


scene = MainScene(KivyGlopsWindow())


class KivyGlopsExampleApp(App):
    def build(self):
        return scene.ui
        #mainform = MainForm()
        #boxlayout = TextForm()
        #boxlayout.add_widget(mainform)
        #boxlayout.cols = 1
        #boxlayout.orientation = "vertical"
        #boxlayout.useButton = Factory.Button(text="Use", id="useButton", size_hint=(.1,.1))
        #boxlayout.add_widget(boxlayout.useButton)
        #return boxlayout


if __name__ == "__main__":
    KivyGlopsExampleApp().run()
