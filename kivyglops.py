"""
This module is the Kivy implementation of PyGlops.
It provides features that are specific to display method
(Kivy's OpenGL-like API in this case).
"""
from pyglops import *

from kivy.resources import resource_find
from kivy.graphics import *
from kivy.uix.widget import Widget
from kivy.core.image import Image
from pyrealtime import *
from kivy.clock import Clock

#stuff required for KivyGlopsWindow
from kivy.app import App
from kivy.core.window import Window
from kivy.core.window import Keyboard
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import *
from kivy.graphics import *
#from kivy.input.providers.mouse import MouseMotionEvent
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle

from kivy.logger import Logger
from kivy.vector import Vector

from kivy.core.audio import SoundLoader

import timeit
from timeit import default_timer as best_timer


from common import *

import time
import random

#TODO: try adding captions and 2d axis indicators in canvas.after, or try RenderContext
sub_canvas_enable = False
missing_bumper_warning_enable = True
missing_bumpable_warning_enable = True
missing_radius_warning_enable = True

def get_distance_kivyglops(a_glop, b_glop):
    return math.sqrt((b_glop._translate_instruction.x - a_glop._translate_instruction.x)**2 +
                     (b_glop._translate_instruction.y - a_glop._translate_instruction.y)**2 +
                     (b_glop._translate_instruction.z - a_glop._translate_instruction.z)**2)

#def get_distance_vec3(a_vec3, b_vec3):
#    return math.sqrt((b_vec3[0] - a_vec3[0])**2 + (b_vec3[1] - a_vec3[1])**2 + (b_vec3[2] - a_vec3[2])**2)

def translate_to_string(_translate_instruction):
    result = "None"
    if _translate_instruction is not None:
        result = str([_translate_instruction.x, _translate_instruction.y, _translate_instruction.z])
    return result


class KivyGlopsMaterial(PyGlopsMaterial):

    def __init__(self):
        super(KivyGlopsMaterial, self).__init__()


def get_kivyglop_from_pyglop(this_pyglop):
    this_kivyglop = KivyGlop()
    this_kivyglop.name = this_pyglop.name
    this_kivyglop.source_path = this_pyglop.source_path
    this_kivyglop.properties = this_pyglop.properties
    this_kivyglop.vertex_depth = this_pyglop.vertex_depth
    this_kivyglop.material = this_pyglop.material
    this_kivyglop._min_coords = this_pyglop._min_coords
    this_kivyglop._max_coords = this_pyglop._max_coords
    this_kivyglop._pivot_point = this_pyglop._pivot_point
    this_kivyglop.eye_height = this_pyglop.eye_height
    this_kivyglop.hit_radius = this_pyglop.hit_radius
    this_kivyglop.item_dict = this_pyglop.item_dict
    this_kivyglop.bump_enable = this_pyglop.bump_enable
    this_kivyglop.reach_radius = this_pyglop.reach_radius
    this_kivyglop.is_out_of_range = this_pyglop.is_out_of_range
    this_kivyglop.physics_enable = this_pyglop.physics_enable
    this_kivyglop.x_velocity = this_pyglop.x_velocity
    this_kivyglop.y_velocity = this_pyglop.y_velocity
    this_kivyglop.z_velocity = this_pyglop.z_velocity
    this_kivyglop._cached_floor_y = this_pyglop._cached_floor_y
    this_kivyglop.infinite_inventory_enable = this_pyglop.infinite_inventory_enable
    this_kivyglop.bump_sounds = this_pyglop.bump_sounds

    this_kivyglop.vertex_format = this_pyglop.vertex_format
    this_kivyglop.vertices = this_pyglop.vertices
    this_kivyglop.indices = this_pyglop.indices
    #region vars moved to material
    #this_kivyglop.ambient_color = this_pyglop.ambient_color
    #this_kivyglop.diffuse_color = this_pyglop.diffuse_color
    #this_kivyglop.specular_color = this_pyglop.specular_color
    ##emissive_color = None  # vec4
    #this_kivyglop.specular_coefficent = this_pyglop.specular_coefficent
    #endregion vars moved to material
    #this_kivyglop.opacity = this_pyglop.opacity # use diffuse color 4th channel instead

    return this_kivyglop


class KivyGlop(PyGlop, Widget):

    #freeAngle = None
    #degreesPerSecond = None
    #freePos = None
    _mesh = None  # the (Kivy) Mesh object
    _calculated_size = None
    _translate_instruction = None
    _rotate_instruction_x = None
    _rotate_instruction_y = None
    _rotate_instruction_z = None
    _scale_instruction = None
    _color_instruction = None

    _pivot_scaled_point = None
    _pushmatrix = None
    _updatenormalmatrix = None
    _popmatrix = None



    def __init__(self):
        super(KivyGlop, self).__init__()
        #self.freeAngle = 0.0
        #self.degreesPerSecond = 0.0
        #self.freePos = (10.0,100.0)

        #TODO:
        #self.canvas = RenderContext()
        #self.canvas = RenderContext(compute_normal_mat=True)
        self.canvas = InstructionGroup()

        self._calculated_size = (1.0,1.0)  #finish this--or skip since only needed for getting pivot point
        #Rotate(angle=self.freeAngle, origin=(self._calculated_size[0]/2.0,self._calculated_size[1]/2.0))
        self._pivot_point = 0.0, 0.0, 0.0  #self.get_center_average_of_vertices()
        self._pivot_scaled_point = 0.0, 0.0, 0.0
        self._rotate_instruction_x = Rotate(0, 1, 0, 0)  #angle, x, y z
        self._rotate_instruction_x.origin = self._pivot_scaled_point
        self._rotate_instruction_y = Rotate(0, 0, 1, 0)  #angle, x, y z
        self._rotate_instruction_y.origin = self._pivot_scaled_point
        self._rotate_instruction_z = Rotate(0, 0, 0, 1)  #angle, x, y z
        self._rotate_instruction_z.origin = self._pivot_scaled_point
        self._scale_instruction = Scale(1.0,1.0,1.0)
        #self._scale_instruction.origin = self._pivot_point
        self._translate_instruction = Translate(0, 0, 0)
        self._color_instruction = Color(Color(1.0, 1.0, 1.0, 1.0))  # TODO: eliminate this in favor of canvas["mat_diffuse_color"]

    def get_context(self):
        return self.canvas

    def rotate_x_relative(self, angle):
        self._rotate_instruction_x.angle += angle

    def rotate_y_relative(self, angle):
        self._rotate_instruction_y.angle += angle

    def rotate_z_relative(self, angle):
        self._rotate_instruction_z.angle += angle

    def move_x_relative(self, distance):
        self._translate_instruction.x += distance

    def move_y_relative(self, distance):
        self._translate_instruction.y += distance

    def move_z_relative(self, distance):
        self._translate_instruction.z += distance

    def transform_pivot_to_geometry(self):
        super(KivyGlop, self).transform_pivot_to_geometry()
        #self._change_instructions()
        self._on_change_pivot()

    def _on_change_pivot(self):
        super(KivyGlop, self)._on_change_pivot()
        self._on_change_scale_instruction()

    def get_scale(self):
        return (self._scale_instruction.x + self._scale_instruction.y + self._scale_instruction.z) / 3.0

    def set_scale(self, overall_scale):
        self._scale_instruction.x = overall_scale
        self._scale_instruction.y = overall_scale
        self._scale_instruction.z = overall_scale
        self._on_change_scale_instruction()

    def _on_change_scale_instruction(self):
        if self._pivot_point is not None:
            self._pivot_scaled_point = self._pivot_point[0]*self._scale_instruction.x+self._translate_instruction.x, self._pivot_point[1]*self._scale_instruction.y+self._translate_instruction.y, self._pivot_point[2]*self._scale_instruction.z+self._translate_instruction.z
#         else:
#             self._pivot_point = 0,0,0
#             self._pivot_scaled_point = 0,0,0
        #super(KivyGlop, self)._on_change_scale()
        #if self._pivot_point is not None:
        self._rotate_instruction_x.origin = self._pivot_scaled_point
        self._rotate_instruction_y.origin = self._pivot_scaled_point
        self._rotate_instruction_z.origin = self._pivot_scaled_point
        #self._translate_instruction.x = self.freePos[0]-self._rectangle_instruction.size[0]*self._scale_instruction.x/2
        #self._translate_instruction.y = self.freePos[1]-self._rectangle_instruction.size[1]*self._scale_instruction.y/2
        #self._rotate_instruction.origin = self._rectangle_instruction.size[0]*self._scale_instruction.x/2.0, self._rectangle_instruction.size[1]*self._scale_instruction.x/2.0
        #self._rotate_instruction.angle = self.freeAngle
        this_name = ""
        if self.name is not None:
            this_name = self.name
        #print()
        #print("_on_change_scale_instruction for object named '"+this_name+"'")
        #print ("_pivot_point:"+str(self._pivot_point))
        #print ("_pivot_scaled_point:"+str(self._pivot_scaled_point))

    def apply_translate(self):
        vertex_count = int(len(self.vertices)/self.vertex_depth)
        v_offset = 0
        for v_number in range(0, vertex_count):
            self.vertices[v_offset+self._POSITION_OFFSET+0] -= self._translate_instruction.x
            self.vertices[v_offset+self._POSITION_OFFSET+1] -= self._translate_instruction.y
            self.vertices[v_offset+self._POSITION_OFFSET+2] -= self._translate_instruction.z
            self._pivot_point = (self._pivot_point[0] - self._translate_instruction.x,
                                 self._pivot_point[1] - self._translate_instruction.y,
                                 self._pivot_point[2] - self._translate_instruction.z)
            self._translate_instruction.x = 0.0
            self._translate_instruction.y = 0.0
            self._translate_instruction.z = 0.0
            v_offset += self.vertex_depth
        self.apply_pivot()

    def set_texture_diffuse(self, path):
        self.last_loaded_path = path
        this_texture_image = None
        if self.last_loaded_path is not None:
            participle = "getting image filename"
            try:
                participle = "loading "+self.last_loaded_path
                if os.path.isfile(self.last_loaded_path):
                    this_texture_image = Image(self.last_loaded_path)
                else:
                    this_texture_image = Image(resource_find(self.last_loaded_path))
                print("Loaded texture '"+str(self.last_loaded_path)+"'")
            except:
                print("Could not finish loading texture: " + self.last_loaded_path)
                view_traceback()
        else:
            if verbose_enable:
                Logger.debug("Warning: no texture specified for glop named '"+this_mesh_name+"'")
                this_material_name = ""
                if self.material is not None:
                    if self.material.name is not None:
                        this_material_name = self.material.name
                        Logger.debug("(material named '"+this_material_name+"')")
                    else:
                        Logger.debug("(material with no name)")
                else:
                    Logger.debug("(no material)")
        if self._mesh is not None and this_texture_image is not None:
            self._mesh.texture = this_texture_image.texture
        return this_texture_image

    def generate_kivy_mesh(self):
        participle = "checking for texture"
        self._mesh = None
        this_texture_image = self.set_texture_diffuse(self.get_texture_diffuse_path())
        participle = "assembling kivy Mesh"
        this_texture = None
        if len(self.vertices)>0:
            if (this_texture_image is not None):
                this_texture = this_texture_image.texture
                this_texture.wrap = 'repeat'  # does same as GL_REPEAT -- see https://gist.github.com/tshirtman/3868962#file-main-py-L15

            self._mesh = Mesh(
                    vertices=self.vertices,
                    indices=self.indices,
                    fmt=self.vertex_format,
                    mode='triangles',
                    texture=this_texture,
                )
            if verbose_enable:
                print(str(len(self.vertices))+" vert(ex/ices)")

        else:
            print("WARNING: 0 vertices in glop")
            if self.name is not None:
                print("  named "+self.name)


class KivyGlops(PyGlops):

    def __init__(self):
        super(KivyGlops, self).__init__()
        self.camera_glop = get_kivyglop_from_pyglop(self.camera_glop)
        self.glops.append(self.camera_glop)
        self._bumper_indices.append(len(self.glops)-1)

    def create_mesh(self):
        #return PyGlops.create_mesh(self)
        return KivyGlop()

    def create_material(self):
        return KivyGlopsMaterial()

class GLWidget(Widget):
    pass

class HudForm(BoxLayout):
    pass

class ContainerForm(BoxLayout):
    pass

class KivyGlopsWindow(ContainerForm):  # formerly a subclass of Widget
    IsVisualDebugMode = False
    scene = None
    camera_walk_units_per_second = None

    selected_glop = None
    selected_glop_index = None

    focal_distance = None

    mode = None

    look_point = None

    # moving_x = 0.0
    # moving_z = 0.0
    # _turning_y = 0.0
    controllers = list()
    player1_controller = None
    _previous_world_light_dir = None
    _previous_camera_rotate_y_angle = None
    _world_cube = None
    projection_near = None
    world_boundary_min = None
    world_boundary_max = None
    _meshes = None # so gl operations can be added in realtime (after resetCallback is added, but so resetCallback is on the stack after them)
    gl_widget = None
    hud_form = None
    hud_buttons_form = None
    _sounds = None
    use_button = None
    _visual_debug_enable = None
    hud_bg_rect = None
    env_rectangle = None
    screen_w_arc_theta = None
    screen_h_arc_theta = None

    def load_glops(self):
        print("Warning: you should subclass KivyGlopsWindow and implement load_glops (and usually update_glops for changing objects each frame)")

    def update_glops(self):
        pass

    def set_fly(self, fly_enable):
        self.scene.set_fly(fly_enable)

    def set_hud_background(self, path):
        if path is not None:
            original_path = path
            if not os.path.isfile(path):
                path = resource_find(path)
            if path is not None:
                self.hud_form.canvas.before.clear()
                #self.hud_form.canvas.before.add(Color(1.0,1.0,1.0,1.0))
                self.hud_bg_rect = Rectangle(size=self.hud_form.size,
                                             pos=self.hud_form.pos,
                                             source=path)
                self.hud_form.canvas.before.add(self.hud_bg_rect)
                self.hud_form.source = path
            else:
                print("ERROR in set_hud_image: could not find "+original_path)
        else:
            print("ERROR in set_hud_image: path is None")

    def set_background_cylmap(self, path):
        print("NOT YET IMPLEMENTED: set_background_cylmap")
        #self.load_obj("env_sphere.obj")
        #self.load_obj("maps/gi/etc/sky_sphere.obj")
        #env_indices = self.get_indices_by_source_path("env_sphere.obj")
        #for i in range(0,len(env_indices)):
        #    index = env_indices[i]
        #    print("Preparing sky object "+str(index))
        #    self.scene.glops[index].set_texture_diffuse(path)
        if self.env_rectangle is not None:
            self.canvas.before.remove(self.env_rectangle)
        original_path = path
        if path is not None:
            if not os.path.isfile(path):
                path = resource_find(path)
            if path is not None:
                #texture = CoreImage(path).texture
                #texture.wrap = repeat
                #self.env_rectangle = Rectangle(texture=texture)
                self.env_rectangle = Rectangle(source=path)
                self.env_rectangle.texture.wrap = "repeat"
                self.canvas.before.add(self.env_rectangle)
            else:
                print("ERROR in set_background_cylmap: "+original_path+" not found in search path")
        else:
            print("ERROR in set_background_cylmap: path is None")

    def __init__(self, **kwargs):
        self._visual_debug_enable = False
        self.gl_widget = GLWidget()
        self.hud_form = HudForm(orientation="vertical", size_hint=(1.0, 1.0))
        self.hud_buttons_form = BoxLayout(orientation="horizontal",
                                          size_hint=(1.0, 0.1))
        self.world_boundary_min = [None,None,None]
        self.world_boundary_max = [None,None,None]
        self.camera_walk_units_per_second = 12.0
        self.camera_turn_radians_per_second = math.radians(90.0)
        self.mode = MODE_EDIT
        self.player1_controller = PyRealTimeController()
        self.controllers.append(self.player1_controller)
        self.focal_distance = 2.0
        self.projection_near = 0.1
        self._sounds = {}
        try:
            self._keyboard = Window.request_keyboard(
                self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
            self._keyboard.bind(on_key_up=self._on_keyboard_up)
        except:
            print("Could not finish loading keyboard" +
                  "(keyboard may not be present).")

        #self.bind(on_touch_down=self.canvasTouchDown)

        self.scene = KivyGlops()
        self.gl_widget.canvas = RenderContext(compute_normal_mat=True)
        self.gl_widget.canvas["_world_light_dir"] = (0.0, 0.5, 1.0)
        self.gl_widget.canvas["_world_light_dir_eye_space"] = (0.0, 0.5, 1.0) #rotated in update_glsl
        self.gl_widget.canvas["camera_light_multiplier"] = (1.0, 1.0, 1.0, 1.0)
        #self.gl_widget.canvas.shader.source = resource_find('simple1b.glsl')
        #self.gl_widget.canvas.shader.source = resource_find('shade-kivyglops-standard.glsl')  # NOT working
        #self.gl_widget.canvas.shader.source = resource_find('shade-normal-only.glsl') #partially working
        #self.gl_widget.canvas.shader.source = resource_find('shade-texture-only.glsl')
        #self.gl_widget.canvas.shader.source = resource_find('shade-kivyglops-minimal.glsl')  # NOT working
        self.gl_widget.canvas.shader.source = resource_find('fresnel.glsl')

        #formerly, .obj was loaded here using load_obj (now calling program does that)

        #print(self.gl_widget.canvas.shader)  #just prints type and memory address
        if dump_enable:
            glopsYAMLLines = []
            self.scene.append_dump(glopsYAMLLines)
            try:
                thisFile = open('glops-dump.yml', 'w')
                for i in range(0,len(glopsYAMLLines)):
                    thisFile.write(glopsYAMLLines[i]+"\n")
                thisFile.close()
            except:
                print("Could not finish writing dump.")
        super(KivyGlopsWindow, self).__init__(**kwargs)
        self.cb = Callback(self.setup_gl_context)
        self.gl_widget.canvas.add(self.cb)

        self.gl_widget.canvas.add(PushMatrix())

        #self.gl_widget.canvas.add(PushMatrix())
        #self.gl_widget.canvas.add(this_texture)
        #self.gl_widget.canvas.add(Color(1, 1, 1, 1))
        #for this_glop_index in range(0,len(self.scene.glops)):
        #    this_mesh_name = ""
        #    #thisMesh = KivyGlop()
        #    this_glop = self.scene.glops[this_glop_index]
        #    add_glop(this_glop)
        #self.gl_widget.canvas.add(PopMatrix())
        self._meshes = InstructionGroup() #RenderContext(compute_normal_mat=True)
        self.gl_widget.canvas.add(self._meshes)

        self.finalize_canvas()
        self.add_widget(self.gl_widget)
        #self.hud_form.rows = 1
        self.add_widget(self.hud_form)
        self.debug_label = Factory.Label(text="...")
        if not self._visual_debug_enable:
            self.debug_label.opacity = 0.0
        self.hud_form.add_widget(self.debug_label)
        self.hud_form.add_widget(self.hud_buttons_form)
        self.inventory_prev_button = Factory.Button(text="<", id="inventory_prev_button", size_hint=(.2,1.0), on_press=self.inventory_prev_button_press)
        self.use_button = Factory.Button(text="0: Empty", id="use_button", size_hint=(.2,1.0), on_press=self.inventory_use_button_press)
        self.inventory_next_button = Factory.Button(text=">", id="inventory_next_button", size_hint=(.2,1.0), on_press=self.inventory_next_button_press)
        self.hud_buttons_form.add_widget(self.inventory_prev_button)
        self.hud_buttons_form.add_widget(self.use_button)
        self.hud_buttons_form.add_widget(self.inventory_next_button)


        #Window.bind(on_motion=self.on_motion)  #TODO: why doesn't this work?

        #x,y,z where y is up:
        self.scene.camera_glop._translate_instruction.x = 0
        self.scene.camera_glop._translate_instruction.y = self.scene.camera_glop.eye_height
        self.scene.camera_glop._translate_instruction.z = 25


        #This is done axis by axis--the only reason is so that you can do OpenGL 6 (boundary detection) lesson from expertmultimedia.com starting with this file
        if self.world_boundary_min[0] is not None:
            if self.scene.camera_glop._translate_instruction.x < self.world_boundary_min[0]:
                self.scene.camera_glop._translate_instruction.x = self.world_boundary_min[0]
        if self.world_boundary_min[1] is not None:
            if self.scene.camera_glop._translate_instruction.y < self.world_boundary_min[1]: #this is done only for this axis, just so that you can do OpenGL 6 lesson using this file (boundary detection)
                self.scene.camera_glop._translate_instruction.y = self.world_boundary_min[1]
        if self.world_boundary_min[2] is not None:
            if self.scene.camera_glop._translate_instruction.z < self.world_boundary_min[2]: #this is done only for this axis, just so that you can do OpenGL 6 lesson using this file (boundary detection)
                self.scene.camera_glop._translate_instruction.z = self.world_boundary_min[2]
        self.scene.camera_glop._rotate_instruction_x.angle = 0.0
        self.scene.camera_glop._rotate_instruction_y.angle = math.radians(-90.0)  # [math.radians(-90.0), 0.0, 1.0, 0.0]
        self.scene.camera_glop._rotate_instruction_z.angle = 0.0
        self.camera_ax = 0
        self.camera_ay = 0
        Clock.schedule_interval(self.update_glsl, 1.0 / self.scene.frames_per_second)
        #Clock.schedule_once(self.update_glsl, 1.0)
        #Clock.schedule_once(self.update_glsl, 1.0)
        self.camera_walk_units_per_frame = self.camera_walk_units_per_second / self.scene.frames_per_second
        self.camera_turn_radians_per_frame = self.camera_turn_radians_per_second / self.scene.frames_per_second

        self._touches = []

        #fix incorrect keycodes in kivy 1.8.0:
        if (Keyboard.keycodes["-"]==41):
            Keyboard.keycodes["-"]=45
        if (Keyboard.keycodes["="]==43):
            Keyboard.keycodes["="]=61

        self.load_glops()

    def inventory_prev_button_press(self, instance):
        event_dict = self.scene.camera_glop.select_next_inventory_slot(False)
        self.after_selected_item(event_dict)

    def inventory_use_button_press(self, instance):
        event_dict = self.use_selected(self.scene.camera_glop)
        #self.after_selected_item(event_dict)

    def inventory_next_button_press(self, instance):
        event_dict = self.scene.camera_glop.select_next_inventory_slot(True)
        self.after_selected_item(event_dict)

    def after_selected_item(self, select_item_event_dict):
        name = None
        #proper_name = None
        inventory_index = None
        if select_item_event_dict is not None:
            calling_method_string = ""
            if "calling_method" in select_item_event_dict:
                calling_method_string = select_item_event_dict["calling_method"]
            if "name" in select_item_event_dict:
                name = select_item_event_dict["name"]
            else:
                print("ERROR in after_selected_item ("+calling_method_string+"): missing name in select_item_event_dict")
            #if "proper_name" in select_item_event_dict:
            #    proper_name = select_item_event_dict["proper_name"]
            #else:
            #    print("ERROR in after_selected_item ("+calling_method_string+"): missing proper_name in select_item_event_dict")
            if "inventory_index" in select_item_event_dict:
                inventory_index = select_item_event_dict["inventory_index"]
            else:
                print("ERROR in after_selected_item ("+calling_method_string+"): missing inventory_index in select_item_event_dict")
        self.use_button.text=str(inventory_index)+": "+str(name)

    def preload_sound(self, path):
        if path is not None:
            if path not in self._sounds:
                self._sounds[path] = {}
                print("loading "+path)
                self._sounds[path]["loader"] = SoundLoader.load(path)

    def play_sound(self, path, loop=False):
        if path is not None:
            self.preload_sound(path)
            if self._sounds[path]:
                if verbose_enable:
                    print("playing "+path)
                self._sounds[path]["loader"].play()
            else:
                print("Failed to play "+path)
        else:
            print("ERROR in play_sound: path is None")

    def play_music(self, path, loop=True):
        self.play_sound(path, loop=loop)  #TODO: handle on_stop and play again if loop=True

    def _internal_bump_glop(self, bumpable_index, bumper_index):
        bumpable_name = self.scene.glops[bumpable_index].name
        bumper_name = self.scene.glops[bumper_index].name
        #result =
        self.bump_glop(bumpable_name, bumper_name)
        #if result is not None:
            #if "bumpable_name" in result:
            #    bumpable_name = result["bumpable_name"]
            #if "bumper_name" in result:
            #    bumper_name = result["bumper_name"]
        #asdf remove if bumpable_glop.item_dict.

        #if bumpable_name is not None and bumper_name is not None:
        if self.scene.glops[bumpable_index].item_dict is not None:
            if "bump" in self.scene.glops[bumpable_index].item_dict:
                self.scene.glops[bumpable_index].is_out_of_range = False  #prevents repeated bumping until out of range again
                if self.scene.glops[bumpable_index].bump_enable:
                    if self.scene.glops[bumpable_index].item_dict["bump"] is not None:
                        commands = self.scene.glops[bumpable_index].item_dict["bump"].split(";")
                        for command in commands:
                            command = command.strip()
                            if command=="hide":
                                self._meshes.remove(self.scene.glops[bumpable_index].get_context())
                                self.scene.glops[bumpable_index].bump_enable = False
                            elif command=="obtain":
                                self.obtain_glop(bumpable_name, bumper_name)
                                item_event = self.scene.camera_glop.push_glop_item(self.scene.glops[bumpable_index], bumpable_index)
                                #process item event so selected inventory slot gets updated in case obtained item ends up in it:
                                self.after_selected_item(item_event)
                                if verbose_enable:
                                    print(command+" "+self.scene.glops[bumpable_index].name)
                            else:
                                print("Glop named "+str(self.scene.glops[bumpable_index].name)+" attempted an unknown glop command (in bump event): "+str(command))
                    else:
                        print("self.scene.glops[bumpable_index].item_dict['bump'] is None")
            else:
                print("self.scene.glops[bumpable_index].item_dict does not contain 'bump'")
        else:
            print("bumped object '"+str(self.scene.glops[bumpable_index].name)+"' is not an item")

    def bump_glop(self, bumpable_name, bumper_name):
        return None

    def obtain_glop(self, bumpable_name, bumper_name):
        return None


    def finalize_canvas(self):
        self.gl_widget.canvas.add(PopMatrix())

        self.resetCallback = Callback(self.reset_gl_context)
        self.gl_widget.canvas.add(self.resetCallback)

    def get_nearest_walkmesh_vec3_using_xz(self, pt):
        result = None
        closest_distance = None
        poly_sides_count = 3
        #corners = list()
        #for i in range(0,poly_sides_count):
        #    corners.append( (0.0, 0.0, 0.0) )
        for this_glop in self.scene._walkmeshes:
            face_i = 0
            indices_count = len(this_glop.indices)
            while (face_i<indices_count):
                v_offset = this_glop.indices[face_i]*this_glop.vertex_depth
                a_vertex = this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+0], this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+1], this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+2]
                v_offset = this_glop.indices[face_i+1]*this_glop.vertex_depth
                b_vertex = this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+0], this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+1], this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+2]
                v_offset = this_glop.indices[face_i+2]*this_glop.vertex_depth
                c_vertex = this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+0], this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+1], this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+2]
                #side_a_distance = get_distance_vec3_xz(pt, a_vertex, b_vertex)
                #side_b_distance = get_distance_vec3_xz(pt, b_vertex, c_vertex)
                #side_c_distance = get_distance_vec3_xz(pt, c_vertex, a_vertex)
                this_point = get_nearest_vec3_on_vec3line_using_xz(pt, a_vertex, b_vertex)
                this_distance = this_point[3] #4th index of returned tuple is distance
                tri_distance = this_distance
                tri_point = this_point

                this_point = get_nearest_vec3_on_vec3line_using_xz(pt, b_vertex, c_vertex)
                this_distance = this_point[3] #4th index of returned tuple is distance
                if this_distance < tri_distance:
                    tri_distance = this_distance
                    tri_point = this_point

                this_point = get_nearest_vec3_on_vec3line_using_xz(pt, c_vertex, a_vertex)
                this_distance = this_point[3] #4th index of returned tuple is distance
                if this_distance < tri_distance:
                    tri_distance = this_distance
                    tri_point = this_point

                if (closest_distance is None) or (tri_distance<closest_distance):
                    result = tri_point[0], tri_point[1], tri_point[2]  # ok to return y since already swizzled (get_nearest_vec3_on_vec3line_using_xz copies source's y to return's y)
                    closest_distance = tri_distance
                face_i += poly_sides_count
        return result

    def get_nearest_walkmesh_vertex_using_xz(self, pt):
        result = None
        second_nearest_pt = None
        for this_glop in self.scene._walkmeshes:
            X_i = this_glop._POSITION_OFFSET + 0
            Y_i = this_glop._POSITION_OFFSET + 1
            Z_i = this_glop._POSITION_OFFSET + 2
            X_abs_i = X_i
            Y_abs_i = Y_i
            Z_abs_i = Z_i
            v_len = len(this_glop.vertices)
            distance_min = None
            while X_abs_i < v_len:
                distance = math.sqrt( (pt[0]-this_glop.vertices[X_abs_i+0])**2 + (pt[2]-this_glop.vertices[X_abs_i+2])**2 )
                if (result is None) or (distance_min) is None or (distance<distance_min):
                    #if result is not None:
                        #second_nearest_pt = result[0],result[1],result[2]
                    result = this_glop.vertices[X_abs_i+0], this_glop.vertices[X_abs_i+1], this_glop.vertices[X_abs_i+2]
                    distance_min = distance
                X_abs_i += this_glop.vertex_depth

            #DOESN'T WORK since second_nearest_pt may not be on edge
            #if second_nearest_pt is not None:
            #    distance1 = get_distance_vec3_xz(pt, result)
            #    distance2 = get_distance_vec3_xz(pt, second_nearest_pt)
            #    distance_total=distance1+distance2
            #    distance1_weight = distance1/distance_total
            #    distance2_weight = distance2/distance_total
            #    result = result[0]*distance1_weight+second_nearest_pt[0]*distance2_weight, result[1]*distance1_weight+second_nearest_pt[1]*distance2_weight, result[2]*distance1_weight+second_nearest_pt[2]*distance2_weight
                #TODO: use second_nearest_pt to get nearest location along the edge instead of warping to a vertex
        return result

    def is_in_any_walkmesh_xz(self, check_vec3):
        return get_container_walkmesh_and_poly_index_xz(check_vec3) is not None

    def get_container_walkmesh_and_poly_index_xz(self, check_vec3):
        result = None
        X_i = 0
        second_i = 2  # actually z since ignoring y
        check_vec2 = check_vec3[X_i], check_vec3[second_i]
        walkmesh_i = 0
        while walkmesh_i < len(self.scene._walkmeshes):
            this_glop = self.scene._walkmeshes[walkmesh_i]
            X_i = this_glop._POSITION_OFFSET + 0
            second_i = this_glop._POSITION_OFFSET + 2
            poly_side_count = 3
            poly_count = int(len(this_glop.indices)/poly_side_count)
            poly_offset = 0
            for poly_index in range(0,poly_count):
                if (  is_in_triangle_vec2( check_vec2, (this_glop.vertices[this_glop.indices[poly_offset]*this_glop.vertex_depth+X_i],this_glop.vertices[this_glop.indices[poly_offset]*this_glop.vertex_depth+second_i]), (this_glop.vertices[this_glop.indices[poly_offset+1]*this_glop.vertex_depth+X_i],this_glop.vertices[this_glop.indices[poly_offset+1]*this_glop.vertex_depth+second_i]), (this_glop.vertices[this_glop.indices[poly_offset+2]*this_glop.vertex_depth+X_i],this_glop.vertices[this_glop.indices[poly_offset+2]*this_glop.vertex_depth+second_i]) )  ):
                    result = dict()
                    result["walkmesh_index"] = walkmesh_i
                    result["polygon_offset"] = poly_offset
                    break
                poly_offset += poly_side_count
            walkmesh_i += 1
        return result

    def use_walkmesh(self, name, hide=True):
        result = False
        #for this_glop in self.scene.glops:
        for index in range(0, len(self.scene.glops)):
            if self.scene.glops[index].name == name:
                result = True
                if self.scene.glops[index] not in self.scene._walkmeshes:
                    self.scene._walkmeshes.append(self.scene.glops[index])
                    print("Applying walkmesh translate "+translate_to_string(self.scene.glops[index]._translate_instruction))
                    self.scene.glops[index].apply_translate()
                    print("  pivot:"+str(self.scene.glops[index]._pivot_point))
                    if hide:
                        self._meshes.remove(self.scene.glops[index].get_context())
                break
        return result

    def get_similar_names(self, partial_name):
        results = None
        checked_count = 0
        if partial_name is not None and len(partial_name)>0:
            partial_name_lower = partial_name.lower()
            results = list()
            for this_glop in self.scene.glops:
                checked_count += 1
                #print("checked "+this_glop.name.lower())
                if this_glop.name is not None:
                    if partial_name_lower in this_glop.name.lower():
                        results.append(this_glop.name)
        #print("checked "+str(checked_count))
        return results

    def get_indices_by_source_path(self, source_path):
        results = None
        checked_count = 0
        if source_path is not None and len(source_path)>0:
            results = list()
            for index in range(0,len(self.scene.glops)):
                this_glop = self.scene.glops[index]
                checked_count += 1
                #print("checked "+this_glop.name.lower())
                if this_glop.source_path is not None:
                    if source_path == this_glop.source_path:
                        results.append(index)
        #print("checked "+str(checked_count))
        return results


    def get_indices_of_similar_names(self, partial_name):
        results = None
        checked_count = 0
        if partial_name is not None and len(partial_name)>0:
            partial_name_lower = partial_name.lower()
            results = list()
            for index in range(0,len(self.scene.glops)):
                this_glop = self.scene.glops[index]
                checked_count += 1
                #print("checked "+this_glop.name.lower())
                if this_glop.name is not None:
                    if partial_name_lower in this_glop.name.lower():
                        results.append(index)
        #print("checked "+str(checked_count))
        return results

    def load_obj(self, source_path, swapyz_enable=False, centered=False):
        if swapyz_enable:
            print("NOT YET IMPLEMENTED: swapyz_enable")
        if source_path is not None:
            original_path = source_path
            source_path = resource_find(source_path)
            if source_path is not None:
                if os.path.isfile(source_path):
                    #super(KivyGlops, self).load_obj(source_path)
                    new_glops = self.scene.get_pyglops_list_from_obj(source_path)
                    if new_glops is None:
                        print("FAILED TO LOAD '"+str(source_path)+"'")
                    elif len(new_glops)<1:
                        print("NO VALID OBJECTS FOUND in '"+str(source_path)+"'")
                    else:
                        if self.scene.glops is None:
                            self.scene.glops = list()

                        #for index in range(0,len(self.glops)):
                        favorite_pivot_point = None
                        for index in range(0,len(new_glops)):
                            new_glops[index] = get_kivyglop_from_pyglop(new_glops[index])
                            #this_glop = new_glops[index]
                            #this_glop = KivyGlop(pyglop=self.glops[index])
                            #if len(self.glops<=index):
                                #self.glops.append(this_glop)
                            #else:
                                #self.glops[index]=this_glop
                            print("")
                            if (favorite_pivot_point is None):
                                favorite_pivot_point = new_glops[index]._pivot_point

                        print("  applying pivot points...")
                        for index in range(0,len(new_glops)):
                            #apply pivot point (so that glop's _translate_instruction is actually the center)
                            prev_pivot = new_glops[index]._pivot_point[0], new_glops[index]._pivot_point[1], new_glops[index]._pivot_point[2]
                            new_glops[index].apply_pivot()
                            #print("    moving from "+str( (new_glops[index]._translate_instruction.x, new_glops[index]._translate_instruction.y, new_glops[index]._translate_instruction.z) ))
                            new_glops[index]._translate_instruction.x = prev_pivot[0]
                            new_glops[index]._translate_instruction.y = prev_pivot[1]
                            new_glops[index]._translate_instruction.z = prev_pivot[2]
                            new_glops[index].generate_kivy_mesh()
                            self.add_glop(new_glops[index])
                        if centered:
                            #TODO: apply pivot point instead (change vertices as if pivot point were 0,0,0) to ensure translate 0 is world 0; instead of:
                            #center it (use only one pivot point, so all objects in obj file remain aligned with each other):
                            for index in range(0,len(new_glops)):
                                print("  centering from "+str(favorite_pivot_point))
                                new_glops[index].move_x_relative(-1.0*favorite_pivot_point[0])
                                new_glops[index].move_y_relative(-1.0*favorite_pivot_point[1])
                                new_glops[index].move_z_relative(-1.0*favorite_pivot_point[2])
                                #TODO: new_glops[index].apply_translate()
                                #TODO: new_glops[index].reset_translate()

                        print("")
                else:
                    print("missing '"+source_path+"'")
            else:
                print("missing '"+original_path+"'")
        else:
            print("ERROR: source_path is None for load_obj")


    def add_glop(self, this_glop):
        participle="initializing"
        try:
            #context = self._meshes
            #context = self.gl_widget.canvas
            #if self.selected_glop_index is None:
            #    self.selected_glop_index = this_glop_index
            #    self.selected_glop = this_glop
            self.selected_glop_index = len(self.scene.glops)
            self.selected_glop = this_glop
            context = this_glop.get_context()
            this_mesh_name = ""
            if this_glop.name is not None:
                this_mesh_name = this_glop.name
            this_glop._pushmatrix = PushMatrix()
            context.add(this_glop._pushmatrix)
            context.add(this_glop._translate_instruction)
            context.add(this_glop._rotate_instruction_x)
            context.add(this_glop._rotate_instruction_y)
            context.add(this_glop._rotate_instruction_z)
            context.add(this_glop._scale_instruction)
            #self.scale = Scale(0.6)
            #m = list(self.scene.glops.values())[0]
            #context.add(m)
            this_glop._updatenormalmatrix = UpdateNormalMatrix()
            context.add(this_glop._updatenormalmatrix)

            if this_glop._mesh is None:
                this_glop.generate_kivy_mesh()
                print("WARNING: glop had no mesh, so was generated when added to render context. Please ensure it is a KivyGlop and not a PyGlop (however, vertex indices misread could also lead to missing Mesh object).")
            print("_color_instruction.r,.g,.b,.a: "+str( [this_glop._color_instruction.r, this_glop._color_instruction.g, this_glop._color_instruction.b, this_glop._color_instruction.a] ))
            print("u_color: "+str(this_glop.material.diffuse_color))

            context.add(this_glop._color_instruction)  #TODO: asdf add as uniform instead
            if this_glop._mesh is not None:
                context.add(this_glop._mesh)
                if verbose_enable:
                    print("Added mesh to render context.")
            else:
                print("NOT adding mesh.")
            this_glop._popmatrix = PopMatrix()
            context.add(this_glop._popmatrix)
            if self.scene.glops is None:
                self.scene.glops = list()
            self.scene.glops.append(this_glop)

            self._meshes.add(context)

            if verbose_enable:
                print("Appended Glop (count:"+str(len(self.scene.glops))+").")

        except:
            print("ERROR: Could not finish "+participle+" in KivyGlops load_obj")
            view_traceback()

    def set_world_boundary_by_object(self, thisGlopsMesh, use_x, use_y, use_z):
        self._world_cube = thisGlopsMesh
        if (self._world_cube is not None):
            self.world_boundary_min = [self._world_cube.get_min_x(), None, self._world_cube.get_min_z()]
            self.world_boundary_max = [self._world_cube.get_max_x(), None, self._world_cube.get_max_z()]

            for axis_index in range(0,3):
                if self.world_boundary_min[axis_index] is not None:
                    self.world_boundary_min[axis_index] += self.projection_near + 0.1
                if self.world_boundary_max[axis_index] is not None:
                    self.world_boundary_max[axis_index] -= self.projection_near + 0.1
        else:
            self.world_boundary_min = [None,None,None]
            self.world_boundary_max = [None,None,None]


    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)

    def rotate_view_relative(self, angle, axis_index):
        #TODO: delete this method and see solutions from http://stackoverflow.com/questions/10048018/opengl-camera-rotation
        #such as set_view method of https://github.com/sgolodetz/hesperus2/blob/master/Shipwreck/MapEditor/GUI/Camera.java
        self.rotate_view_relative_around_point(angle, axis_index, self.scene.camera_glop._translate_instruction.x, self.scene.camera_glop._translate_instruction.y, self.scene.camera_glop._translate_instruction.z)

    def rotate_view_relative_around_point(self, angle, axis_index, around_x, around_y, around_z):
        if axis_index == 0:  #x
            # += around_y * math.tan(angle)
            self.scene.camera_glop._rotate_instruction_x.angle += angle
            # origin_distance = math.sqrt(around_z*around_z + around_y*around_y)
            # self.scene.camera_glop._translate_instruction.z += origin_distance * math.cos(-1*angle)
            # self.scene.camera_glop._translate_instruction.y += origin_distance * math.sin(-1*angle)
        elif axis_index == 1:  #y
            self.scene.camera_glop._rotate_instruction_y.angle += angle
            # origin_distance = math.sqrt(around_x*around_x + around_z*around_z)
            # self.scene.camera_glop._translate_instruction.x += origin_distance * math.cos(-1*angle)
            # self.scene.camera_glop._translate_instruction.z += origin_distance * math.sin(-1*angle)
        else:  #z
            #self.scene.camera_glop._translate_instruction.z += around_y * math.tan(angle)
            self.scene.camera_glop._rotate_instruction_z.angle += angle
            # origin_distance = math.sqrt(around_x*around_x + around_y*around_y)
            # self.scene.camera_glop._translate_instruction.x += origin_distance * math.cos(-1*angle)
            # self.scene.camera_glop._translate_instruction.y += origin_distance * math.sin(-1*angle)

    def axis_index_to_string(self,index):
        result = "unknown axis"
        if (index==0):
            result = "x"
        elif (index==1):
            result = "y"
        elif (index==2):
            result = "z"
        return result



    def set_as_item(self, glop_name, template_dict):
        result = False
        if glop_name is not None:
            for i in range(0,len(self.scene.glops)):
                if self.scene.glops[i].name == glop_name:
                    self.set_as_item_by_index(i, template_dict)
                    break

    def add_bump_sound_by_index(self, i, path):
        if path not in self.scene.glops[i].bump_sounds:
            self.scene.glops[i].bump_sounds.append(path)

    def set_as_item_by_index(self, i, template_dict):
        result = False
        item_dict = get_dict_deepcopy(template_dict)  #prevents every item template from being the one
        self.scene.glops[i].item_dict = item_dict
        self.scene.glops[i].item_dict["glop_name"] = self.scene.glops[i].name
        self.scene.glops[i].item_dict["glop_index"] = i
        self.scene.glops[i].bump_enable = True
        self.scene.glops[i].is_out_of_range = True  # allows item to be obtained instantly at start of main event loop
        self.scene.glops[i].hit_radius = 0.1

        this_glop = self.scene.glops[i]
        vertex_count = int(len(this_glop.vertices)/this_glop.vertex_depth)
        v_offset = 0
        min_y = None
        for v_number in range(0, vertex_count):
            if min_y is None or this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+1] < min_y:
                min_y = this_glop.vertices[v_offset+this_glop._POSITION_OFFSET+1]
            v_offset += this_glop.vertex_depth
        if min_y is not None:
            self.scene.glops[i].hit_radius = min_y
            if self.scene.glops[i].hit_radius < 0.0:
                self.scene.glops[i].hit_radius = 0.0 - self.scene.glops[i].hit_radius
        else:
            print("ERROR: could not read any y values from glop named "+str(this_glop.name))
        #self.scene.glops[i].hit_radius = 1.0
        self.scene._bumpable_indices.append(i)
        return result

    def use_selected(self, user_glop):
        if user_glop is not None:
            if user_glop.properties is not None:
                if "inventory_items" in user_glop.properties:
                    if "inventory_index" in user_glop.properties:
                        try:
                            if user_glop.properties["inventory_index"] > -1:
                                user_glop.properties["inventory_items"][user_glop.properties["inventory_index"]]
                                this_item = user_glop.properties["inventory_items"][user_glop.properties["inventory_index"]]
                                glop_index = None
                                item_glop = None
                                if "glop_index" in this_item:
                                    glop_index = this_item["glop_index"]
                                    if glop_index is not None:
                                        item_glop = self.scene.glops[glop_index]
                                if item_glop is not None:
                                    if item_glop.item_dict is not None:
                                        if "use" in item_glop.item_dict:
                                            is_ready = True
                                            if "cooldown" in item_glop.item_dict:
                                                is_ready = False
                                                if ("RUNTIME_last_used_time" not in item_glop.item_dict) or (time.time() - item_glop.item_dict["RUNTIME_last_used_time"]):
                                                    if ("RUNTIME_last_used_time" in item_glop.item_dict):
                                                        is_ready = True
                                                    #else Don't assume cooled down when obtained, otherwise rapid firing items will be allowed
                                                    item_glop.item_dict["RUNTIME_last_used_time"] = time.time()
                                            if is_ready:
                                                if "use_sound" in item_glop.item_dict:
                                                    self.play_sound(item_glop.item_dict["use_sound"])
                                                print(item_glop.item_dict["use"]+" "+item_glop.name)
                                                if "throw_" in item_glop.item_dict["use"]:  # such as item_dict["throw_arc"]

                                                    self.scene.glops[item_glop.item_dict["glop_index"]].physics_enable = True
                                                    throw_speed = 1.0 # meters/sec
                                                    try:

                                                        x_angle = user_glop._rotate_instruction_x.angle + math.radians(30)
                                                        if x_angle > math.radians(90):
                                                            x_angle = math.radians(90)
                                                        self.scene.glops[item_glop.item_dict["glop_index"]].y_velocity = throw_speed * math.sin(x_angle)
                                                        horizontal_throw_speed = throw_speed * math.cos(x_angle)
                                                        self.scene.glops[item_glop.item_dict["glop_index"]].x_velocity = horizontal_throw_speed * math.cos(user_glop._rotate_instruction_y.angle)
                                                        self.scene.glops[item_glop.item_dict["glop_index"]].z_velocity = horizontal_throw_speed * math.sin(user_glop._rotate_instruction_y.angle)

                                                    except:
                                                        self.scene.glops[item_glop.item_dict["glop_index"]].x_velocity = 0
                                                        self.scene.glops[item_glop.item_dict["glop_index"]].z_velocity = 0
                                                        print("Could not finish getting throw x,,z values")
                                                        view_traceback()

                                                    self.scene.glops[item_glop.item_dict["glop_index"]].is_out_of_range = False
                                                    self.scene.glops[item_glop.item_dict["glop_index"]].bump_enable = True
                                                    event_dict = user_glop.pop_glop_item(user_glop.properties["inventory_index"])
                                                    self.after_selected_item(event_dict)
                                                    item_glop._translate_instruction.x = user_glop._translate_instruction.x
                                                    item_glop._translate_instruction.y = user_glop._translate_instruction.y
                                                    item_glop._translate_instruction.z = user_glop._translate_instruction.z
                                                    self._meshes.add(item_glop.get_context())
                                        else:
                                            print(item_glop.name+" has no use.")
                                    else:
                                        print("ERROR: tried to use a glop that is not an item (this should not be in "+str(user_glop.name)+"'s inventory)")
                                #self.scene.glops[
                        except:
                            print("user_glop.name:"+str(user_glop.name))
                            print('user_glop.properties["inventory_index"]:'+str(user_glop.properties["inventory_index"]))
                            print('len(user_glop.properties["inventory_items"]):'+str(len(user_glop.properties["inventory_items"])))
                            print("Could not finish use_selected:")
                            view_traceback()

    def update_glsl(self, *largs):
        #print("coords:"+str(Window.mouse_pos))
        #see also asp and clip_top in init
        #screen_w_arc_theta = 32.0  # actual number is from proj matrix
        #screen_h_arc_theta = 18.0  # actual number is from proj matrix
        if self.env_rectangle is not None:
            if self.screen_w_arc_theta is not None and self.screen_h_arc_theta is not None:
                #region old way (does not repeat)
                #env_h_ratio = (2 * math.pi) / self.screen_h_arc_theta
                #env_w_ratio = env_h_ratio * math.pi
                #self.env_rectangle.size = (Window.size[0]*env_w_ratio,
                                           #Window.size[1]*env_h_ratio)
                #self.env_rectangle.pos = (-(self.scene.camera_glop._rotate_instruction_y.angle/(2*math.pi)*self.env_rectangle.size[0]),
                                          #-(self.scene.camera_glop._rotate_instruction_x.angle/(2*math.pi)*self.env_rectangle.size[1]))
                #engregion old way (does not repeat)
                self.env_rectangle.size = Window.size
                self.env_rectangle.pos = 0.0, 0.0
                view_right = self.screen_w_arc_theta / 2.0 + self.scene.camera_glop._rotate_instruction_y.angle
                view_left = view_right - self.screen_w_arc_theta
                view_top = self.screen_h_arc_theta / 2.0 + self.scene.camera_glop._rotate_instruction_x.angle + 90.0
                view_bottom = view_top - self.screen_h_arc_theta
                circle_theta = 2*math.pi
                view_right_ratio = view_right / circle_theta
                view_left_ratio = view_left / circle_theta
                view_top_ratio = view_top / circle_theta
                view_bottom_ratio = view_bottom / circle_theta
                #tex_coords order: u,      v,      u + w,  v,
                #                  u + w,  v + h,  u,      v + h
                # as per https://kivy.org/planet/2014/02/using-tex_coords-in-kivy-for-fun-and-profit/
                self.env_rectangle.tex_coords = view_left_ratio, view_bottom_ratio, view_right_ratio, view_bottom_ratio, \
                                                view_right_ratio, view_top_ratio, view_left_ratio, view_top_ratio


        self.hud_form.pos = 0.0, 0.0
        self.hud_form.size = Window.size
        if self.hud_bg_rect is not None:
            self.hud_bg_rect.size = self.hud_form.size
            self.hud_bg_rect.pos=self.hud_form.pos

        x_rad, y_rad = self.get_view_angles_by_pos_rad(Window.mouse_pos)
        self.scene.camera_glop._rotate_instruction_y.angle = x_rad
        self.scene.camera_glop._rotate_instruction_x.angle = y_rad
        got_frame_delay = 0.0
        if self.scene.last_update_s is not None:
            got_frame_delay = best_timer() - self.scene.last_update_s
        self.scene.last_update_s = best_timer()

        self.update_glops()
        rotation_multiplier_y = 0.0  # 1.0 is maximum speed
        moving_x = 0.0  # 1.0 is maximum speed
        moving_y = 0.0  # 1.0 is maximum speed
        moving_z = 0.0  # 1.0 is maximum speed; NOTE: increased z should move object closer to viewer in right-handed coordinate system
        moving_theta = 0.0
        position_change = [0.0, 0.0, 0.0]
        # for keycode strings, see  http://kivy.org/docs/_modules/kivy/core/window.html
        if self.player1_controller.get_pressed(Keyboard.keycodes["a"]):
            #if self.player1_controller.get_pressed(Keyboard.keycodes["shift"]):
            moving_x = 1.0
            #else:
            #    rotation_multiplier_y = -1.0
        if self.player1_controller.get_pressed(Keyboard.keycodes["d"]):
            #if self.player1_controller.get_pressed(Keyboard.keycodes["shift"]):
            moving_x = -1.0
            #else:
            #    rotation_multiplier_y = 1.0
        if self.player1_controller.get_pressed(Keyboard.keycodes["w"]):
            if self.scene._fly_enable:
                #intentionally use z,y:
                moving_z, moving_y = get_rect_from_polar_rad(1.0, self.scene.camera_glop._rotate_instruction_x.angle)
            else:
                moving_z = 1.0

        if self.player1_controller.get_pressed(Keyboard.keycodes["s"]):
            if self.scene._fly_enable:
                #intentionally use z,y:
                moving_z, moving_y = get_rect_from_polar_rad(1.0, self.scene.camera_glop._rotate_instruction_x.angle)
                moving_z *= -1.0
                moving_y *= -1.0
            else:
                moving_z = -1.0

        if self.player1_controller.get_pressed(Keyboard.keycodes["enter"]):
            self.use_selected(self.scene.camera_glop)

        if rotation_multiplier_y != 0.0:
            delta_y = self.camera_turn_radians_per_frame * rotation_multiplier_y
            self.scene.camera_glop._rotate_instruction_y.angle += delta_y
            #origin_distance = math.sqrt(self.scene.camera_glop._translate_instruction.x*self.scene.camera_glop._translate_instruction.x + self.scene.camera_glop._translate_instruction.z*self.scene.camera_glop._translate_instruction.z)
            #self.scene.camera_glop._translate_instruction.x -= origin_distance * math.cos(delta_y)
            #self.scene.camera_glop._translate_instruction.z -= origin_distance * math.sin(delta_y)

        #xz coords of edges of 16x16 square are:
        # move in the direction you are facing
        moving_theta = 0.0
        if moving_x != 0.0 or moving_y != 0.0 or moving_z != 0.0:
            #makes movement relative to rotation (which alaso limits speed when moving diagonally):
            moving_theta = theta_radians_from_rectangular(moving_x, moving_z)
            moving_r_multiplier = math.sqrt((moving_x*moving_x)+(moving_z*moving_z))
            if moving_r_multiplier > 1.0:
                moving_r_multiplier = 1.0  # Limited so that you can't move faster when moving diagonally


            #TODO: reprogram so adding math.radians(-90) is not needed (?)
            position_change[0] = self.camera_walk_units_per_frame*moving_r_multiplier * math.cos(self.scene.camera_glop._rotate_instruction_y.angle+moving_theta+math.radians(-90))
            position_change[1] = self.camera_walk_units_per_frame*moving_y
            position_change[2] = self.camera_walk_units_per_frame*moving_r_multiplier * math.sin(self.scene.camera_glop._rotate_instruction_y.angle+moving_theta+math.radians(-90))

            # if (self.scene.camera_glop._translate_instruction.x + move_by_x > self._world_cube.get_max_x()):
            #     move_by_x = self._world_cube.get_max_x() - self.scene.camera_glop._translate_instruction.x
            #     print(str(self.scene.camera_glop._translate_instruction.x)+" of max_x:"+str(self._world_cube.get_max_x()))
            # if (self.scene.camera_glop._translate_instruction.z + move_by_z > self._world_cube.get_max_z()):
            #     move_by_z = self._world_cube.get_max_z() - self.scene.camera_glop._translate_instruction.z
            #     print(str(self.scene.camera_glop._translate_instruction.z)+" of max_z:"+str(self._world_cube.get_max_z()))
            # if (self.scene.camera_glop._translate_instruction.x + move_by_x < self._world_cube.get_min_x()):
            #     move_by_x = self._world_cube.get_min_x() - self.scene.camera_glop._translate_instruction.x
            #     print(str(self.scene.camera_glop._translate_instruction.x)+" of max_x:"+str(self._world_cube.get_max_x()))
            # if (self.scene.camera_glop._translate_instruction.z + move_by_z < self._world_cube.get_min_z()):
            #     move_by_z = self._world_cube.get_min_z() - self.scene.camera_glop._translate_instruction.z
            #     print(str(self.scene.camera_glop._translate_instruction.z)+" of max_z:"+str(self._world_cube.get_max_z()))

            #print(str(self.scene.camera_glop._translate_instruction.x)+","+str(self.scene.camera_glop._translate_instruction.z)+" each coordinate should be between matching one in "+str(self._world_cube.get_min_x())+","+str(self._world_cube.get_min_z())+" and "+str(self._world_cube.get_max_x())+","+str(self._world_cube.get_max_z()))
            #print(str( (self.scene.camera_glop._translate_instruction.x, self.scene.camera_glop._translate_instruction.y, self.scene.camera_glop._translate_instruction.z) )+" each coordinate should be between matching one in "+str(self.world_boundary_min)+" and "+str(self.world_boundary_max))

        #for axis_index in range(0,3):
        if position_change[0] is not None:
            self.scene.camera_glop._translate_instruction.x += position_change[0]
        if position_change[1] is not None:
            self.scene.camera_glop._translate_instruction.y += position_change[1]
        if position_change[2] is not None:
            self.scene.camera_glop._translate_instruction.z += position_change[2]

        if len(self.scene._walkmeshes)>0:
            walkmesh_result = self.get_container_walkmesh_and_poly_index_xz( (self.scene.camera_glop._translate_instruction.x, self.scene.camera_glop._translate_instruction.y, self.scene.camera_glop._translate_instruction.z) )
            if walkmesh_result is None:
                #print("Out of bounds")
                corrected_pos = None
                #if self.scene.prev_inbounds_camera_translate is not None:
                #    self.scene.camera_glop._translate_instruction.x = self.scene.prev_inbounds_camera_translate[0]
                #    self.scene.camera_glop._translate_instruction.y = self.scene.prev_inbounds_camera_translate[1]
                #    self.scene.camera_glop._translate_instruction.z = self.scene.prev_inbounds_camera_translate[2]
                #else:
                corrected_pos = self.get_nearest_walkmesh_vec3_using_xz( (self.scene.camera_glop._translate_instruction.x, self.scene.camera_glop._translate_instruction.y, self.scene.camera_glop._translate_instruction.z) )
                if corrected_pos is not None:
                    pushed_angle = get_angle_between_two_vec3_xz( (self.scene.camera_glop._translate_instruction.x, self.scene.camera_glop._translate_instruction.y, self.scene.camera_glop._translate_instruction.z), corrected_pos)
                    corrected_pos = get_pushed_vec3_xz_rad(corrected_pos, self.scene.camera_glop.hit_radius, pushed_angle)
                    self.scene.camera_glop._translate_instruction.x = corrected_pos[0]
                    self.scene.camera_glop._translate_instruction.y = corrected_pos[1]   # TODO: check y (vertical) axis against eye height and jump height etc
                    #+ self.scene.camera_glop.eye_height #no longer needed since swizzled to xz (get_nearest_walkmesh_vec3_using_xz returns original's y in return's y)
                    self.scene.camera_glop._translate_instruction.z = corrected_pos[2]
                #else:
                #    print("ERROR: could not find point to bring player in bounds.")
            else:
                #print("In bounds")
                result_glop = self.scene._walkmeshes[walkmesh_result["walkmesh_index"]]
                X_i = result_glop._POSITION_OFFSET + 0
                Y_i = result_glop._POSITION_OFFSET + 1
                Z_i = result_glop._POSITION_OFFSET + 2
                ground_tri = list()
                ground_tri.append( (result_glop.vertices[result_glop.indices[walkmesh_result["polygon_offset"]]*result_glop.vertex_depth+X_i], result_glop.vertices[result_glop.indices[walkmesh_result["polygon_offset"]]*result_glop.vertex_depth+Y_i], result_glop.vertices[result_glop.indices[walkmesh_result["polygon_offset"]]*result_glop.vertex_depth+Z_i]) )
                ground_tri.append( (result_glop.vertices[result_glop.indices[walkmesh_result["polygon_offset"]+1]*result_glop.vertex_depth+X_i], result_glop.vertices[result_glop.indices[walkmesh_result["polygon_offset"]+1]*result_glop.vertex_depth+Y_i], result_glop.vertices[result_glop.indices[walkmesh_result["polygon_offset"]+1]*result_glop.vertex_depth+Z_i]) )
                ground_tri.append( (result_glop.vertices[result_glop.indices[walkmesh_result["polygon_offset"]+2]*result_glop.vertex_depth+X_i], result_glop.vertices[result_glop.indices[walkmesh_result["polygon_offset"]+2]*result_glop.vertex_depth+Y_i], result_glop.vertices[result_glop.indices[walkmesh_result["polygon_offset"]+2]*result_glop.vertex_depth+Z_i]) )
                #self.scene.camera_glop._translate_instruction.y = ground_tri[0][1] + self.scene.camera_glop.eye_height
                ground_y = get_y_from_xz(ground_tri[0], ground_tri[1], ground_tri[2], self.scene.camera_glop._translate_instruction.x, self.scene.camera_glop._translate_instruction.z)
                self.scene.camera_glop._translate_instruction.y = ground_y + self.scene.camera_glop.eye_height
                if self.scene._world_min_y is None or ground_y < self.scene._world_min_y:
                    self.scene._world_min_y = ground_y
                #if self.scene.prev_inbounds_camera_translate is None or self.scene.camera_glop._translate_instruction.y != self.scene.prev_inbounds_camera_translate[1]:
                    #print("y:"+str(self.scene.camera_glop._translate_instruction.y))
        else:
            #print("No bounds")
            pass
        self.scene.prev_inbounds_camera_translate = self.scene.camera_glop._translate_instruction.x, self.scene.camera_glop._translate_instruction.y, self.scene.camera_glop._translate_instruction.z

        # else:
        #     self.scene.camera_glop._translate_instruction.x += self.camera_walk_units_per_frame * moving_x
        #     self.scene.camera_glop._translate_instruction.z += self.camera_walk_units_per_frame * moving_z

        #if verbose_enable:
        #    print("update_glsl...")
        asp = float(self.width) / float(self.height)

        clip_top = 0.06  #NOTE: 0.03 is ~1.72 degrees, if that matters
        # formerly field_of_view_factor
        # was changed to .03 when projection_near was changed from 1 to .1
        # was .3 when projection_near was 1

        clip_right = asp*clip_top  # formerly overwrote asp
        proj = Matrix()
        modelViewMatrix = Matrix()

        #modelViewMatrix.rotate(self.scene.camera_glop._rotate_instruction_x.angle,1.0,0.0,0.0)
        #modelViewMatrix.rotate(self.scene.camera_glop._rotate_instruction_y.angle,0.0,1.0,0.0)
        #look_at(eyeX, eyeY, eyeZ, centerX, centerY, centerZ, upX, upY, upZ)  $http://kivy.org/docs/api-kivy.graphics.transformation.html
        #modelViewMatrix.rotate(self.scene.camera_glop._rotate_instruction_z.angle,0.0,0.0,1.0)
        previous_look_point = None
        if self.look_point is not None:
            previous_look_point = self.look_point[0], self.look_point[1], self.look_point[2]

        self.look_point = [0.0,0.0,0.0]

        #0 is the angle (1, 2, and 3 are the matrix)
        self.look_point[0] = self.focal_distance * math.cos(self.scene.camera_glop._rotate_instruction_y.angle)
        self.look_point[2] = self.focal_distance * math.sin(self.scene.camera_glop._rotate_instruction_y.angle)

        #self.look_point[1] = 0.0  #(changed in "for" loop below) since y is up, and 1 is y, ignore index 1 when we are rotating on that axis
        self.look_point[1] = self.focal_distance * math.sin(self.scene.camera_glop._rotate_instruction_x.angle)


        #modelViewMatrix = modelViewMatrix.look_at(0,self.scene.camera_glop._translate_instruction.y,0, self.look_point[0], self.look_point[1], self.look_point[2], 0, 1, 0)

        #Since what you are looking at should be relative to yourself, add camera's position:

        self.look_point[0] += self.scene.camera_glop._translate_instruction.x
        self.look_point[1] += self.scene.camera_glop._translate_instruction.y
        self.look_point[2] += self.scene.camera_glop._translate_instruction.z

        #must translate first, otherwise look_at will override position on rotation axis ('y' in this case)
        modelViewMatrix.translate(self.scene.camera_glop._translate_instruction.x, self.scene.camera_glop._translate_instruction.y, self.scene.camera_glop._translate_instruction.z)
        #moving_theta = theta_radians_from_rectangular(moving_x, moving_z)
        modelViewMatrix = modelViewMatrix.look_at(self.scene.camera_glop._translate_instruction.x, self.scene.camera_glop._translate_instruction.y, self.scene.camera_glop._translate_instruction.z, self.look_point[0], self.look_point[1], self.look_point[2], 0, 1, 0)



        #proj.view_clip(left, right, bottom, top, near, far, perspective)
        #"In OpenGL, a 3D point in eye space is projected onto the near plane (projection plane)"
        # -http://www.songho.ca/opengl/gl_projectionmatrix.html
        #The near plane and far plane distances are in the -z direction but are
        # expressed as positive values since they are distances from the camera
        # then they are compressed to -1 to 1
        # -https://www.youtube.com/watch?v=frtzb2WWECg
        proj = proj.view_clip(-clip_right, clip_right, -1*clip_top, clip_top, self.projection_near, 100, 1)
        top_theta = theta_radians_from_rectangular(self.projection_near, clip_top)
        right_theta = theta_radians_from_rectangular(self.projection_near, clip_right)
        self.screen_w_arc_theta = right_theta*2.0
        self.screen_h_arc_theta = top_theta*2.0

        self.gl_widget.canvas['projection_mat'] = proj
        self.gl_widget.canvas['modelview_mat'] = modelViewMatrix
        self.gl_widget.canvas["camera_world_pos"] = [self.scene.camera_glop._translate_instruction.x, self.scene.camera_glop._translate_instruction.y, self.scene.camera_glop._translate_instruction.z]
        #if verbose_enable:
        #    Logger.debug("ok (update_glsl)")

        is_look_point_changed = False
        if previous_look_point is not None:
            for axis_index in range(3):
                if self.look_point[axis_index] != previous_look_point[axis_index]:
                    is_look_point_changed = True
                    #print(str(self.look_point)+" was "+str(previous_look_point))
                    break
        else:
            is_look_point_changed = True

        if is_look_point_changed:
            pass
            #print("Now looking at "+str(self.look_point))
            #print ("position: "+str( (self.scene.camera_glop._translate_instruction.x, self.scene.camera_glop._translate_instruction.y, self.scene.camera_glop._translate_instruction.z) )+"; self.scene.camera_glop._rotate_instruction_y.angle:"+str(self.scene.camera_glop._rotate_instruction_y.angle) +"("+str(math.degrees(self.scene.camera_glop._rotate_instruction_y.angle))+"degrees); moving_theta:"+str(math.degrees(moving_theta))+" degrees")

        if (self._previous_world_light_dir is None
            or self._previous_world_light_dir[0]!=self.gl_widget.canvas["_world_light_dir"][0]
            or self._previous_world_light_dir[1]!=self.gl_widget.canvas["_world_light_dir"][1]
            or self._previous_world_light_dir[2]!=self.gl_widget.canvas["_world_light_dir"][2]
            or self._previous_camera_rotate_y_angle is None
            or self._previous_camera_rotate_y_angle != self.scene.camera_glop._rotate_instruction_y.angle
            ):
            #self.gl_widget.canvas["_world_light_dir"] = (0.0,.5,1.0);
            #self.gl_widget.canvas["_world_light_dir_eye_space"] = (0.0,.5,1.0);
            world_light_theta = theta_radians_from_rectangular(self.gl_widget.canvas["_world_light_dir"][0], self.gl_widget.canvas["_world_light_dir"][2])
            light_theta = world_light_theta+self.scene.camera_glop._rotate_instruction_y.angle
            light_r = math.sqrt((self.gl_widget.canvas["_world_light_dir"][0]*self.gl_widget.canvas["_world_light_dir"][0])+(self.gl_widget.canvas["_world_light_dir"][2]*self.gl_widget.canvas["_world_light_dir"][2]))
            self.gl_widget.canvas["_world_light_dir_eye_space"] = light_r * math.cos(light_theta), self.gl_widget.canvas["_world_light_dir_eye_space"][1], light_r * math.sin(light_theta)
            self._previous_camera_rotate_y_angle = self.scene.camera_glop._rotate_instruction_y.angle
            self._previous_world_light_dir = self.gl_widget.canvas["_world_light_dir"][0], self.gl_widget.canvas["_world_light_dir"][1], self.gl_widget.canvas["_world_light_dir"][2]

        global missing_bumper_warning_enable
        global missing_bumpable_warning_enable
        global missing_radius_warning_enable
        for bumpable_index_index in range(0, len(self.scene._bumpable_indices)):
            bumpable_index = self.scene._bumpable_indices[bumpable_index_index]
            bumpable_name = self.scene.glops[bumpable_index].name
            if self.scene.glops[bumpable_index].bump_enable is True:
                for bumper_index_index in range(0,len(self.scene._bumper_indices)):
                    bumper_index = self.scene._bumper_indices[bumper_index_index]
                    bumper_name = self.scene.glops[bumper_index].name
                    distance = get_distance_kivyglops(self.scene.glops[bumpable_index], self.scene.glops[bumper_index])
                    if self.scene.glops[bumpable_index].hit_radius is not None and self.scene.glops[bumpable_index].hit_radius is not None:
                        total_hit_radius = self.scene.glops[bumpable_index].hit_radius+self.scene.glops[bumper_index].reach_radius
                        if distance <= total_hit_radius:
                            if self.scene.glops[bumpable_index].is_out_of_range:  # only run if ever moved away from it
                                if self.scene.glops[bumpable_index].bump_enable:
                                    #print("distance:"+str(total_hit_radius)+" <= total_hit_radius:"+str(total_hit_radius))
                                    #print("bumper:"+str( (self.scene.glops[bumper_index]._translate_instruction.x, self.scene.glops[bumper_index]._translate_instruction.y, self.scene.glops[bumper_index]._translate_instruction.z) ) +
                                    #      "; bumped:"+str( (self.scene.glops[bumpable_index]._translate_instruction.x, self.scene.glops[bumpable_index]._translate_instruction.y, self.scene.glops[bumpable_index]._translate_instruction.z) ))
                                    self._internal_bump_glop(bumpable_index, bumper_index)
                        else:
                            self.scene.glops[bumpable_index].is_out_of_range = True
                            #print("did not bump "+str(bumpable_name)+" (bumper is at "+str( (self.scene.camera_glop._translate_instruction.x,self.scene.camera_glop._translate_instruction.y,self.scene.camera_glop._translate_instruction.z) )+")")
                            pass
                    else:
                        if missing_radius_warning_enable:
                            print("WARNING: Missing radius while checking bumped named "+str(bumpable_name))
                            missing_radius_warning_enable = False
            if self.scene.glops[bumpable_index]._cached_floor_y is None:
                self.scene.glops[bumpable_index]._cached_floor_y = self.scene._world_min_y
                #TODO: get from walkmesh instead
            if self.scene.glops[bumpable_index].physics_enable:
                if self.scene.glops[bumpable_index]._cached_floor_y is not None:
                    if self.scene.glops[bumpable_index]._translate_instruction.y - self.scene.glops[bumpable_index].hit_radius - kEpsilon > self.scene.glops[bumpable_index]._cached_floor_y:
                        self.scene.glops[bumpable_index]._translate_instruction.x += self.scene.glops[bumpable_index].x_velocity
                        self.scene.glops[bumpable_index]._translate_instruction.y += self.scene.glops[bumpable_index].y_velocity
                        self.scene.glops[bumpable_index]._translate_instruction.z += self.scene.glops[bumpable_index].z_velocity
                        if got_frame_delay > 0.0:
                            #print("  GRAVITY AFFECTED:"+str(self.scene.glops[bumpable_index]._translate_instruction.y)+" += "+str(self.scene.glops[bumpable_index].y_velocity))
                            self.scene.glops[bumpable_index].y_velocity -= self.scene._world_grav_acceleration * got_frame_delay
                            #print("  THEN VELOCITY CHANGED TO:"+str(self.scene.glops[bumpable_index].y_velocity))
                            #print("  FRAME INTERVAL:"+str(got_frame_delay))
                        else:
                            print("missing delay")
                    else:
                        #if self.scene.glops[bumpable_index].z_velocity > kEpsilon:
                        if (self.scene.glops[bumpable_index].y_velocity < 0.0 - (kEpsilon + self.scene.glops[bumpable_index].hit_radius)):
                            #print("  HIT GROUND Y:"+str(self.scene.glops[bumpable_index]._cached_floor_y))
                            if self.scene.glops[bumpable_index].bump_sounds is not None and len(self.scene.glops[bumpable_index].bump_sounds) > 0:
                                rand_i = random.randrange(0,len(self.scene.glops[bumpable_index].bump_sounds))
                                self.play_sound(self.scene.glops[bumpable_index].bump_sounds[rand_i])
                        self.scene.glops[bumpable_index]._translate_instruction.y = self.scene.glops[bumpable_index]._cached_floor_y + self.scene.glops[bumpable_index].hit_radius
                        self.scene.glops[bumpable_index].x_velocity = 0.0
                        self.scene.glops[bumpable_index].y_velocity = 0.0
                        self.scene.glops[bumpable_index].z_velocity = 0.0

    #end update_glsl

    #def get_view_angles_by_touch_deg(self, touch):
    #    # formerly define_rotate_angle(self, touch):
    #    x_angle = (touch.dx/self.width)*360
    #    y_angle = -1*(touch.dy/self.height)*360
    #    return x_angle, y_angle

    #def get_view_angles_by_pos_deg(self, pos):
    #    x_angle = (pos[0]/self.width)*360
    #    y_angle = -1*(pos[1]/self.height)*360
    #    return x_angle, y_angle

    def get_view_angles_by_pos_rad(self, pos):
        x_angle = -math.pi + (float(pos[0])/float(self.width-1))*(2.0*math.pi)
        y_angle = -(math.pi/2.0) + (float(pos[1])/float(self.height-1))*(math.pi)
        self.debug_label.text = "View:" + "\n  pos:" + str(pos) + \
            "\n  size:" + str( (self.width, self.height) ) + \
            "\n  pitch,yaw:" + str( (int(math.degrees(x_angle)),
                                  int(math.degrees(y_angle))) )
        if self.screen_w_arc_theta is not None and self.screen_h_arc_theta is not None:
            self.debug_label.text += "\n field of view: " + \
                str( (int(math.degrees(self.screen_w_arc_theta)),
                    int(math.degrees(self.screen_h_arc_theta))) )
        return x_angle, y_angle

#     def canvasTouchDown(self, touch, *largs):
#         touchX, touchY = largs[0].pos
#         #self.player1.targetX = touchX
#         #self.player1.targetY = touchY
#         print("\n")
#         print(str(largs).replace("\" ","\"\n"))

    def on_touch_down(self, touch):
        super(KivyGlopsWindow, self).on_touch_down(touch)
        #touch.grab(self)
        #self._touches.append(touch)

#         thisTouch = MouseMotionEvent(touch)
#         thisTouch.
        if touch.is_mouse_scrolling:
            event_dict = None
            if touch.button == "scrolldown":
                event_dict = self.scene.camera_glop.select_next_inventory_slot(True)
            else:
                event_dict = self.scene.camera_glop.select_next_inventory_slot(False)
            self.after_selected_item(event_dict)
        else:
            event_dict = self.use_selected(self.scene.camera_glop)

    def on_touch_up(self, touch):
        super(KivyGlopsWindow, self).on_touch_up(touch)
        #touch.ungrab(self)
        #self._touches.remove(touch)
        #self.player1_controller.dump()

    def print_location(self):
        if verbose_enable:
            Logger.debug("self.camera_walk_units_per_second:"+str(self.camera_walk_units_per_second)+"; location:"+str( (self.scene.camera_glop._translate_instruction.x, self.scene.camera_glop._translate_instruction.y, self.scene.camera_glop._translate_instruction.z) ))

    def get_pressed(self, key_name):
        return self.player1_controller.get_pressed(Keyboard.keycodes[key_name])

    def toggle_visual_debug(self):
        if not self._visual_debug_enable:
            self._visual_debug_enable = True
            self.debug_label.opacity = 1.0
        else:
            self._visual_debug_enable = False
            self.debug_label.opacity = 0.0


    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
#         print('The key' + str(keycode) + ' pressed')
#         print(' - text is ' + text)
#         print(' - modifiers are '+ str(modifiers))

        #print("pressed keycode "+str(keycode[0])+" (should match keycode constant: "+str(Keyboard.keycodes[keycode[1]])+")")

        #if len(keycode[1])>0:
        self.player1_controller.set_pressed(keycode[0], keycode[1], True)

        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if keycode[1] == 'escape':
            pass  #keyboard.release()
        # elif keycode[1] == 'w':
        #     self.scene.camera_glop._translate_instruction.z += self.camera_walk_units_per_frame
        # elif keycode[1] == 's':
        #     self.scene.camera_glop._translate_instruction.z -= self.camera_walk_units_per_frame
        # elif text == 'a':
        #     self.player1_controller["left"] = True
        #     self.moving_x = -1.0
        # elif text == 'd':
        #     self.moving_x = 1.0
        #     self.player1_controller["right"] = True
#         elif keycode[1] == '.':
#             self.look_at_center()
#         elif keycode[1] == 'numpadadd':
#             pass
#         elif keycode[1] == 'numpadsubtract' or keycode[1] == 'numpadsubstract':  #since is mispelled as numpadsubstract in kivy
#             pass
        elif keycode[1] == "tab":
            self.select_mesh_by_index(self.selected_glop_index+1)
            #if verbose_enable:
            this_name = None
            if self.selected_glop_index is not None:
                this_name = "["+str(self.selected_glop_index)+"]"
            if self.selected_glop is not None and self.selected_glop.name is not None:
                this_name = self.selected_glop.name
            if this_name is not None:
                print('Selected glop: '+this_name)
            else:
                print('Select glop failed (maybe there are no glops loaded.')
        elif keycode[1] == "x":
            event_dict = self.scene.camera_glop.select_next_inventory_slot(True)
            self.after_selected_item(event_dict)
        elif keycode[1] == "z":
            event_dict = self.scene.camera_glop.select_next_inventory_slot(False)
            self.after_selected_item(event_dict)
        elif keycode[1] == "f3":
            self.toggle_visual_debug()
        # else:
        #     print('Pressed unused key: ' + str(keycode) + "; text:"+text)

        if verbose_enable:
            self.print_location()
            print("scene.camera_glop._rotate_instruction_y.angle:"+str(self.scene.camera_glop._rotate_instruction_y.angle))
            print("modelview_mat:"+str(self.gl_widget.canvas['modelview_mat']))
        self.update_glsl()
        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

    def _on_keyboard_up(self, keyboard, keycode):
        self.player1_controller.set_pressed(keycode[0], keycode[1], False)
        #print('Released key ' + str(keycode))

    def select_mesh_by_index(self, index):
        glops_count = len(self.scene.glops)
        if (index>=glops_count):
            index=0
        if verbose_enable:
            Logger.debug("trying to select index "+str(index)+" (count is "+str(glops_count)+")...")
        if (glops_count > 0):
            self.selected_glop_index = index
            self.selected_glop = self.scene.glops[index]
        else:
            self.selected_glop = None
            self.selected_glop_index = None

    def _keyboard_closed(self):
        print('Keyboard disconnected!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    #def on_motion(self, etype, motionevent):
        #print("coords:"+str(motionevent.dx)+","+str(motionevent.dx))
        # will receive all motion events.
        #pass

    def on_touch_move(self, touch):
        #print("touch.dx:"+str(touch.dx)+" touch.dy:"+str(touch.dx))
        pass
#         print ("on_touch_move")
#         print (str(touch))
#         #Logger.debug("dx: %s, dy: %s. Widget: (%s, %s)" % (touch.dx, touch.dy, self.width, self.height))
#         #self.update_glsl()
#         if touch in self._touches and touch.grab_current == self:
#             if len(self._touches) == 1:
#                 # here do just rotation
#                 ax, ay = self.define_rotate_angle(touch)
#
#
#                 self.rotx.angle += ax
#                 self.roty.angle += ay
#
#                 #ax, ay = math.radians(ax), math.radians(ay)
#
#
#             elif len(self._touches) == 2: # scaling here
#                 #use two touches to determine do we need scal
#                 touch1, touch2 = self._touches
#                 old_pos1 = (touch1.x - touch1.dx, touch1.y - touch1.dy)
#                 old_pos2 = (touch2.x - touch2.dx, touch2.y - touch2.dy)
#
#                 old_dx = old_pos1[0] - old_pos2[0]
#                 old_dy = old_pos1[1] - old_pos2[1]
#
#                 old_distance = (old_dx*old_dx + old_dy*old_dy)
#                 Logger.debug('Old distance: %s' % old_distance)
#
#                 new_dx = touch1.x - touch2.x
#                 new_dy = touch1.y - touch2.y
#
#                 new_distance = (new_dx*new_dx + new_dy*new_dy)
#
#                 Logger.debug('New distance: %s' % new_distance)
#                 self.camera_walk_units_per_frame = self.camera_walk_units_per_second / self.scene.frames_per_second
#                 #self.camera_walk_units_per_frame = 0.01
#
#                 if new_distance > old_distance:
#                     scale = -1*self.camera_walk_units_per_frame
#                     Logger.debug('Scale up')
#                 elif new_distance == old_distance:
#                     scale = 0
#                 else:
#                     scale = self.camera_walk_units_per_frame
#                     Logger.debug('Scale down')
#
#                 if scale:
#                     self.scene.camera_glop._translate_instruction.z += scale
#                     print(str(scale) + " " + (self.scene.camera_glop._translate_instruction.x, self.scene.camera_glop._translate_instruction.y, self.scene.camera_glop._translate_instruction.z) )
#             self.update_glsl()

