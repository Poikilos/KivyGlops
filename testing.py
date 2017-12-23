
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

    #def __init__(self, **kwargs):
    def load_glops(self):
        #self.canvas.shader.source = resource_find('simple1b.glsl')
        #self.canvas.shader.source = resource_find('shade-normal-only.glsl') #partially working
        #self.canvas.shader.source = resource_find('shade-texture-only.glsl')
        #self.canvas.shader.source = resource_find('shade-kivyglops-minimal.glsl')
        #self.canvas.shader.source = resource_find('fresnel.glsl')
        #super(MainForm, self).__init__(**kwargs)
        #self.load_obj("barrels triangulated (Costinus at turbosquid).obj")
        #self.load_obj("barrel.obj")
        #self.load_obj("WarehouseOfFruit_by_Expertmm.obj")
        #self.load_obj("pyramid.obj")
        #self.load_obj("testnurbs-all-textured.obj")
        #self.load_obj(finalize_scene"orion.obj")
        #self.load_obj("etc/problematic mesh files/4 Gold Rings.obj", centered=True)  # self.load_obj("4 Gold Rings.obj")
        #self.load_obj("KivyForest.obj")
        #self.load_obj("pedestal-suzanne.obj")
        #self.load_obj("colonnato.obj") #has memory errors and takes several minutes to load
        #self.load_obj("OfficeInterior.obj")

        #self.load_obj("OfficeInteriorWalkmesh.obj")
        #walkmesh_names = self.get_similar_names("floor")
        #self.load_obj("OfficeInterior.obj")
        #for name in walkmesh_names:
        #    print("Found possible walkmesh: "+name)
        #    is_ok = self.use_walkmesh(name, hide=True)

        #self.load_obj(os.path.join(profile_path,"ownCloud\\Meshes\\Environments,Outdoor-Manmade\\Medieval Kind of Seaport by tokabilitor (CC0)\\medseaport1b-lowpoly.obj"))
        #self.load_obj(os.path.join(profile_path,"ownCloud\\Meshes\\Environments,Outdoor-Manmade\\Medieval Kind of Seaport by tokabilitor (CC0)\\medseaport1b-minimal.obj"))
        #self.load_obj(os.path.join(profile_path,"ownCloud\\Meshes\\Environments,Outdoor-Manmade\\Medieval Kind of Seaport by tokabilitor (CC0)\\medseaport1b-techdemo.obj"))
        #self.load_obj("R:\\Meshes\\Environments,Outdoor-Manmade\\Medieval Kind of Seaport by tokabilitor (CC0)\\medseaport1b-lowpoly.obj")
        #self.load_obj("R:\\Meshes\\Environments,Outdoor-Manmade\\Medieval Kind of Seaport by tokabilitor (CC0)\\medseaport1b-minimal.obj")
        #self.load_obj("R:\\Meshes\\Environments,Outdoor-Manmade\\Medieval Kind of Seaport by tokabilitor (CC0)\\medseaport1b-techdemo.obj")
        #self.load_obj("etc\\problematic mesh files\\medseaport1b-floor_glrepeat.obj")
        #self.load_obj("medseaport1b-lowpoly.obj")
        #medseaport1b-lowpoly (including dependencies) is available from http://www.expertmultimedia.com/usingpython/resources/Environments,Outdoor-Manmade/seaport.zip

        #self.load_obj("medseaport1b-minimal.obj")

        # If you already have existing walkmesh code, keep that instead of
        # typing this section, but change "floor" to "walkmesh"
        #walkmesh_names = self.get_similar_names("walkmesh")
        #for name in walkmesh_names:
        #    print("Using walkmesh: ")
        #    is_ok = self.use_walkmesh(name, hide=True)

        #item_dict = dict()
        #item_dict["name"] = "barrel"
        #item_dict["bump"] = "hide; obtain"
        #item_dict["use"] = "throw_arc"
        #item_dict["cooldown"] = .7

        #barrel_names = self.get_similar_names("barrel")
        #for name in barrel_names:
        #    print("Preparing item: "+name)
        #    self.set_as_item(name, item_dict)

        #self.play_music("music/edinburgh-loop.ogg")

        #item_dict["name"] = "crate"
        #item_dict["use_sound"] = "sounds/woosh-medium.wav"
        #for index in self.get_indices_of_similar_names("crate"):
        #    self.set_as_item_by_index(index, item_dict)
        #    self.add_bump_sound_by_index(index, "sounds/crate-drop2.wav")
        #    self.add_bump_sound_by_index(index, "sounds/crate-drop3.wav")
        #    self.add_bump_sound_by_index(index, "sounds/crate-drop4.wav")
        #    self.add_bump_sound_by_index(index, "sounds/crate-drop5.wav")
        #    self.add_bump_sound_by_index(index, "sounds/crate-drop6.wav")
        #    self.add_bump_sound_by_index(index, "sounds/crate-drop7.wav")
        #    self.add_bump_sound_by_index(index, "sounds/crate-drop8.wav")
        self.set_background_cylmap("starfield1-coryg89.jpg")

        self.set_fly(True)
        self.ui.set_hud_background("example_hud.png")
        self.set_background_cylmap("starfield_cylindrical_map.jpg")
        self.load_obj("spaceship,simple-denapes.obj")

        ship_info = dict()
        ship_info["hp"] = 1.0

        player1_index = self.get_player_glop_index(1)
        #self.set_as_actor_by_index(player1_index, ship_info)  # already done by PyGlops or KivyGlops __init__

        weapon = dict()
        weapon["droppable"] = "no"
        weapon["fired_sprite_path"] = "blue_jet_bulb.png"
        weapon["fired_sprite_size"] = .5,.5  # width and height in meters
        weapon["fire_type"] = "throw_linear"
        weapon["hit_damage"] = .3
        self.add_actor_weapon(player1_index, weapon)
        #self.player_glop = self.glops[player1_index]  # already done by PyGlops __init__
        #test_deepcopy_weapon = self.player_glop.deepcopy_with_my_type(weapon)
        print("[ debug only ] #" + str(player1_index) + " named " + str(self.glops[player1_index].name) + " detected as player") 
        enemy_indices = self.get_indices_by_source_path("spaceship,simple-denapes.obj")
        for i in range(0,len(enemy_indices)):
            index = enemy_indices[i]
            self.set_as_actor_by_index(index, ship_info)
            self.add_actor_weapon(index, weapon)
            print("[ debug only ] #" + str(index) + " named " + str(self.glops[index].name) + " added as enemy") 
        print("[ debug only ] " + str(len(enemy_indices)) + " enemies found.") 
        #test_deepcopy_weapon = self.player_glop.deepcopy_with_my_type(weapon)

    def attacked_glop(self, attacked_index, attacker_index, weapon_dict):
        self.glops[attacked_index].actor_dict["hp"] -= weapon_dict["hit_damage"]
        if self.glops[attacked_index].actor_dict["hp"] <= 0:
            self.explode_glop_by_index(attacked_index, weapon_dict)
            print("[ after exploding ] HP: "+str(self.glops[attacked_index].actor_dict["hp"]))
        else:
            print("HP: "+str(self.glops[attacked_index].actor_dict["hp"]))

    def obtain_glop(self, bumpable_name, bumper_name):
        if "barrel" in bumpable_name.lower():
            self.play_sound("sounds/barrel,wooden-pickup.wav")
        if "crate" in bumpable_name.lower():
            self.play_sound("sounds/crate-pickup.wav")

    #def display_explosion(self, pos, radius, attacked_index, weapon):
    #    print("display_explosion...Not Yet Implemented")
    #    pass

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
                self.selected_glop.move_x_relative(-.1)
            elif self.get_pressed("right"):
                self.selected_glop.move_x_relative(.1)
            elif self.get_pressed("up"):
                self.selected_glop.move_y_relative(.1)
            elif self.get_pressed("down"):
                self.selected_glop.move_y_relative(-.1)
            elif self.get_pressed("-"):
                self.selected_glop.move_z_relative(-.1)
            elif self.get_pressed("="):
                self.selected_glop.move_z_relative(.1)
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

scene = MainScene(KivyGlopsWindow())

class KivyGlopsExampleApp(App):
    def build(self):
        #mainform = MainForm()
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
