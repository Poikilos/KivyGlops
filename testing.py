#!/usr/bin/env python
"""PyGlops is a game engine for python. It is "abstract" so in most
cases classes here need to be subclassed to be useful (see KivyGlops)
"""
import math
import os

__author__ = 'Jake Gustafson'
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

from kivyglops import (
    KivyGlop,
    KivyGlops,
    KivyGlopsWindow,
)
from kivyglops.common import (
    set_verbose_enable,
)

from kivyglops.pyglops import (
    new_material,
    copy_material,
)
set_verbose_enable(True)


profile_path = None

if 'USERPROFILE' in os.environ:  # if os_name=="windows":
    profile_path = os.environ['USERPROFILE']
else:
    profile_path = os.environ['HOME']


# class MainForm(KivyGlopsWindow()):
#     def __init__(self, **kwargs):
#         super(MainForm, self).__init__(**kwargs)

item_dict = {}


class MainScene(KivyGlops):

    def on_load_glops(self):
        global item_dict
        test_space_enable = True
        test_medieval_enable = False
        test_shader_enable = False
        test_infinite_crates = True
        if test_infinite_crates:
            if not test_medieval_enable:
                print("test_infinite_crates requires"
                      " test_medieval_enable")
        try_dict = {}
        try_dict['glop'] = KivyGlop()
        print("[ testing ] copying dict with glop...")
        with_glop_dict = try_dict['glop'].deepcopy_with_my_type(try_dict)
        try_dict['material'] = new_material()
        print("[ testing ] copying dict with glop and material using"
              " glop...")
        with_gm_via_glop_dict = try_dict['glop'].deepcopy_with_my_type(
            try_dict
        )
        mat_dict = {}
        mat_dict['material'] = new_material()
        print("[ testing ] copying material using copy_material...")
        with_gm_via_mat_dict = copy_material(mat_dict['material'])
        try_dict['glop'].material = new_material()
        del try_dict['material']
        print("[ testing ] copying dict with glop that has "
              "material, using deepcopy_with_my_type...")
        with_glop_with_gm_dict = try_dict['glop'].deepcopy_with_my_type(try_dict)
        print("[ testing ] making actor_glop...")
        actor = {}
        # actor['hp'] = 1.
        actor_glop = KivyGlop()
        actor_glop.name = "InvisibleTestDummyAtOrigin_Actor"
        self.ui.add_glop(actor_glop)
        print("[ testing ] setting actor which calls deepcopy_with_my_type...")
        self.set_as_actor_at(actor_glop.glop_index, actor)
        print("[ testing ] actor now has the following defaults: " +
              str(actor_glop.actor_dict))

        print("[ testing ] making item_glop...")
        item = {}
        # item['name'] = "something"
        item_glop = KivyGlop()
        item_glop.name = "InvisibleTestDummyAtOrigin_Item"
        self.ui.add_glop(item_glop)
        print("[ testing ] setting item which calls deepcopy_with_my_type...")
        self.set_as_item_at(item_glop.glop_index, item)
        print("[ testing ] item now has the following defaults: " +
              str(item_glop.item_dict))

        # NOTE: default gl_widget shader is already loaded by KivyGlops
        # self.ui.gl_widget.canvas.shader.source = resource_find(os.path.join('shaders','simple1b.glsl'))
        # self.ui.gl_widget.canvas.shader.source = resource_find(os.path.join('shaders','shade-normal-only.glsl'))  # partially working
        # self.ui.gl_widget.canvas.shader.source = resource_find(os.path.join('shaders','shade-texture-only.glsl'))
        # self.ui.gl_widget.canvas.shader.source = resource_find(os.path.join('shaders','shade-kivyglops-minimal.glsl'))
        # self.ui.gl_widget.canvas.shader.source = resource_find(os.path.join('shaders','fresnel.glsl'))

        # self.load_obj("barrels triangulated (Costinus at turbosquid).obj")
        # self.load_obj("barrel.obj")
        # self.load_obj("WarehouseOfFruit_by_Poikilos.obj")
        # self.load_obj("pyramid.obj")
        # self.load_obj("testnurbs-all-textured.obj")
        # self.load_obj("orion.obj")
        # self.load_obj("etc/problematic mesh files/4 Gold Rings.obj", centered=True)  # self.load_obj("4 Gold Rings.obj")
        # self.load_obj("KivyForest.obj")
        # self.load_obj("pedestal-suzanne.obj")
        # self.load_obj("colonnato.obj") #has memory errors and takes several minutes to load
        # self.load_obj("OfficeInterior.obj")

        # self.load_obj("OfficeInteriorWalkmesh.obj")
        # walkmesh_names = self.get_similar_names("floor")
        # self.load_obj("OfficeInterior.obj")
        # for name in walkmesh_names:
        #     print("Found possible walkmesh: "+name)
        #     is_ok = self.use_walkmesh(name, hide=True)

        if test_shader_enable:
            test_name = "shader-test.obj"
            test_path = os.path.join("meshes", test_name)
            self.load_obj(test_path)

        if test_medieval_enable:

            # self.load_obj(os.path.join(profile_path,"ownCloud\\Meshes\\Environments,Outdoor-Manmade\\Medieval Kind of Seaport by tokabilitor (CC0)\\medseaport1b-lowpoly.obj"))
            # self.load_obj(os.path.join(profile_path,"ownCloud\\Meshes\\Environments,Outdoor-Manmade\\Medieval Kind of Seaport by tokabilitor (CC0)\\medseaport1b-minimal.obj"))
            # self.load_obj(os.path.join(profile_path,"ownCloud\\Meshes\\Environments,Outdoor-Manmade\\Medieval Kind of Seaport by tokabilitor (CC0)\\medseaport1b-techdemo.obj"))
            # self.load_obj("R:\\Meshes\\Environments,Outdoor-Manmade\\Medieval Kind of Seaport by tokabilitor (CC0)\\medseaport1b-lowpoly.obj")
            # self.load_obj("R:\\Meshes\\Environments,Outdoor-Manmade\\Medieval Kind of Seaport by tokabilitor (CC0)\\medseaport1b-minimal.obj")
            # self.load_obj("R:\\Meshes\\Environments,Outdoor-Manmade\\Medieval Kind of Seaport by tokabilitor (CC0)\\medseaport1b-techdemo.obj")
            # self.load_obj("etc\\problematic mesh files\\medseaport1b-floor_glrepeat.obj")
            # self.load_obj("medseaport1b-lowpoly.obj")
            # seaport_name = "medseaport1b-techdemo.obj"
            seaport_name = "medseaport1b-techdemo.obj"
            # seaport_name = "medseaport1b-door.obj"
            # seaport_name = "medseaport1b-minimal.obj"
            # testing_path = os.path.join( os.path.join(profile_path, "Desktop"), "KivyGlopsTesting")
            testing_path = os.path.join("meshes", "medseaport")
            seaport_path = resource_find(seaport_name)
            if seaport_path is None:
                seaport_path = os.path.join(testing_path, seaport_name)
            if os.path.isfile(seaport_path):
                self.load_obj(seaport_path, pivot_to_g_enable=True)
            else:
                # try_path
                print("[ testing ] ERROR: can't find '" + seaport_name + "'")
            # medseaport1b-lowpoly (including dependencies) is available
            # from
            # expertmultimedia.com/usingpython/resources/Environments,Outdoor-Manmade/seaport.zip

            # self.load_obj("medseaport1b-minimal.obj")

            # If you already have existing walkmesh code, keep that instead of
            # typing this section, but change "floor" to "walkmesh"
            walkmesh_names = self.get_similar_names("walkmesh")
            for name in walkmesh_names:
                print("[ testing ] Using walkmesh: ")
                is_ok = self.use_walkmesh(name, hide=True)

            # item_dict = dict()
            item_dict['name'] = 'barrel'
            item_dict['bump'] = "hide; obtain"
            # item_dict['use'] = 'throw_arc'
            item_dict['uses'] = ['throw_arc']
            # item_dict['uses'] = []
            # item_dict['uses'].append('throw_arc')
            item_dict['cooldown'] = .7

            results = self.get_index_lists_by_similar_names(
                ['crate', 'barrel']
            )
            crate_indices = results['crate']
            barrel_indices = results['barrel']

            barrel_names = []  # stored for debug output
            for index in barrel_indices:
                print("Preparing item: " + name)
                self.set_as_item_at(index, item_dict)
                barrel_names.append(self.glops[index].name)

            # self.play_music("music/edinburgh-loop.ogg")

            item_dict['name'] = 'crate'
            item_dict['use_sound'] = "sounds/woosh-medium.wav"
            item_dict['hit_damage'] = .3
            print("[ testing ] about to create projectile weapon"
                  " without projectile keys to make sure"
                  " projectile_dict received by attacked_glop"
                  " has all user-specified variables ("
                  " the custom on_attack_glop event in here"
                  " will show errors if missing)")
            # item_dict['projectile_keys'] = ['hit_damage']
            if test_infinite_crates:
                item_dict['droppable'] = False
                item_dict['cooldown'] = .1
                item_dict['uses'] = ["throw_linear"]

            for index in crate_indices:
                self.set_as_item_at(index, item_dict)
                self.add_bump_sound_at(index, "sounds/crate-drop1.wav")
                self.add_bump_sound_at(index, "sounds/crate-drop2.wav")
                self.add_bump_sound_at(index, "sounds/crate-drop3.wav")
                self.add_bump_sound_at(index, "sounds/crate-drop4.wav")
                self.add_bump_sound_at(index, "sounds/crate-drop5.wav")
                self.add_bump_sound_at(index, "sounds/crate-drop6.wav")
                self.add_bump_sound_at(index, "sounds/crate-drop7.wav")
                self.add_bump_sound_at(index, "sounds/crate-drop8.wav")
            print("[ testing ] len(barrel_names): " + str(len(barrel_names)))
            print("[ testing ] len(crate_indices): " + str(len(crate_indices)))
            self.set_background_cylmap(
                os.path.join("maps", "sky-texture-seamless.jpg")
            )
        if test_space_enable:
            # self.set_background_cylmap("maps/starfield1-coryg89.jpg")

            self.set_gravity(True)
            self.set_player_fly(1, True)
            self.set_hud_background("example_hud.png")
            self.set_background_cylmap("maps/starfield_cylindrical_map.jpg")
            self.load_obj("meshes/spaceship,simple-denapes.obj")

            ship_info = dict()
            ship_info['hp'] = 1.0

            player1_index = self.get_player_glop_index(1)
            # self.set_as_actor_at(player1_index, ship_info)
            #     already done by PyGlops or KivyGlops __init__

            weapon = dict()
            weapon['name'] = "missile"
            weapon['droppable'] = "no"
            weapon['fired_sprite_path'] = "sprites/blue_jet_bulb.png"
            weapon['fired_sprite_size'] = (.5, .5)
            # ^ width and height in meters
            weapon['uses'] = ["throw_linear"]
            # weapon['fire_type'] = 'throw_arc'
            weapon['hit_damage'] = .3
            weapon['projectile_keys'] = ['hit_damage']
            self.add_actor_weapon(player1_index, weapon)
            # self.player_glop = self.glops[player1_index]
            #     already done by PyGlops __init__
            # test_deepcopy_weapon = \
            #     self.player_glop.deepcopy_with_my_type(weapon)
            print("[ testing ] #" + str(player1_index) + " named " +
                  str(self.glops[player1_index].name) +
                  " detected as player")
            enemy_indices = self.get_indices_by_source_path(
                "spaceship,simple-denapes.obj"
            )
            for i in range(0, len(enemy_indices)):
                index = enemy_indices[i]
                self.set_as_actor_at(index, ship_info)
                self.add_actor_weapon(index, weapon)
                print("[ testing ] #" + str(index) + " named " +
                      str(self.glops[index].name) + " added as enemy")
            print("[ testing ] " + str(len(enemy_indices)) +
                  " enemies found.")
        # test_deepcopy_weapon = \
        #     self.player_glop.deepcopy_with_my_type(weapon)

    def on_bump(self, glop_index, bumper_index):
        print("[ testing ] '" + self.glops[glop_index].name +
              "' was bumped by '" + self.glops[bumper_index].name +
              "'")

    def on_bump_world(self, glop_index, description):
        print("[ testing ] '" + self.glops[glop_index].name +
              "' was bumped by world '" + description + "'")

    def on_attacked_glop(self, attacked_index, attacker_index,
                         weapon_dict):
        missing_key_count = 0
        global item_dict
        if 'projectile_keys' in item_dict:
            for val in item_dict['projectile_keys']:
                if val not in weapon_dict:
                    print("[ testing ] projectile_key '" + val
                          + "' specified in projectile_keys"
                          " is missing from projectile_dict"
                          " provided to on_attacked_glop event")
                    missing_key_count += 1
        else:
            for key in item_dict:
                if key not in weapon_dict:
                    print("[ testing ] projectile_key '" + val
                          + "' specified in item_dict"
                          " is missing from projectile_dict"
                          " provided to on_attacked_glop event")
                    missing_key_count += 1

        if attacked_index is not None:
            dg = self.glops[attacked_index]
            if 'hp' in dg.actor_dict:
                dg.actor_dict['hp'] -= weapon_dict['hit_damage']
                if dg.actor_dict['hp'] <= 0:
                    self.explode_glop_at(attacked_index)
                    print("[ testing ] (on_attacked_glop:" +
                          " after exploding) HP: " +
                          str(dg.actor_dict['hp']))
                else:
                    print("[ testing ] (on_attacked_glop) HP: " +
                          str(dg.actor_dict['hp']))
            else:
                print("[ testing ] ERROR: no hp in '" + dg.name +
                      "'s actor dict: " + str(dg.actor_dict))
        else:
            # projectile hit environmental obstacle (no glop was hit)
            print("[ opengl7 ] projectile hit environmental obstacle")

    def on_obtain_glop(self, bumpable_index, bumper_index):
        if self.glops[bumpable_index].item_dict['name'] == 'barrel':
            self.play_sound("sounds/barrel,wooden-pickup.wav")
        elif self.glops[bumpable_index].item_dict['name'] == 'crate':
            self.play_sound("sounds/crate-pickup.wav")

    def _deprecated_on_obtain_glop_by_name(self, egn, rgn):
        pass
        # if 'barrel' in egn.lower():
        #     self.play_sound("sounds/barrel,wooden-pickup.wav")
        # if 'crate' in egn.lower():
        #     self.play_sound("sounds/crate-pickup.wav")

    # def on_explode_glop(self, pos, radius, attacked_index, weapon):
    #     print("on_explode_glop...Not Yet Implemented")
    #     pass

    def on_update_glops(self):
        if self.selected_glop is not None:
            if self._get_key_state_at("j"):
                self.selected_glop.rotate_y_relative(1)
            elif self._get_key_state_at("l"):
                self.selected_glop.rotate_y_relative(-1)
            elif self._get_key_state_at("i"):
                self.selected_glop.rotate_x_relative(-1)
            elif self._get_key_state_at("k"):
                self.selected_glop.rotate_x_relative(1)
            elif self._get_key_state_at("u"):
                self.selected_glop.rotate_z_relative(1)
            elif self._get_key_state_at("o"):
                self.selected_glop.rotate_z_relative(-1)

            if self._get_key_state_at('left'):
                self.selected_glop.move_x_relative(-.1)
            elif self._get_key_state_at('right'):
                self.selected_glop.move_x_relative(.1)
            elif self._get_key_state_at("up"):
                self.selected_glop.move_y_relative(.1)
            elif self._get_key_state_at("down"):
                self.selected_glop.move_y_relative(-.1)
            elif self._get_key_state_at("-"):
                self.selected_glop.move_z_relative(-.1)
            elif self._get_key_state_at("="):
                self.selected_glop.move_z_relative(.1)
        # else:
        #     print("No glop selected.")

        # this_index = find_by_name(self.scene.glops, "Suzanne")
        # if this_index>-1:
        #     if self._get_key_state_at("j"):
        #         self.scene.glops[this_index].rotate_y_relative(-1)
        #     elif self._get_key_state_at("l"):
        #         self.scene.glops[this_index].rotate_y_relative(1)
        # else:
        #     print("Object not found.")
        # this_index = find_by_name(self.scene.glops, "Suzanne")
        # if this_index > -1:
        #     self.scene.glops[this_index].rotate_z_relative(1)
        #     print("using index "+str(this_index))
        # else:
        #     print("Not found.")

        # this_glop = get_by_name(self.scene.glops, "Suzanne")
        # if this_glop is not None:
        #     this_glop.rotate_z_relative(1)
        # else:
        #     print("Not found.")


scene = MainScene(KivyGlopsWindow())


class KivyGlopsTestingApp(App):
    def build(self):
        # mainform = MainForm()
        return scene.ui
        # mainform = MainForm()
        # boxlayout = TextForm()
        # boxlayout.add_widget(mainform)
        # boxlayout.cols = 1
        # boxlayout.orientation = "vertical"
        # boxlayout.useButton = Factory.Button(text='use',
        #                                      id="useButton",
        #                                      size_hint=(.1,.1))
        # boxlayout.add_widget(boxlayout.useButton)
        # return boxlayout


if __name__ == "__main__":
    KivyGlopsTestingApp().run()
