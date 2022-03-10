
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.resources import resource_find
from kivy.logger import Logger
from kivy.vector import Vector
from kivy.core.image import Image
from kivy.core.window import Keyboard
# from kivy.graphics.transformation import Matrix
# from kivy.graphics.opengl import *
# from kivy.graphics import *
# from objloader import ObjFile
# from pyrealtime import *
# from kivy.clock import Clock
from kivy.input.providers.mouse import MouseMotionEvent
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivyglops import *
from common import (
    set_verbose_enable,
)
import math
import os

profile_path = None
if 'USERPROFILE' in os.environ:  # if os_name=="windows":
    profile_path = os.environ['USERPROFILE']
else:
    profile_path = os.environ['HOME']


script_path = os.path.abspath(__file__)
my_dir = os.path.dirname(script_path)

class MainScene(KivyGlops):

    def on_load_glops(self):
        try_paths = [
            # "meshes/stadium,primitive.obj",
            "meshes/stadium,primitive-simpler.obj",
            os.path.join(my_dir,
                         "meshes/stadium,primitive-simpler.obj"),
            "stadium,primitive-simpler.obj",
            # "../KivyGlops/meshes/stadium,primitive-simpler.obj",
        ]
        for try_path in try_paths:
            result = self.load_obj(try_path)
            print("[example-stadium] * trying {}...got {}"
                  "".format(try_path, result))
            if result is not None:
                break

        walkmesh_names = self.get_similar_names("walkmesh")
        for name in walkmesh_names:
            print("Found possible walkmesh: "+name)
            is_ok = self.use_walkmesh(name, hide=True)

        # self.load_obj("player1.obj")

        item_dict = dict()
        item_dict['name'] = "rock"
        item_dict["bump"] = "hide; obtain"
        item_dict["uses"] = ["throw_arc", "melee"]
        item_dict["target_types"] = ["surface", "actor", "glop"]  # TODO
        item_dict["cooldown"] = .7
        item_dict['hit_damage'] = .3
        item_dict['projectile_keys'] = ['hit_damage']

        # weapon = dict()
        # weapon['hit_damage'] = .3

        # item_dict['as_projectile'] = weapon

        for index in self.get_indices_of_similar_names("rock"):
            print("Preparing item at index " + str(index))
            self.set_as_item_at(index, item_dict)
            self.add_bump_sound_at(index, "sounds/carpeted-cement-hit,light1.wav")
            self.add_bump_sound_at(index, "sounds/carpeted-cement-hit1.wav")
            self.add_bump_sound_at(index, "sounds/carpeted-cement-hit2.wav")

        self.set_background_cylmap("maps/sky-texture-seamless.jpg")

        human_info = dict()
        human_info['hp'] = 1.0

        player1_index = self.get_player_glop_index(1)
        self.set_as_actor_at(player1_index, human_info)
        self.add_damaged_sound_at(player1_index, "sounds/body-hit1.wav")
        self.add_damaged_sound_at(player1_index, "sounds/body-hit2.wav")
        self.add_damaged_sound_at(player1_index, "sounds/body-hit3.wav")
        self.add_damaged_sound_at(player1_index, "sounds/body-hit4.wav")

        chimp_info = dict()
        chimp_info['hp'] = 1.0

        chimp_info["land_units_per_second"] = self.glops[player1_index].actor_dict["land_units_per_second"] / 2.
        # If the ranges below are not set, PyGlops will set defaults for them:
        chimp_info["ranges"] = {}
        chimp_info["ranges"]["melee"] = 0.5
        chimp_info["ranges"]["throw_arc"] = 10.

        enemy_indices = self.get_indices_of_similar_names("chimp")
        print("Found "+str(len(enemy_indices))+" chimp(s)")
        for i in range(0,len(enemy_indices)):
            index = enemy_indices[i]
            self.set_as_actor_at(index, chimp_info)
            self.add_damaged_sound_at(index, "sounds/chimp-ooh1.wav")
            self.add_damaged_sound_at(index, "sounds/chimp-upset1.wav")

    def on_attacked_glop(self, attacked_index, attacker_index, weapon_dict):
        self.glops[attacked_index].actor_dict['hp'] -= weapon_dict['hit_damage']
        if self.glops[attacked_index].actor_dict['hp'] <= 0:
            self.explode_glop_at(attacked_index, weapon_dict)
        # if get_verbose_enable():
        print(str(self.glops[attacked_index].name) + "'s hp: " + \
              str(self.glops[attacked_index].actor_dict['hp']))

    def obtain_glop(self, bumpable_name, bumper_name):
        # if "rock" in bumpable_name.lower():
        #     self.play_sound("sounds/rock-pickup.wav")
        pass

    def on_update_glops(self):
        pass

set_verbose_enable(True)
scene = MainScene(KivyGlopsWindow())


class KivyGlopsExampleApp(App):
    def build(self):
        return scene.ui
        # mainform = MainForm()
        # boxlayout = TextForm()
        # boxlayout.add_widget(mainform)
        # boxlayout.cols = 1
        # boxlayout.orientation = "vertical"
        # boxlayout.useButton = Factory.Button(text="Use", id="useButton", \
        #                                      size_hint=(.1,.1))
        # boxlayout.add_widget(boxlayout.useButton)
        # return boxlayout


if __name__ == "__main__":
    KivyGlopsExampleApp().run()
