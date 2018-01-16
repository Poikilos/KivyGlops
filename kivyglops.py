"""
This module is the Kivy implementation of PyGlops.
It provides features that are specific to display method
(Kivy's OpenGL-like API in this case).
"""
__author__ = 'Jake Gustafson'
import hashlib
from pyglops import *
import uuid

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

from common import *

import time
import random

nearest_not_found_warning_enable = True
_multicontext_enable = False  # only should be set while not running
print("[ kivyglops.py ] default _multicontext_enable: " + \
      str(_multicontext_enable))
#region changed automatically after showing error only once
bounds_warning_enable = True
look_at_none_warning_enable = True
look_at_pos_none_warning_enable = True
missing_bumpable_warning_enable = True
missing_bumper_warning_enable = True
missing_radius_warning_enable = True
no_bounds_warning_enable = True
#out_of_hitbox_note_enable = True
show_zero_degrees_pf_warning_enable = True  # pf is per frame
show_zero_walk_upf_warning_enable = True  # upf is units per frame
#endregion changed automatically after showing error only once

def get_distance_kivyglops(a_glop, b_glop):
    return math.sqrt((b_glop._t_ins.x - a_glop._t_ins.x)**2 +
                     (b_glop._t_ins.y - a_glop._t_ins.y)**2 +
                     (b_glop._t_ins.z - a_glop._t_ins.z)**2)

#def get_distance_vec3(a_vec3, b_vec3):
#    return math.sqrt((b_vec3[0] - a_vec3[0])**2 + (b_vec3[1] - a_vec3[1])**2 + (b_vec3[2] - a_vec3[2])**2)

#NOTE: use str(_t_ins.xyz) instead
#def translate_to_string(_t_ins):
#    result = "None"
#    if _t_ins is not None:
#        result = str([_t_ins.x, _t_ins.y, _t_ins.z])
#    return result


class KivyGlopsMaterial(PyGlopsMaterial):

    def __init__(self):
        super(KivyGlopsMaterial, self).__init__()

    def new_material_method(self):
        return KivyGlopsMaterial()

    def get_class_name(self):
        return "KivyGlopsMaterial"

    def copy(self, depth=0):
        target = None
        try:
            target = self.copy_as_subclass(self.new_material_method, depth=depth+1)
        except:
            print("[ KivyGlopsMaterial ] ERROR--could not finish" + \
                  " self.copy_as_subclass:")
            view_traceback()
        return target


# If inherits from Widget, has the following error only on
# Kivy 1.9.0 (on Windows 10; does not occur on 1.10.0 on linux):
#[ KivyGlop ] ERROR--__init__ could not finish super!
#<class 'TypeError'> 'dict' object is not callable:
#   File "T:\pcerruti2020\Programming\Open GL\kivyglops.py", line 111, in __init__
#     super(KivyGlop, self).__init__()  # only does class inherited FIRST (see class line above) therefore _init_glop is called below
#   File "C:\kivy\kivy34\kivy\uix\widget.py", line 261, in __init__
#     super(Widget, self).__init__(**kwargs)
#   File "kivy\_event.pyx", line 252, in kivy._event.EventDispatcher.__init__ (kivy\_event.c:4571)
#   File "kivy\_event.pyx", line 777, in kivy._event.EventDispatcher.properties (kivy\_event.c:8189)
class KivyGlop(PyGlop):  # formerly KivyGlop(Widget, PyGlop)

    #freeAngle = None
    #degreesPerSecond = None
    #freePos = None
    _mesh = None  # the (Kivy) Mesh object
    _calculated_size = None
    _t_ins = None
    _r_ins_x = None
    _r_ins_y = None
    _r_ins_z = None
    _s_ins = None
    _color_instruction = None
    _context_instruction = None

    _axes_mesh = None  # InstructionGroup for axes

    _pivot_scaled_point = None
    _pushmatrix = None
    _updatenormalmatrix = None
    _popmatrix = None
    _own_shader_enable = None
    show_next_no_mesh_warning_enable = None

    def __init__(self):
        try:
            super(KivyGlop, self).__init__()  # only does class inherited FIRST (see class line above) therefore _init_glop is called below
        except:
            print("[ KivyGlop ] ERROR--__init__ could not finish" + \
                  " super!")
            view_traceback()
            try:
                self._init_glop()
            except:
                print("[ KivyGlop ] ERROR--uh oh, " + \
                      "self._init_glop didn't work either:")
                view_traceback()
        #NOTE: super makes PyGlopsMaterial!
        self.material = KivyGlopsMaterial()
        self.material.diffuse_color = (1.0, 1.0, 1.0, 1.0)  # overlay vertex color onto this using vertex alpha
        self.material.ambient_color = (0.0, 0.0, 0.0, 1.0)
        self.material.specular_color = (1.0, 1.0, 1.0, 1.0)
        self.material.specular_coefficent = 16.0

        self._own_shader_enable = False  # if False during add_glop, gets shader of parent if _multicontext_enable, else does nothing either way
        self.show_next_no_mesh_warning_enable = True
        #self.freeAngle = 0.0
        #self.degreesPerSecond = 0.0
        #self.freePos = (10.0,100.0)

        #TODO: use a RenderContext instead?
        #self.canvas = RenderContext()
        if _multicontext_enable:
            self.canvas = RenderContext(use_parent_projection=True, use_parent_modelview=True, use_parent_frag_modelview=True)  # compute_normal_mat=False,
        else:
            self.canvas = InstructionGroup()
        self.canvas.clear()
        self._context_instruction = ContextInstruction()

        self._calculated_size = (1.0,1.0)  #finish this--or skip since only needed for getting pivot point
        #Rotate(angle=self.freeAngle, origin=(self._calculated_size[0]/2.0,self._calculated_size[1]/2.0))
        self._pivot_point = 0.0, 0.0, 0.0  #self.get_center_average_of_vertices()
        self._pivot_scaled_point = 0.0, 0.0, 0.0
        self._r_ins_x = Rotate(0, 1, 0, 0)  #angle, x, y z
        self._r_ins_x.origin = self._pivot_scaled_point
        self._r_ins_y = Rotate(0, 0, 1, 0)  #angle, x, y z
        self._r_ins_y.origin = self._pivot_scaled_point
        self._r_ins_z = Rotate(0, 0, 0, 1)  #angle, x, y z
        self._r_ins_z.origin = self._pivot_scaled_point
        self._s_ins = Scale(1.0,1.0,1.0)
        #self._s_ins.origin = self._pivot_point
        self._t_ins = Translate(0, 0, 0)
        self._color_instruction = Color(1.0, 0.0, 1.0, 1.0)  # TODO: eliminate this in favor of self.set_uniform("mat_diffuse_color", (1.0, 0.0, 1.0, 1.0))

        self.generate_axes()

    def __str__(self):
        result = str(type(self))
        if self._t_ins is not None:
            result = str(type(self)) + " named " + str(self.name) + \
                   " at " + str(self._t_ins.xyz)
        return result

    def emit_debug_to_dict(self, dest):
        #debug_dict["camera_glop"]["pos"] = str(self._t_ins.xyz)
        dest["pos"] = fixed_width(self._t_ins.xyz, 4, " ")


    def save(self, path):
        lines = []
        self.emit_yaml(lines, "")
        try:
            outs = open(path, 'w')
            for line in lines:
                outs.write(line + "\n")
            outs.close()
        except:
            print("[ KivyGlop ] ERROR--could not finish save to '" + \
                  path + "':")
            view_traceback()

    #load yaml-formatted glop file
    def load(self, source_path, original_path=None):
        specified_path = source_path
        if self.vertices is not None:
            print("[ KivyGlop ] WARNING: vertices are already present during load, overwriting")
        if specified_path is not None:
            if original_path is None:
                original_path = source_path
            if not os.path.isfile(source_path):
                source_path = resource_find(source_path)
            if os.path.isfile(source_path):
                ins = open(source_path)
                line = True
                line_number = 1
                scopes = [ScopeInfo()]
                scopes[0].indent = ""
                scopes[0].name = ""
                scopes[0].line_number = -1
                nyi_names = {}
                while line:
                    line = ins.readline()
                    if line:
                        line_strip = line.strip()
                        indent = find_any_not(line, " \t")
                        depth = int(len(indent)/2)  # assumes "  " yaml indent
                        while len(scopes)<=depth:
                            scopes.append(ScopeInfo())
                        if line_strip[:1] != "#":
                            op_i = line_strip.find(":")
                            if line_strip[-1:]==":":
                                scopes[depth].name = line_strip[:-1].strip()
                                scopes[depth].indent = indent
                                scopes[depth].line_number = line_number
                            array_i = line_strip.find("-")
                            if line_strip[0:1]=="-":
                                if depth>0:
                                    val = get_literal_value_from_yaml(line_strip[2:].strip())
                                    if scopes[depth-1].name=="vertices":
                                        self.vertices.append(float(val))
                                    elif scopes[depth-1].name=="indices":
                                        self.indices.append(int(val))
                                    else:
                                        if scopes[depth-1].name not in nyi_names:
                                            print(specified_path + "(" + str(line_number) + ",0): (INPUT ERROR) item for unknown array " + scopes[depth-1].name + " not implemented (this is the last time this message will be shown for " + scopes[depth-1].name + ")")
                                            nyi_names[scopes[depth-1].name] = False
                                else:
                                    print(specified_path + "(" + str(line_number) + ",0): (INPUT ERROR) array in deepest scope (should be indented under an object name)")
                            else:
                                if op_i > -1:
                                    name = line_strip[:op_i]
                                    val = get_literal_value_from_yaml(line_strip[op_i+1:])
                                    if name=="get_texture_diffuse_path()":
                                        self.set_texture_diffuse(val)
                                else:
                                    print(specified_path + "(" + str(line_number) + ",0): (INPUT ERROR) input with neither colon nor starting with hyphen is not implemented")
                        prev_indent = indent
                    line_number += 1
                ins.close()
            else:
                print("[ KivyGlop ] ERROR in load: missing '" + specified_path + "")
            #TODO: if cached, change source_path for each object to that in stats.yml in cache folder
        else:
            print("[ KivyGlop ] ERROR in load: source_path was None")

    def emit_yaml(self, lines, min_tab_string):
        super(KivyGlop, self).emit_yaml(lines, min_tab_string)
        lines.append(min_tab_string + "translate_x: " + get_yaml_from_literal_value(self._t_ins.x))
        lines.append(min_tab_string + "translate_y: " + get_yaml_from_literal_value(self._t_ins.y))
        lines.append(min_tab_string + "translate_z: " + get_yaml_from_literal_value(self._t_ins.z))

    def set_coord(self, index, value):
        if index == 0:
            self._t_ins.x = value
        elif index == 1:
            self._t_ins.y = value
        elif index == 2:
            self._t_ins.z = value
        else:
            print("[ KivyGlop ] ERROR in set_coord: bad index " + \
                  str(index))

    def get_coord(self, index):
        if index == 0:
            return self._t_ins.x
        elif index == 1:
            return self._t_ins.y
        elif index == 2:
            return self._t_ins.z
        else:
            print("[ KivyGlop ] ERROR in get_coord: bad index " + \
                  str(index))
        return None

    def new_vertex(self, set_coords, set_color):
        # NOTE: assumes vertex format is ok (should be checked by generate_axes)
        # assumes normal should be point relative to 0,0,0
        vertex_components = [0.0]*self.vertex_depth
        for i in range(0, 3):
            vertex_components[self._POSITION_OFFSET+i] = set_coords[i]

        # Without the 4th index, matrix math cannot work and geometry
        # cannot be translated (!):
        if self.vertex_format[self.POSITION_INDEX][VFORMAT_VECTOR_LEN_INDEX] > 3:
            vertex_components[self._POSITION_OFFSET+3] = 1.0
        if set_color is not None:
            for i in range(0, len(set_color)):
                vertex_components[self.COLOR_OFFSET+i] = set_color[i]
            if (len(set_color)) < 4 and (self.vertex_depth > 3):
                vertex_components[self.COLOR_OFFSET+3] = 1.0
        normals = [0.0]*3;
        for i in range(0, 3):
            normals[i] = set_coords[i]
        normalize_3d_by_ref(normals)
        for i in range(0, 3):
            vertex_components[self._NORMAL_OFFSET+i] = normals[i]
        #print("  #* made new vertex " + str(vertex_components) + " (color at " + str(self.COLOR_OFFSET) + ")")
        return vertex_components

    def append_vertex(self, target_vertices, set_coords, set_color):
        offset = len(target_vertices)
        index = int(offset/self.vertex_depth)
        target_vertices.extend(self.new_vertex(set_coords, set_color))
        return index

    def generate_plane(self):
        _axes_vertices = []
        _axes_indices = []

        IS_SELF_VFORMAT_OK = True
        try:
            if self._POSITION_OFFSET<0:
                IS_SELF_VFORMAT_OK = False
                print("generate_axes couldn't find name containing 'pos' or 'position' in any vertex format element (see pyops.py PyGlop constructor)")
            if self._NORMAL_OFFSET<0:
                IS_SELF_VFORMAT_OK = False
                print("generate_axes couldn't find name containing 'normal' in any vertex format element (see pyops.py PyGlop constructor)")
            if self._TEXCOORD0_OFFSET<0:
                IS_SELF_VFORMAT_OK = False
                print("generate_axes couldn't find name containing 'texcoord' in any vertex format element (see pyops.py PyGlop constructor)")
            if self.COLOR_OFFSET<0:
                IS_SELF_VFORMAT_OK = False
                print("generate_axes couldn't find name containing 'color' in any vertex format element (see pyops.py PyGlop constructor)")
        except:
            IS_SELF_VFORMAT_OK = False
            print("[ KivyGlop ] ERROR: generate_plane couldn't find offsets")

        offset = 0
        white = (1.0, 1.0, 1.0, 1.0)
        nv = -.5  # near vector
        fv = .5  # far vector
        self.append_vertex(_axes_vertices, (nv, 0.0, nv), white)
        self.append_vertex(_axes_vertices, (nv, 0.0, fv), white)
        self.append_vertex(_axes_vertices, (fv, 0.0, fv), white)
        self.append_vertex(_axes_vertices, (fv, 0.0, nv), white)
        _axes_indices.extend([0,3,2, 2,1,0])  # counterclockwise winding
        #clockwise winding (not usual unless want to flip normal):
        #_axes_indices.extend([0,1,2, 2,3,0])

        self._mesh = Mesh(
                               vertices=_axes_vertices,
                               indices=_axes_indices,
                               fmt=self.vertex_format,
                               mode='triangles',
                               texture=None,
                              )

    def generate_axes(self):
        # NOTE: This is a full solid (3 boxes) where all axes can always
        # be seen except when another is in the way (some vertices are
        # doubled so that vertex color can be used).
        # See etc/axes-widget-diagram.png

        _axes_vertices = []
        _axes_indices = []

        IS_SELF_VFORMAT_OK = True
        try:
            if self._POSITION_OFFSET<0:
                IS_SELF_VFORMAT_OK = False
                print("[ KivyGlop ] generate_axes couldn't find name " + \
                      "containing 'pos' or 'position' in any vertex format" + \
                      " element (see pyops.py PyGlop constructor)")
            if self._NORMAL_OFFSET<0:
                IS_SELF_VFORMAT_OK = False
                print("[ KivyGlop ] generate_axes couldn't find name " + \
                      "containing 'normal' in any vertex format" + \
                      " element (see pyops.py PyGlop constructor)")
            if self._TEXCOORD0_OFFSET<0:
                IS_SELF_VFORMAT_OK = False
                print("[ KivyGlop ] generate_axes couldn't find name " + \
                      "containing 'texcoord' in any vertex format" + \
                      " element (see pyops.py PyGlop constructor)")
            if self.COLOR_OFFSET<0:
                IS_SELF_VFORMAT_OK = False
                print("[ KivyGlop ] generate_axes couldn't find name " + \
                      "containing 'color' in any vertex format" + \
                      " element (see pyops.py PyGlop constructor)")
        except:
            IS_SELF_VFORMAT_OK = False
            print("[ KivyGlop ] ERROR: generate_axes couldn't find offsets")
        offset = 0
        red = (1.0, 0.0, 0.0)
        green = (0.0, 1.0, 0.0)
        blue = (0.0, 0.0, 1.0)
        # NOTE: default opengl winding order is counter-clockwise
        # (where makes normal face you)
        cv = 0.0  # center vector
        nv = 0.1  # near vector
        fv = 1.0  # far vector
        self.append_vertex(_axes_vertices, (cv, cv, cv), green)  # 0
        self.append_vertex(_axes_vertices, (nv, cv, cv), green)  # 1
        self.append_vertex(_axes_vertices, (cv, cv, nv), green)  # 2
        self.append_vertex(_axes_vertices, (nv, cv, nv), green)  # 3
        self.append_vertex(_axes_vertices, (cv, fv, cv), green)  # 4
        self.append_vertex(_axes_vertices, (nv, fv, cv), green)  # 5
        self.append_vertex(_axes_vertices, (cv, fv, nv), green)  # 6
        self.append_vertex(_axes_vertices, (nv, fv, nv), green)  # 7

        _axes_indices.extend([0,1,3, 0,3,2, 0,2,6, 0,6,4,  # bottom & right
                              0,4,5, 0,5,1, 4,5,7, 4,7,6,  # back & top
                              1,5,7, 1,7,3, 2,3,7, 2,7,6  # left & front
                              ])

        self.append_vertex(_axes_vertices, (nv, cv, cv), red)  # 8
        self.append_vertex(_axes_vertices, (nv, cv, nv), red)  # 9
        self.append_vertex(_axes_vertices, (nv, nv, cv), red)  # 10
        self.append_vertex(_axes_vertices, (fv, nv, nv), red)  # 11
        self.append_vertex(_axes_vertices, (fv, cv, cv), red)  # 12
        self.append_vertex(_axes_vertices, (fv, nv, cv), red)  # 13
        self.append_vertex(_axes_vertices, (fv, cv, nv), red)  # 14
        self.append_vertex(_axes_vertices, (fv, nv, nv), red)  # 15

        _axes_indices.extend([8,9,11, 8,11,10, 8,10,13, 8,13,12,  # back & outside
                              8,12,14, 8,14,9,  9,14,15, 9,15,11,  # bottom & inside
                              10,11,15, 11,15,13, 12,13,15, 12,15,14  # top & front
                              ])

        self.append_vertex(_axes_vertices, (cv, cv, nv), blue)  # 16
        self.append_vertex(_axes_vertices, (nv, cv, nv), blue)  # 17
        self.append_vertex(_axes_vertices, (cv, nv, nv), blue)  # 18
        self.append_vertex(_axes_vertices, (nv, nv, nv), blue)  # 19
        self.append_vertex(_axes_vertices, (cv, cv, fv), blue)  # 20
        self.append_vertex(_axes_vertices, (nv, cv, fv), blue)  # 21
        self.append_vertex(_axes_vertices, (cv, nv, fv), blue)  # 22
        self.append_vertex(_axes_vertices, (nv, nv, fv), blue)  # 23

        _axes_indices.extend([16,18,19, 16,19,17, 16,22,18, 16,20,22,  # back & outside
                              16,17,21, 16,21,20, 17,19,20, 17,20,21,  # bottom & inside
                              19,18,22, 19,22,23, 20,21,23, 20,23,22  # top & front
                              ])

        #new_texcoord = new_tuple(self.vertex_format[self.TEXCOORD0_INDEX][VFORMAT_VECTOR_LEN_INDEX])
        if IS_SELF_VFORMAT_OK:
            self._axes_mesh = Mesh(
                                   vertices=_axes_vertices,
                                   indices=_axes_indices,
                                   fmt=self.vertex_format,
                                   mode='triangles',
                                   texture=None,
                                  )
        else:
            #error already shown
            #print("[ KivyGlop ] ERROR in generate_axes:"
            #      " bad vertex_format")
            pass
        #return _axes_vertices, _axes_indices

    #"Called by the repr() built-in function to compute the "official"
    # string representation of an object. If at all possible, this
    # should look like a valid Python expression that could be used to
    # recreate an object..."
    #   - <https://docs.python.org/3/reference/datamodel.html#customization>
    def __repr__(self):
        return "KivyGlop(name=" + str(self.name) + ", location=" + \
               str(self._t_ins.xyz) + ")"

    def copy(self, depth=0):
        target = None
        try:
            new_material_method = None
            if self.material is not None:
                new_material_method = self.material.new_material_method
            if get_verbose_enable():
                print("[ KivyGlop ] " + "  " * depth + "copy is" + \
                      " calling copy_as_subclass")
            target = self.copy_as_subclass(self.new_glop_method,
                                           new_material_method,
                                           depth=depth+1)
            target.canvas = InstructionGroup()
            target._pivot_point = self._pivot_point
            target._pivot_scaled_point = self._pivot_scaled_point
            target._r_ins_x = Rotate(self._r_ins_x.angle, 1, 0, 0)  #angle, x, y z
            target._r_ins_x.origin = self._pivot_scaled_point
            target._r_ins_y = Rotate(self._r_ins_y.angle, 0, 1, 0)  #angle, x, y z
            target._r_ins_y.origin = self._pivot_scaled_point
            target._r_ins_z = Rotate(self._r_ins_z.angle, 0, 0, 1)  #angle, x, y z
            target._r_ins_z.origin = self._pivot_scaled_point
            target._t_ins = Translate(self._t_ins.x, self._t_ins.y, self._t_ins.z)
            target._color_instruction = Color(self._color_instruction.r, self._color_instruction.g, self._color_instruction.b, self._color_instruction.a)
        except:
            print("[ KivyGlop ] ERROR--could not finish copy:")
            view_traceback()
        return target

    def get_location(self):
        return self._t_ins.xyz

    def rotate_camera_relative(self, angle, axis_index):
        #TODO: delete this method and see solutions from http://stackoverflow.com/questions/10048018/opengl-camera-rotation
        #such as set_view method of https://github.com/sgolodetz/hesperus2/blob/master/Shipwreck/MapEditor/GUI/Camera.java
        self.rotate_relative_around_point(self.camera_glop, angle, axis_index, self.camera_glop._t_ins.x, self.camera_glop._t_ins.y, self.camera_glop._t_ins.z)

    def rotate_player_relative(self, angle, axis_index):
        #TODO: delete this method and see solutions from http://stackoverflow.com/questions/10048018/opengl-camera-rotation
        #such as set_view method of https://github.com/sgolodetz/hesperus2/blob/master/Shipwreck/MapEditor/GUI/Camera.java
        self.rotate_relative_around_point(self.player_glop, angle, axis_index, self.player_glop._t_ins.x, self.player_glop._t_ins.y, self.player_glop._t_ins.z)

    def rotate_relative_around_point(self, this_glop, angle, axis_index, around_x, around_y, around_z):
        if axis_index == 0:  #x
            # += around_y * math.tan(angle)
            this_glop._r_ins_x.angle += angle
            # origin_distance = math.sqrt(around_z*around_z + around_y*around_y)
            # this_glop._t_ins.z += origin_distance * math.cos(-1*angle)
            # this_glop._t_ins.y += origin_distance * math.sin(-1*angle)
        elif axis_index == 1:  #y
            this_glop._r_ins_y.angle += angle
            # origin_distance = math.sqrt(around_x*around_x + around_z*around_z)
            # this_glop._t_ins.x += origin_distance * math.cos(-1*angle)
            # this_glop._t_ins.z += origin_distance * math.sin(-1*angle)
        else:  #z
            #this_glop._t_ins.z += around_y * math.tan(angle)
            this_glop._r_ins_z.angle += angle
            # origin_distance = math.sqrt(around_x*around_x + around_y*around_y)
            # this_glop._t_ins.x += origin_distance * math.cos(-1*angle)
            # this_glop._t_ins.y += origin_distance * math.sin(-1*angle)

    def new_glop_method(self):
        #return PyGlops.new_glop_method(self)
        return KivyGlop()

    def get_class_name(self):
        return "KivyGlop"

    def look_at(self, target_glop):
        if target_glop is not None:
            self.look_at_pos(target_glop._t_ins.xyz)
            #pitch = 0.0
            #pitch = get_angle_between_points(self._t_ins.y, self._t_ins.z, target_glop._t_ins.y, target_glop._t_ins.z)
            #self._r_ins_x.angle = pitch
            #yaw = get_angle_between_points(self._t_ins.x, self._t_ins.z, target_glop._t_ins.x, target_glop._t_ins.z)
            #self._r_ins_y.angle = yaw
            #print("look at pitch,yaw: " + str(int(math.degrees(pitch))) + "," + str(int(math.degrees(yaw))))
        else:
            global look_at_none_warning_enable
            if look_at_none_warning_enable:
                print("[ KivyGlop ] look_at got None for target_glop")
                look_at_none_warning_enable = False

    def look_at_pos(self, pos):
        if pos is not None:
            pitch = self._r_ins_x.angle
            yaw = self._r_ins_y.angle
            if len(pos) > 2:
                pitch = get_angle_between_points(self._t_ins.y, self._t_ins.z, pos[1], pos[2])
                yaw = get_angle_between_points(self._t_ins.x, self._t_ins.z, pos[0], pos[2])
            else:
                yaw = get_angle_between_points(self._t_ins.x, self._t_ins.z, pos[0], pos[1])
                if get_verbose_enable():
                    print("[ KivyGlop ] WARNING: look_at_pos got 2D coords")
            self._r_ins_x.angle = pitch
            self._r_ins_y.angle = yaw
            #print("look at pitch,yaw: " + str(int(math.degrees(pitch))) + "," + str(int(math.degrees(yaw))))
        else:
            global look_at_none_warning_enable
            if look_at_pos_none_warning_enable:
                print("[ KivyGlop ] ERROR: look_at_pos got None for pos")
                look_at_pos_none_warning_enable = False

    def copy_as_mesh_instance(self, depth=0, ref_vertices_enable=True):
        result = KivyGlop()
        result.name = self.name
        if ref_vertices_enable:
            result.vertex_format = self.vertex_format
            result.on_vertex_format_change()
            result.vertices = self.vertices
            result.indices = self.indices
        else:
            result.vertex_format = copy.deepcopy(self.vertex_format)
            result.on_vertex_format_change()
        result.hit_radius = self.hit_radius
        result.hitbox = self.hitbox
        context = result.get_context()
        result._t_ins.x = self._t_ins.x
        result._t_ins.y = self._t_ins.y
        result._t_ins.z = self._t_ins.z
        result._r_ins_x.angle = self._r_ins_x.angle
        result._r_ins_y.angle = self._r_ins_y.angle
        result._r_ins_z.angle = self._r_ins_z.angle
        #result._s_ins.x = self._s_ins.x
        #result._s_ins.y = self._s_ins.y
        #result._s_ins.z = self._s_ins.z
        #result._color_instruction.r = self._color_instruction.r
        #result._color_instruction.g = self._color_instruction.g
        #result._color_instruction.b = self._color_instruction.b
        result._pushmatrix = PushMatrix()
        result._updatenormalmatrix = UpdateNormalMatrix()
        result._popmatrix = PopMatrix()

        context.add(result._pushmatrix)
        context.add(result._t_ins)
        context.add(result._r_ins_x)
        context.add(result._r_ins_y)
        context.add(result._r_ins_z)
        context.add(result._s_ins)
        context.add(result._updatenormalmatrix)
        #context.add(this_glop._color_instruction)  #TODO: asdf add as uniform
        if self._mesh is not None:
            context.add(self._mesh)
        else:
            print("[ KivyGlop ] " + "  "*depth + "WARNING in " + \
                  "copy_as_mesh_instance: meshless glop '" + \
                  str(self.name) + "'")
        context.add(result._popmatrix)

        return result


    def get_hit_range_present(self):
        return (self.hitbox is not None) and \
               (self.hit_radius is not None)

    def calculate_hit_range(self):
        # TODO: re-implement super method, changing hitbox taking
        # rotation & scale into account
        # NOTE: index is set by add_glop so None if done earlier:
        glop_msg = "new glop"
        if self.glop_index is not None:
            glop_msg = str(self.glop_index)
        if self.name is not None:
            glop_msg += " '" + self.name + "'"
        if get_verbose_enable():
            print("[ KivyGlop ] calculate_hit_range (hitbox) for " + glop_msg + "...")
        if self.vertices is not None:
            vertex_count = int(len(self.vertices)/self.vertex_depth)
            if vertex_count>0:
                v_offset = 0
                self.hit_radius = 0.0
                for i in range(0,3):
                    #intentionally set to rediculously far in opposite direction:
                    self.hitbox.minimums[i] = sys.maxsize
                    self.hitbox.maximums[i] = -sys.maxsize
                for v_number in range(0, vertex_count):
                    for i in range(0,3):
                        if self.vertices[v_offset+self._POSITION_OFFSET+i] < self.hitbox.minimums[i]:
                            self.hitbox.minimums[i] = self.vertices[v_offset+self._POSITION_OFFSET+i]
                        if self.vertices[v_offset+self._POSITION_OFFSET+i] > self.hitbox.maximums[i]:
                            self.hitbox.maximums[i] = self.vertices[v_offset+self._POSITION_OFFSET+i]
                    this_vertex_relative_distance = get_distance_vec3(self.vertices[v_offset+self._POSITION_OFFSET:v_offset+self._POSITION_OFFSET+3], self._pivot_point)
                    if this_vertex_relative_distance > self.hit_radius:
                        self.hit_radius = this_vertex_relative_distance
                    v_offset += self.vertex_depth
                phi_eye_height = 86.5 * self.hitbox.maximums[1]
                if self.eye_height > phi_eye_height:
                    print("[ KivyGlop ] WARNING in calculate_hit_range:" + \
                          " eye_height " + str(self.eye_height) + \
                          " is beyond phi_eye_height" + \
                          str(phi_eye_height) + \
                          " so is being set to that value")
                    self.eye_height = self.hitbox.maximums[1]
                print("    done calculate_hit_range")
            else:
                self.hitbox = None  # avoid 0-size hitbot which would prevent bumps
                if self.hit_radius is None:
                    self.hit_radius = .4444  # flag value
                print("    skipped (0 vertices).")
        else:
            self.hitbox = None  # avoid 0-size hitbot which would prevent bumps
            if self.hit_radius is None:
                self.hit_radius = .4444  # flag value
            print("[ KivyGlop ] hitbox skipped since vertices None.")

    def rotate_x_relative(self, angle):
        self._r_ins_x.angle += angle

    def rotate_y_relative(self, angle):
        self._r_ins_y.angle += angle

    def rotate_z_relative(self, angle):
        self._r_ins_z.angle += angle

    def move_x_relative(self, distance):
        self._t_ins.x += distance

    def move_y_relative(self, distance):
        self._t_ins.y += distance

    def move_z_relative(self, distance):
        self._t_ins.z += distance

    def transform_pivot_to_geometry(self):
        previous_point = self._pivot_point
        super(KivyGlop, self).transform_pivot_to_geometry()
        #self._change_instructions()
        #self._on_change_pivot(previous_point)  #commenting this assumes this subclass' version of _on_change_pivot is already run by super

    def _on_change_pivot(self, previous_point=(0.0,0.0,0.0)):
        super(KivyGlop, self)._on_change_pivot(previous_point=previous_point)
        print("[ KivyGlop ] (verbose message) _on_change_pivot from " + str(previous_point))
        self._on_change_s_ins()  # does calculate_hit_range

    def get_scale(self):
        return (self._s_ins.x + self._s_ins.y + self._s_ins.z) / 3.0

    def set_scale(self, overall_scale):
        self._s_ins.x = overall_scale
        self._s_ins.y = overall_scale
        self._s_ins.z = overall_scale
        self._on_change_s_ins()  # does calculate_hit_range

    def _on_change_s_ins(self):
        if self._pivot_point is not None:
            self._pivot_scaled_point = self._pivot_point[0] * self._s_ins.x + self._t_ins.x, self._pivot_point[1] * self._s_ins.y + self._t_ins.y, self._pivot_point[2] * self._s_ins.z + self._t_ins.z
#         else:
#             self._pivot_point = 0,0,0
#             self._pivot_scaled_point = 0,0,0
        #super(KivyGlop, self)._on_change_scale()
        #if self._pivot_point is not None:
        self._r_ins_x.origin = self._pivot_scaled_point
        self._r_ins_y.origin = self._pivot_scaled_point
        self._r_ins_z.origin = self._pivot_scaled_point
        #self._t_ins.x = self.freePos[0]-self._rectangle_instruction.size[0]*self._s_ins.x/2
        #self._t_ins.y = self.freePos[1]-self._rectangle_instruction.size[1]*self._s_ins.y/2
        #self._rotate_instruction.origin = self._rectangle_instruction.size[0]*self._s_ins.x/2.0, self._rectangle_instruction.size[1]*self._s_ins.x/2.0
        #self._rotate_instruction.angle = self.freeAngle
        this_name = ""
        if self.name is not None:
            this_name = self.name
        #print()
        #print("_on_change_s_ins for object named '"+this_name+"'")
        #print ("_pivot_point:"+str(self._pivot_point))
        #print ("_pivot_scaled_point:"+str(self._pivot_scaled_point))
        #if self.hitbox is not None:
            #only should be recalculated if already
            # (already bumper or bumpable list)
        if self.get_has_hit_range():
            self.calculate_hit_range()

    def apply_translate(self):
        vertex_count = int(len(self.vertices)/self.vertex_depth)
        v_offset = 0
        for v_number in range(0, vertex_count):
            self.vertices[v_offset+self._POSITION_OFFSET+0] -= self._t_ins.x
            self.vertices[v_offset+self._POSITION_OFFSET+1] -= self._t_ins.y
            self.vertices[v_offset+self._POSITION_OFFSET+2] -= self._t_ins.z
            self._pivot_point = (self._pivot_point[0] - self._t_ins.x,
                                 self._pivot_point[1] - self._t_ins.y,
                                 self._pivot_point[2] - self._t_ins.z)
            self._t_ins.x = 0.0
            self._t_ins.y = 0.0
            self._t_ins.z = 0.0
            v_offset += self.vertex_depth
        self.apply_pivot()
        if self.get_has_hit_range():
            self.calculate_hit_range()

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
                print("[ KivyGlop ] Loaded texture '" + str(self.last_loaded_path) + "'")
            except:
                print("[ KivyGlop ] Could not finish loading texture: " + str(self.last_loaded_path))
                view_traceback()
        else:
            if get_verbose_enable():
                Logger.debug("[ KivyGlop ] Warning: no texture specified for glop named '" + str(self.name) + "'")
                this_material_name = ""
                if self.material is not None:
                    if self.material.name is not None:
                        this_material_name = self.material.name
                        Logger.debug("[ KivyGlop ] (material named '" + this_material_name + "')")
                    else:
                        Logger.debug("[ KivyGlop ] (material with no name)")
                else:
                    Logger.debug("[ KivyGlop ] (no material)")
        if self._mesh is not None and this_texture_image is not None:
            self._mesh.texture = this_texture_image.texture
            context = self.get_context()
            self.set_uniform("texture0_enable", True)
        return this_texture_image

    def _generate_kivy_mesh(self):
        participle = "checking for texture"
        if self._mesh is not None:
            print("[ KivyGlop ] WARNING in generate_kivy_mesh: self._mesh is not None, overriding")
        self._mesh = None
        this_texture_image = self.set_texture_diffuse(self.get_texture_diffuse_path())
        participle = "assembling kivy Mesh"
        this_texture = None
        if self.vertices is not None:
            if len(self.vertices) > 0:
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
                if get_verbose_enable():
                    print("[ KivyGlop ] " + str(len(self.vertices)) + " vert(s)")
            else:
                print("[ KivyGlop ] WARNING: 0 vertices in glop")
                if self.name is not None:
                    print("[ KivyGlop ]   named " + self.name)
        else:
            print("[ KivyGlop ] WARNING: vertices is None in glop " + str(self.name))

    def set_uniform(self, name, val):
        # NOTE: this is the LOCAL object canvas, which may be
        # either a RenderContext (not full Canvas) or InstructionGroup
        if _multicontext_enable:
            self.canvas[name] = val
        else:
            #can't do it to InstructionGroup so don't try
            pass

    def get_uniform(self, name):
        if _multicontext_enable:
            return self.canvas[name]
        else:
            #can't do it so don't try
            return None

    def prepare_canvas(self, use_meshes=None, axes_index=-1):
        if self._mesh is None:
            #verts, indices = self.generate_kivy_mesh()
            self._generate_kivy_mesh()
            #_contexts = [ self._axes_mesh ]
            #print("[ KivyGlop ] WARNING: glop had no mesh, so was" + \
            #      " generated when added to render context. Please" + \
            #      "ensure it is a KivyGlop and not a PyGlop " + \
            #      "(however, vertex indices misread could also " + \
            #      "lead to missing Mesh object).")
        if use_meshes is None:
            use_meshes = [self._mesh]

        m_i = 0
        context = self.get_context()
        context.clear()

        #self.generate_axes()
        #self.generate_plane()
        self.set_uniform("texture0_enable", False)
        for i in range(len(use_meshes)):
            use_mesh = use_meshes[i]
            #self._axes_mesh.
            #self._s_ins = Scale(0.6)
            self._pushmatrix = PushMatrix()
            self._updatenormalmatrix = UpdateNormalMatrix()
            self._popmatrix = PopMatrix()

            context.add(self._pushmatrix)
            context.add(self._t_ins)
            context.add(self._r_ins_x)
            context.add(self._r_ins_y)
            context.add(self._r_ins_z)
            context.add(self._s_ins)
            # NOTE: this can cause an untraceable segfault if bad scale
            # such as 0.0, so code below hopefully corrects all issues
            if i == axes_index:
                this_s_ins = None
                if self.hitbox is not None and \
                        self.hitbox.maximums is not None:
                    radii = [.1, .1, .1]
                    if len(self.hitbox.maximums) < 3:
                        print("[ KivyGlops ] ERROR in " + \
                              "prepare_canvas: len(maximums) is " + \
                              "less than 3 dimensions, filled in .1")
                    for m_i in range(len(self.hitbox.maximums)):
                        try:
                            radii[m_i] = self.hitbox.maximums[m_i] - \
                                         self.hitbox.minimums[m_i]
                        except:
                            print(
                                "[ KivyGlops ] ERROR in " + \
                                "prepare_canvas: missing minimums, " + \
                                "setting radii[" + str(m_i) + "] to .1")
                            radii[m_i] = .1
                        if radii[m_i] <= kEpsilon:
                            print("[ KivyGlops ] WARNING in " + \
                                  "prepare_canvas: " + \
                                  str(self.name) + \
                                  "'s hitbox radii[" + \
                                  str(m_i) + "] is " + \
                                  str(radii[m_i]) + \
                                  " so setting to .1")
                            radii[m_i] = .1
                    this_s_ins = Scale(radii[0], radii[1], radii[2])
                elif self.hit_radius > .1:
                    this_s_ins = Scale(self.hit_radius, self.hit_radius, self.hit_radius)
                else:
                    this_s_ins = Scale(.1, .1, .1)
                context.add(this_s_ins)
            else:
                context.add(self._s_ins)
            context.add(self._updatenormalmatrix)
            context.add(self._context_instruction)
            #context.add(self._color_instruction)  #TODO: asdf add as uniform instead
            #print("_color_instruction.r,.g,.b,.a: " + str( [self._color_instruction.r, self._color_instruction.g, self._color_instruction.b, self._color_instruction.a] ))
            #print("u_color: " + str(self.material.diffuse_color))
            #if self._axes_mesh is not None:
                #context.add(self._axes_mesh)  # debug only
                #self._mesh = self._axes_mesh  # debug only
            #    pass
            #else:
            #    print("[ KivyGlop ] no _axes_mesh.")  # debug only
            #    pass

            if use_mesh is not None:
                context.add(use_mesh)  # commented for debug only
                if get_verbose_enable():
                    print("[ KivyGlop ] (verbose message) Added mesh to render context.")
                if use_mesh.texture is not None:
                    self.set_uniform("texture0_enable", True)
                else:
                    self.set_uniform("texture0_enable", False)
                if get_verbose_enable():
                    print("[ KivyGlop ] (verbose message) texture0_enable: " + str(self.get_uniform("texture0_enable")))
            else:
                if get_verbose_enable():
                    print("[ KivyGlop ] (verbose message) NOT adding mesh None at " + str(m_i) + ".")
            context.add(self._popmatrix)

            #context.add(PushMatrix())
            #context.add(self._t_ins)
            #context.add(self._r_ins_x)
            #context.add(self._r_ins_y)
            #context.add(self._r_ins_z)
            #context.add(self._s_ins)
            #context.add(self._updatenormalmatrix)
            #context.add(self._axes_mesh)
            #context.add(PopMatrix())
            m_i += 1

    def get_context(self):
        return self.canvas


class KivyGlops(PyGlops):

    #region moved from ui
    projection_near = None
    look_point = None
    focal_distance = None  # exists so look_point has more freedom
    selected_glop = None
    selected_glop_index = None
    mode = None
    env_rectangle = None
    controllers = None
    player1_controller = None
    _previous_world_light_dir = None
    _previous_camera_rotate_y_angle = None
    _world_cube = None
    world_boundary_min = None
    world_boundary_max = None
    _sounds = None
    #endregion moved from ui
    #camera_glop = None  # inherited from PyGlops (so are many other member variables)

    def __init__(self, new_ui):
        self._load_glops_enable = False
        self._loading_glops_enable = False
        self._loaded_glops_enable = False
        self.ui = new_ui
        if self.ui is None:
            print("[ KivyGlops ] FATAL ERROR in __init__: KivyGlops cannot init without a ui")
            exit(1)

        #TODO? or remove if is ok without it: Clock.schedule_once(
        #    self._update,
        #    self.update_interval)
        self.ui.scene = self
        try:
            super(KivyGlops, self).__init__(self.new_glop_method)
        except:
            print("[ KivyGlops ] FATAL ERROR--__init__ could not" + \
                  " finish super:")
            view_traceback()
            sys.exit(1)
        try:
            self.controllers = list()
            #region moved from ui
            self.world_boundary_min = [None,None,None]
            self.world_boundary_max = [None,None,None]
            self.mode = MODE_EDIT
            self.player1_controller = PyRealTimeController()
            self.controllers.append(self.player1_controller)
            self.focal_distance = 2.0
            self.projection_near = 0.1
            self._sounds = {}

            self.player_glop = KivyGlop()
            self.player_glop.eye_height = 1.7  # 1.7 since 5'10" person is ~1.77m, and eye down a bit
            self.player_glop.hit_radius = .2  # default is 0.1524  # .5' equals .1524m
            self.player_glop.reach_radius = 2.5  # default is 0.381 # 2.5' .381m

            #x,y,z where y is up:
            self.player_glop._t_ins.x = 0
            self.player_glop._t_ins.y = 0
            self.player_glop._t_ins.z = 25  # + toward view

            self.player_glop._r_ins_x.angle = 0.0
            self.player_glop._r_ins_y.angle = math.radians(-90.0)  # [math.radians(-90.0), 0.0, 1.0, 0.0]
            self.player_glop._r_ins_z.angle = 0.0
            #region moved from ui

            self.set_camera_mode(self.CAMERA_FIRST_PERSON())
            #self.player_glop = self.camera_glop  # TODO: separate into two objects and make camera follow player
            self.player_glop.bump_enable = True
            self.camera_glop.glop_index = len(self.glops)
            self.glops.append(self.camera_glop)
            self.player_glop.name = "Player 1"
            #self._fly_enables[self.player_glop.name] = True
            self.player_glop.glop_index = len(self.glops)
            self.glops.append(self.player_glop)
            self._player_glop_index = len(self.glops)-1
            # call after_selected_item to keep label consistent:
            self.after_selected_item(
                {"glop_index":self._player_glop_index})
            self.set_as_actor_at(self._player_glop_index, None)
            if self.glops[self._player_glop_index] is not self.player_glop:
                #then address multithreading paranoia
                self._player_glop_index = None
                for try_i in range(len(self.glops)):
                    if self.glops[try_i] is self.player_glop:
                        self._player_glop_index = try_i
                        break
                if self._player_glop_index is not None:
                    print("WARNING: glop array changed during init, so redetected self._player_glop_index.")
                else:
                    print("WARNING: glop array changed during init, and self._player_glop_index could not be detected.")
            #self._bumper_indices.append(self._player_glop_index)

            #TODO: why was this code here? it's not good. these are set during update instead now
            #this_actor_dict = dict()
            #this_actor_dict["land_units_per_second"] = 12.0
            #this_actor_dict["land_degrees_per_second"] = 90.0
            #self.set_as_actor_at(self._player_glop_index, this_actor_dict)

            #NOTE: set_as_actor_at sets hitbox to None if has no vertices
        except:
            print("[ KivyGlops ] ERROR--__init__ could not finish:")
            view_traceback()

    def new_glop_method(self):
        #return PyGlops.new_glop_method(self)
        return KivyGlop()

    def get_class_name(self):
        return "KivyGlops"

    def on_load_glops(self):
        print("WARNING: app's subclass of KivyGlops should implement on_load_glops (and usually on_update_glops, which will be called before each frame is drawn)")

    def create_material(self):
        return KivyGlopsMaterial()

    def hide_glop(self, this_glop):
        self.ui._contexts.remove(this_glop.get_context())
        this_glop.visible_enable = False

    def show_glop(self, this_glop_index):
        self.ui._contexts.add(self.glops[this_glop_index].get_context())
        self.glops[this_glop_index].visible_enable = True

    def use_walkmesh_at(self, index, hide=True):
        if self.glops[index] not in self._walkmeshes:
            self._walkmeshes.append(self.glops[index])
            if self.settings.get("world_gravity_enable") is None:
                self.settings["world_gravity_enable"] = True
                print("[ KivyGlops ] use_walkmesh_at set " + \
                      "world_gravity_enable to True " + \
                      "in settings dict since was None")
            print("[ KivyGlops ] Applying walkmesh translate " + \
                  str(self.glops[index]._t_ins.xyz))
            self.glops[index].apply_translate()
            print("[ KivyGlops ]   pivot:" + \
                  str(self.glops[index]._pivot_point))
            if hide:
                self.hide_glop(self.glops[index])

    def use_walkmesh(self, name, hide=True):
        result = False
        #for this_glop in self.glops:
        for index in range(0, len(self.glops)):
            if self.glops[index].name == name:
                result = True
                self.use_walkmesh_at(index, hide=hide)
                break
        return result

    def set_hud_background(self, path):
        self.ui.set_hud_background(path)

    def set_background_cylmap(self, path):
        #self.load_obj("env_sphere.obj")
        #self.load_obj("maps/gi/etc/sky_sphere.obj")
        #env_indices = self.get_indices_by_source_path("env_sphere.obj")
        #for i in range(0,len(env_indices)):
        #    index = env_indices[i]
        #    print("Preparing sky object "+str(index))
        #    self.ui.glops[index].set_texture_diffuse(path)
        if self.env_rectangle is not None:
            self.ui.canvas.before.remove(self.env_rectangle)
            self.env_rectangle = None
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
                self.ui.canvas.before.add(self.env_rectangle)
            else:
                print("ERROR in set_background_cylmap: " + \
                      original_path + " not found in search path")
        else:
            print("ERROR in set_background_cylmap: path is None")

    def preload_sound(self, path):
        if path is not None:
            if path not in self._sounds:
                self._sounds[path] = {}
                print("loading " + path)
                self._sounds[path]["loader"] = SoundLoader.load(path)

    def explode_glop_at(self, index, weapon_dict=None):
        self.on_explode_glop( \
            self.glops[index]._t_ins.xyz, \
            self.glops[index].hit_radius, \
            index,
            weapon_dict)
        self.kill_glop_at(index, weapon_dict)

    def on_explode_glop(self, pos, radius, attacked_index, weapon_dict):
        print("[ KivyGlops ] NOTICE: there is no default " + \
              "on_explode_glop in this version, so nothing will " +
              "be shown")

    def play_sound(self, path, loop=False):
        if path is not None:
            self.preload_sound(path)
            if self._sounds[path]:
                if get_verbose_enable():
                    print("playing " + path)
                self._sounds[path]["loader"].play()
            else:
                print("[ KivyGlops ] ERROR: Failed to play " + path)
        else:
            print("[ KivyGlops ] ERROR in play_sound: path is None")

    def play_music(self, path, loop=True):
        self.play_sound(path, loop=loop)

    def load_obj(self, source_path, swapyz_enable=False, centered=False, pivot_to_geometry_enable=True):
        self.ui.suspend_debug_label_update(True)
        load_obj_start_s = best_timer()
        results = None
        cache_path = None
        cached_count = 0
        cache_path = None
        original_path = source_path
        if swapyz_enable:
            print("[ KivyGlops ] (load_obj) swapyz_enable is NOT YET IMPLEMENTED")
        if source_path is not None:
            source_path = resource_find(source_path)
            if source_path is not None:
                if os.path.isfile(source_path):
                    #cache_name = hashlib.sha224(source_path).hexdigest()
                    #path_hash = hashlib.new('ripemd160')
                    #cache_name = path_hash.hexdigest()
                    #cache_name = hashlib.ripemd160(source_path).hexdigest()
                    # 20 like SHA-1, but blake2b is more secure:
                    try:
                        cache_name = hashlib.blake2b(digest_size=20).hexdigest()
                    except:
                        cache_name = hashlib.sha1().hexdigest()
                    # NOTE: at this point, len(cache_name) should be 40
                    # (since is a hexdigest of a 20-value hash)
                    caches_path = "cache"
                    if not os.path.isdir(caches_path):
                        os.mkdir(caches_path)
                    glop_caches_path = os.path.join(caches_path, "glop")
                    if not os.path.isdir(glop_caches_path):
                        os.mkdir(glop_caches_path)
                    cache_path = os.path.join(glop_caches_path, cache_name)
                    cache_path_enable = False
                    if not os.path.isdir(cache_path):
                        os.mkdir(cache_path)
                        cache_path_enable = True
                    #super(KivyGlops, self).load_obj(source_path)
                    new_glops = self.get_glop_list_from_obj(source_path, self.new_glop_method)  #asdf
                    if new_glops is None:
                        print("[ KivyGlops ] (load_obj) FAILED TO LOAD '" + str(source_path) + "'")
                    elif len(new_glops)<1:
                        print("[ KivyGlops ] (load_obj) NO VALID OBJECTS FOUND in '" + str(source_path) + "'")
                    else:
                        if self.glops is None:
                            self.glops = list()

                        #for index in range(0,len(self.glops)):
                        favorite_pivot_point = None
                        for index in range(0,len(new_glops)):
                            new_glops[index].original_path = original_path
                            #this_glop = new_glops[index]
                            #this_glop = KivyGlop(pyglop=self.glops[index])
                            #if len(self.glops<=index):
                                #self.glops.append(this_glop)
                            #else:
                                #self.glops[index]=this_glop
                            #print("")
                            if favorite_pivot_point is None:
                                favorite_pivot_point = new_glops[index]._pivot_point
                        if favorite_pivot_point is None:
                            favorite_pivot_point = (0.0, 0.0, 0.0)
                        folder_path = cache_path
                        for sub_name in os.listdir(folder_path):
                            sub_path = os.path.join(folder_path, sub_name)
                            if sub_name[:1] != ".":
                                if len(sub_name) == 40 and \
                                   sub_name[:-5] == ".glop":
                                    # Remove uuid hex digest-named files
                                    os.remove(sub_path)
                        for index in range(0,len(new_glops)):
                            if pivot_to_geometry_enable:
                                #apply pivot point (so that glop's _t_ins is actually the center)
                                some_name = ""
                                if new_glops[index].name is not None:
                                    some_name = new_glops[index].name
                                self.ui.set_debug_label("processing pivot for mesh '" + some_name + "'...")
                                print("[ KivyGlops ] (load_obj) applying pivot point for " + some_name + "...")
                                prev_pivot = new_glops[index]._pivot_point[0], new_glops[index]._pivot_point[1], new_glops[index]._pivot_point[2]
                                new_glops[index].apply_pivot()
                                #print("    moving from "+str( (new_glops[index]._t_ins.x, new_glops[index]._t_ins.y, new_glops[index]._t_ins.z) ))
                                new_glops[index]._t_ins.x = prev_pivot[0]
                                new_glops[index]._t_ins.y = prev_pivot[1]
                                new_glops[index]._t_ins.z = prev_pivot[2]
                            new_glops[index].prepare_canvas()  # does generate_kivy_mesh() if needed
                            self.ui.add_glop(new_glops[index])
                            if results is None:
                                results = list()
                            results.append(len(self.glops)-1)
                            if (new_glops[index].name is None) and \
                               (cache_path_enable):
                                # ok since deleted uuid-named files already:
                                new_glops[index].name = str(uuid.uuid4())
                            if new_glops[index].name is not None:
                                new_glops[index].save(os.path.join(cache_path, good_path_name(new_glops[index].name) + ".glop"))
                        if centered:
                            #TODO: apply pivot point instead (change vertices as if pivot point were 0,0,0) to ensure translate 0 is world 0; instead of:
                            #center it (use only one pivot point, so all objects in obj file remain aligned with each other):

                            for index in range(0,len(new_glops)):
                                if index==0:
                                    print("  centering from "+str(favorite_pivot_point))
                                    print("  (this is the last centering message that will be shown)")
                                    print("")
                                new_glops[index].move_x_relative(-1.0*favorite_pivot_point[0])
                                new_glops[index].move_y_relative(-1.0*favorite_pivot_point[1])
                                new_glops[index].move_z_relative(-1.0*favorite_pivot_point[2])
                                #TODO: new_glops[index].apply_translate()
                                #TODO: new_glops[index].reset_translate()

                        #print("")
                else:
                    print("[ KivyGlops ] (load_obj) missing '" + \
                          source_path + "'")
            else:
                print("[ KivyGlops ] (load_obj) missing '" + \
                      original_path + "'")
        else:
            print("[ KivyGlops ] (load_obj) ERROR: source_path is None" + \
                  " for load_obj")
        load_obj_s = best_timer() - load_obj_start_s
        if results is not None:
            print("[ KivyGlops ] (load_obj) Loaded '" + original_path + \
                  "' in " + str(load_obj_s) + " seconds.")
            if cache_path is not None:
                stats_name = "stats.yml"
                stats_path = os.path.join(cache_path, stats_name)
                try:
                    outs = open(stats_path, 'w')
                    outs.write("original_path: " + original_path + "\n")
                    outs.write("path: " + source_path + "\n")
                    outs.close()
                    if cached_count > 0:
                        stats_name = "stats-cached.yml"
                        stats_path = os.path.join(cache_path, stats_name)
                        if not os.path.isfile(stats_path):
                            outs = open(stats_path, 'w')
                            outs.write("cached_load_time_s: " + \
                                       str(load_obj_s) + "\n")
                            outs.close()
                    else:
                        stats_name = "stats-notcached.yml"
                        stats_path = os.path.join(cache_path, stats_name)
                        if not os.path.isfile(stats_path):
                            outs = open(stats_path, 'w')
                            outs.write("not_cached_load_time_s: " + \
                                       str(load_obj_s) + "\n")
                            outs.close()
                except:
                    print("[ KivyGlops ] ERROR in load_obj--could not" + \
                          " finish saving stats to '" + stats_path + "'")
        else:
            print("[ KivyGlops ] (load_obj) WARNING: Loaded 0 objects.")
        self.ui.suspend_debug_label_update(False)
        return results

    def get_pressed(self, key_name):
        #WARNING: this is for backward compatibility only
        if key_name is not None:
            try:
                return self.player1_controller.get_pressed(self.ui.get_keycode(key_name))
            except:
                # no keyboard attached
                pass
        # else don't complain, get_keycode returns None if no keybaord
        # and that is the method to find the keycode
        return False

    #def constrain_glop_to_walkmesh(self, this_glop, height_only_enable=False):
    # these_radii[0] is used to push against side if
    # height_only_enable=False (to push x,z away from wall)
    # these_radii[1] is used to push against floor (new y will be
    # increased by this amount)
    def get_walk_info(self, this_pos, these_radii, height_only_enable=False):
        walk_info = {}
        walk_info["pos"] = [ this_pos[0], this_pos[1], this_pos[2] ]
        walk_info["change_enable"] = False
        if len(self._walkmeshes)>0:
            walkmesh_result = self.get_container_walkmesh_and_poly_index_xz(this_pos)
            corrected_pos = None
            if walkmesh_result is None:
                #if self.prev_inbounds_camera_translate is not None:
                #    #this would cause player to stick to wall pushed:
                #    walk_info["pos"] = [ self.prev_inbounds_camera_translate[0]
                #                       self.prev_inbounds_camera_translate[1]
                #                       self.prev_inbounds_camera_translate[2] ]
                #else:
                corrected_pos = self.get_nearest_walkmesh_vec3_using_xz(this_pos)
                if corrected_pos is not None:
                    # Push away from wall (edge of walkmesh), but allow
                    # sliding along:
                    pushed_angle = get_angle_between_two_vec3_xz(this_pos, corrected_pos)
                    corrected_pos = get_pushed_vec3_xz_rad(corrected_pos, these_radii[0], pushed_angle)
                else:
                    global nearest_not_found_warning_enable
                    if nearest_not_found_warning_enable:
                        nearest_not_found_warning_enable = False
                        print("[ KivyGlops ] ERROR in get_walk_info: could not find point to bring player in bounds.")
                walk_info["walkmesh_found_by"] = "nearest"
            else:
                # In bounds, so only change y
                w_glop = self._walkmeshes[walkmesh_result["walkmesh_index"]]
                X_i = w_glop._POSITION_OFFSET + 0
                Y_i = w_glop._POSITION_OFFSET + 1
                Z_i = w_glop._POSITION_OFFSET + 2
                ground_tri = list()
                #TODO: use vertext format of w_glop for ground_tri instead of assuming first 3 entries in vertext are 3D pos
                ground_tri.append( (w_glop.vertices[w_glop.indices[walkmesh_result["polygon_offset"]]*w_glop.vertex_depth+X_i], w_glop.vertices[w_glop.indices[walkmesh_result["polygon_offset"]]*w_glop.vertex_depth+Y_i], w_glop.vertices[w_glop.indices[walkmesh_result["polygon_offset"]]*w_glop.vertex_depth+Z_i]) )
                ground_tri.append( (w_glop.vertices[w_glop.indices[walkmesh_result["polygon_offset"]+1]*w_glop.vertex_depth+X_i], w_glop.vertices[w_glop.indices[walkmesh_result["polygon_offset"]+1]*w_glop.vertex_depth+Y_i], w_glop.vertices[w_glop.indices[walkmesh_result["polygon_offset"]+1]*w_glop.vertex_depth+Z_i]) )
                ground_tri.append( (w_glop.vertices[w_glop.indices[walkmesh_result["polygon_offset"]+2]*w_glop.vertex_depth+X_i], w_glop.vertices[w_glop.indices[walkmesh_result["polygon_offset"]+2]*w_glop.vertex_depth+Y_i], w_glop.vertices[w_glop.indices[walkmesh_result["polygon_offset"]+2]*w_glop.vertex_depth+Z_i]) )
                ground_y = get_y_from_xz(ground_tri[0], ground_tri[1], ground_tri[2], this_pos[0], this_pos[2])
                corrected_pos = [this_pos[0], ground_y + these_radii[1], this_pos[2]]
                if self._world_min_y is None or ground_y < self._world_min_y:
                    self._world_min_y = ground_y
                #if self.prev_inbounds_camera_translate is None or this_pos[1] != self.prev_inbounds_camera_translate[1]:
                    #print("y:"+str(this_pos[1]))
                walk_info["walkmesh_found_by"] = "under"
            if corrected_pos is not None:
                if not height_only_enable:
                    walk_info["change_enable"] = True
                    walk_info["pos"][0] = corrected_pos[0]
                    walk_info["pos"][2] = corrected_pos[2]   # TODO: check y (vertical) axis against eye height and jump height etc
                #+ this_glop.eye_height #no longer needed since swizzled to xz (get_nearest_walkmesh_vec3_using_xz returns original's y in return's y)

                if walk_info["pos"][1] - corrected_pos[1] < kEpsilon:
                    walk_info["at_rest_enable"] = True
                else:
                    # Hovering higher than kEpsilon--
                    # use kEpsilon as a deadzone so that floating
                    # point errors don't cause physics and hence many
                    # at_rest events
                    walk_info["at_rest_enable"] = False
                    pass

                if corrected_pos[1] > walk_info["pos"][1]:
                    walk_info["change_enable"] = True
                    walk_info["pos"][1] = corrected_pos[1]
                else:
                    # Hovering, but previous if-else flags for physics
                    pass
            global bounds_warning_enable
            if bounds_warning_enable:
                print("[ KivyGlops ] (verbose message) walkmesh used")
                bounds_warning_enable = False
        else:
            global no_bounds_warning_enable
            if no_bounds_warning_enable:
                print("[ KivyGlops ] (verbose message) no walkmesh")
                no_bounds_warning_enable = False
            pass
        walk_info["feet_y"] = walk_info["pos"][1] - these_radii[1]
        return walk_info

    def update_view_visual_debug(self):
        global debug_dict
        # ensure essential dicts exist to avoid needing checks later:
        if "camera_glop" not in debug_dict:
            debug_dict["camera_glop"] = {}
        if "View" not in debug_dict:
            debug_dict["View"] = {}
        try:
            debug_dict["View"]["modelview_mat"] = str(self.ui.gl_widget.canvas['modelview_mat'])
        except:
            debug_dict["View"]["modelview_mat"] = "<could not finish accessing>"
        if self.camera_glop is not None:
            debug_dict["camera_glop"]["pitch"] = str(math.degrees(self.camera_glop._r_ins_x.angle))
            debug_dict["camera_glop"]["yaw"] = str(math.degrees(self.camera_glop._r_ins_y.angle))
            debug_dict["camera_glop"]["roll"] = str(math.degrees(self.camera_glop._r_ins_z.angle))
            self.camera_glop.emit_debug_to_dict(debug_dict["camera_glop"])
        if self.player_glop is not None:
            if "player_glop" not in debug_dict:
                debug_dict["player_glop"] = {}
            if self.player_glop.actor_dict is not None:
                if "land_units_per_second" in self.player_glop.actor_dict:
                    debug_dict["player_glop"]["land_units_per_second"] = self.player_glop.actor_dict["land_units_per_second"]
                if "hp" in self.player_glop.actor_dict:
                    debug_dict["player_glop"]["hp"] = self.player_glop.actor_dict["hp"]
            debug_dict["player_glop"]["clip_enable"] = self.player_glop.properties["clip_enable"]
        self.ui.update_debug_label()

    def update(self):
        # KivyGlops.update is called by KivyGlopsWindow.*update* such as update_glsl
        #super(KivyGlops, self).update()
        #region pre-bump ops
        #NOT: tried to move regions "pre-bump ops" and "bump loop" to pyglops but didn't work well
        #print("coords:"+str(Window.mouse_pos))
        #see also asp and clip_top in init
        #screen_w_arc_theta = 32.0  # actual number is from projectionMatrix matrix
        #screen_h_arc_theta = 18.0  # actual number is from projectionMatrix matrix

        global missing_bumper_warning_enable
        global missing_bumpable_warning_enable
        global missing_radius_warning_enable
        for bumper_index_index in range(0,len(self._bumper_indices)):
            bumper_index = self._bumper_indices[bumper_index_index]
            if bumper_index is not None:
                actor_glop = self.glops[bumper_index]
                bumper_name = actor_glop.name
                if actor_glop.actor_dict is None:
                    print("[ KivyGlops ] error in update: actor_dict is None for bumper named '" + str(actor_glop.name) + "'")
                if actor_glop.actor_dict is not None and \
                   "ai_enable" in actor_glop.actor_dict and \
                   actor_glop.actor_dict["ai_enable"]:
                    self.on_process_ai(bumper_index)
                    #NOTE: moveto_index and target_index are guaranteed to exist by set_as_actor_at
                    if actor_glop.actor_dict["target_index"] is not None:
                        actor_glop.actor_dict["target_pos"] = self.glops[actor_glop.actor_dict["target_index"]]._t_ins.xyz
                    elif actor_glop.actor_dict["moveto_index"] is not None:
                        if not self.glops[actor_glop.actor_dict["moveto_index"]].visible_enable:
                            actor_glop.actor_dict["moveto_index"] = None
                            if get_verbose_enable():
                                print(
                                    "[ KivyGlops ] (verbose message) actor" + \
                                    " lost target since glop at" + \
                                    " moveto_index is now invisible")
                        else:
                            actor_glop.actor_dict["target_pos"] = self.glops[actor_glop.actor_dict["moveto_index"]]._t_ins.xyz
                    if actor_glop.actor_dict["target_pos"] is not None:

                        actor_glop.state["acquire_radius"] = actor_glop.reach_radius

                        src_pos = actor_glop._t_ins.xyz
                        dest_pos = actor_glop.actor_dict["target_pos"]
                        # acquire_radius is changed below if using ranged weapon
                        distance = get_distance_vec3_xz(src_pos, dest_pos)

                        actor_glop.state["desired_use"] = None
                        actor_glop.state["desired_item_index"] = -1
                        if actor_glop.actor_dict.get("target_index") is not None:
                            weapon_index = None
                            # NOTE: uses is determined by item_dict,
                            # ranges is by actor_dict (unless use contains
                            # "shoot_", then ranges are determined by
                            # item_dict)
                            # Start desired_* as None in case item is no
                            # longer in inventory.
                            if actor_glop.actor_dict["inventory_index"] >= 0:
                                try_item = actor_glop.actor_dict["inventory_items"][actor_glop.actor_dict["inventory_index"]]
                                if "uses" in try_item:
                                    for this_use in try_item["uses"]:
                                        if this_use in self.attack_uses:
                                            actor_glop.state["desired_use"] = this_use
                                            # attack guarantees attack_types exists
                                            # (via set_as_item)
                                            actor_glop.state["desired_item_index"] = actor_glop.actor_dict["inventory_index"]  # guaranteed to exist by set_as_actor_at
                                    #TODO: loop again and look for melee
                                #else item has no use
                            if actor_glop.actor_dict["desired_item_index"] < 0:
                                # If weapon is not selected, choose random weapon even if selected a slot.
                                actor_glop.state["desired_item_index"], actor_glop.state["desired_use"] = actor_glop.find_item_with_any_use(self.attack_uses)
                            if actor_glop.state["desired_item_index"] >= 0:
                                if "shoot_" in this_use:
                                    if "ranges" in try_item and (try_item["ranges"].get(this_use) is not None):
                                        actor_glop.state["acquire_radius"] = try_item["ranges"][this_use]
                                    else:
                                        #TODO: predict arc to determine range instead
                                        actor_glop.state["acquire_radius"] = 20.
                                        if get_verbose_enable():
                                            print("[ KivyGlops ] (verbose message in update) used default acquire radius " + str(actor_glop.state["acquire_radius"]) + " since item['ranges']['" + this_use + "'] was not set")
                                else:
                                    if this_use in actor_glop.actor_dict["ranges"]:
                                        actor_glop.state["acquire_radius"] = actor_glop.actor_dict["ranges"][this_use]
                                    else:
                                        #TODO: predict arc to determine range instead
                                        actor_glop.state["acquire_radius"] = 20.
                                        if get_verbose_enable():
                                            print("[ KivyGlops ] (verbose message in update) used default acquire radius " + str(actor_glop.state["acquire_radius"]) + " since actor_dict['ranges']['" + this_use + "'] was not set")
                            else:
                                actor_glop.state["acquire_radius"] = actor_glop.reach_radius
                        # ACTUAL MOVEMENT is done further down, in
                        # #region choice-based movement and physics
            #else bumper_index is None
        #end for bumper_index
        self.on_update_glops()
        #endregion pre-bump ops

        #NOTE: (ANOTHER non-nested LOOP is at end of update, for physics and unit movement)
        #region nested bump loop
        for bumpable_index_index in range(0, len(self._bumpable_indices)):
            bumpable_index = self._bumpable_indices[bumpable_index_index]
            if bumpable_index is not None:
                item_glop = self.glops[bumpable_index]
                bumpable_name = item_glop.name
                if item_glop.bump_enable:
                    for bumper_index_index in range(0,len(self._bumper_indices)):
                        bumper_index = self._bumper_indices[bumper_index_index]
                        if bumper_index is not None:
                            actor_glop = self.glops[bumper_index]
                            bumper_name = actor_glop.name
                            distance = get_distance_kivyglops(item_glop, actor_glop)
                            if item_glop.hit_radius is not None and item_glop.hit_radius is not None:
                                total_hit_radius = 0.0
                                if item_glop.projectile_dict is not None:
                                    total_hit_radius = item_glop.hit_radius + actor_glop.hit_radius
                                else:
                                    total_hit_radius = item_glop.hit_radius + actor_glop.reach_radius
                                if distance <= total_hit_radius:
                                    #print("total_hit_radius:" + str(total_hit_radius))
                                    if bumper_index not in item_glop.in_range_indices:
                                        # (only run if ever moved away from it)
                                        if bumper_index != bumpable_index:
                                            if get_verbose_enable():
                                                print("[ KivyGlops ] (verbose message) '" + str(actor_glop.name) + "' in range of '" + str(item_glop.name) + "'")
                                            if actor_glop.bump_enable:
                                                if (item_glop.projectile_dict is None) or \
                                                   (actor_glop.hitbox is None) or \
                                                   actor_glop.hitbox.contains_vec3(item_glop._t_ins.xyz):
                                                    item_glop.state["bumped_by_index"] = bumper_index
                                                    item_glop.state["at_rest_event_enable"] = True
                                                else:
                                                    #global out_of_hitbox_note_enable
                                                    #if out_of_hitbox_note_enable:
                                                    print("[ KivyGlops ] (debug only--this is normal) within total_hit_radius, but bumpable is not in bumper's hitbox: " + actor_glop.hitbox.to_string())
                                                    #out_of_hitbox_note_enable = False
                                            else:
                                                if get_verbose_enable():
                                                    print("[ KivyGlops ] (verbose message) '" + str(actor_glop.name) + "' is not a bumper.")
                                            if not bumper_index in item_glop.in_range_indices:
                                                item_glop.in_range_indices.append(bumper_index)
                                        #else can't bump self
                                    #else:
                                        #print("not out of range yet")
                                else:
                                    if bumper_index in item_glop.in_range_indices:
                                        item_glop.in_range_indices.remove(bumper_index)
                                    if distance < 2:
                                        #debug only:
                                        #print("did not bump " + str(bumpable_name) + " (distance:" + str(distance) + "; bumper is at " + str(actor_glop._t_ins.xyz) + ")")
                                        pass
                                    pass
                            else:
                                if missing_radius_warning_enable:
                                    print("[ KivyGlops ] WARNING in update: Missing radius while bumped bumpable named "+str(bumpable_name))
                                    missing_radius_warning_enable = False
                        else:
                            pass  # None will be cleaned up after bump loop
                    #end for bumper
                #else bump_enable is False for bumpable
            else:
                pass  # None will be cleaned up later
        #endregion nested bump loop
        # (ANOTHER non-nested LOOP is at end of update, for physics and unit movement)

        # NOTE: hit detection above (such as item hitting enemy)
        # can make the item no longer bumpable or bumper,
        # so check for None:
        for j in reversed(range(len(self._bumpable_indices))):
            if self._bumpable_indices[j] == None:
                del(self._bumpable_indices[j])
        for j in reversed(range(len(self._bumper_indices))):
            if self._bumper_indices[j] == None:
                del(self._bumper_indices[j])

        #region choice-based movement and physics
        # --in that order, so you don't go through stuff
        got_frame_delay = 0.0  # do NOT move this to anywhere before hit
                               # detection is finished--otherwise
                               # invisible movement could occur (ones
                               # using got_frame_delay) before hit
                               # detection
        if self.last_update_s is not None:
            got_frame_delay = best_timer() - self.last_update_s
        self.last_update_s = best_timer()
        if not self._delay_is_available_enable:
            # prevent useless work and 0 movement warnings
            # by stopping here if got_frame_delay 0 is expected
            self._delay_is_available_enable = True
            return
        for motivated_index in range(len(self.glops)):
            m_glop = self.glops[motivated_index]
            choice_try_theta = None
            lups = None
            if m_glop.actor_dict is not None:
                lups = m_glop.actor_dict.get("land_units_per_second")
            if lups is None:
                lups = self.settings["templates"]["actor"]["land_units_per_second"]
            land_units_per_frame = lups * got_frame_delay
            if land_units_per_frame <= 0.:
                land_units_per_frame = 0.
                global show_zero_walk_upf_warning_enable
                # TODO: why does next line show exception if not
                # declared as global manually??
                if show_zero_walk_upf_warning_enable:
                    print("[ KivyGlops ] WARNING in update: zero land " + \
                          "units per frame (this is the last time this" + \
                          " message will be shown)")
                    show_zero_walk_upf_warning_enable = False

            ldps = None
            if m_glop.actor_dict is not None:
                ldps = m_glop.actor_dict.get("land_degrees_per_second")
            if ldps is None:
                ldps = self.settings["templates"]["actor"]["land_degrees_per_second"]
            land_radians_per_frame = math.radians(ldps) * got_frame_delay
            if land_radians_per_frame <= 0.:
                land_radians_per_frame = 0.
                global show_zero_degrees_pf_warning_enable
                if show_zero_degrees_pf_warning_enable:
                    print("[ KivyGlops ] WARNING in update: zero land " + \
                          "degrees per frame (this is the last time " + \
                          "this message will be shown)")
                    show_zero_degrees_pf_warning_enable = False

            # choice_try_vel_multiplier will be constrained later:
            rotation_multiplier_y = 0.0  # 1.0 is maximum speed
            # NOTE: Increased z should move object closer to viewer
            # in right-handed coordinate system
            choice_try_vel_multiplier = [0.0, 0.0, 0.0] # 1.0 is max
                                                        # joystick tilt:
                                                        # use [0],[2]

            if m_glop.actor_dict is not None and \
               m_glop.actor_dict["target_pos"] is not None:
                # If has target_pos, auto-move to target without
                # intervention even if is player-controlled glop.
                m_glop.look_at_pos(m_glop.actor_dict["target_pos"])
                src_pos = m_glop._t_ins.xyz
                dest_pos = m_glop.actor_dict["target_pos"]
                distance = get_distance_vec3_xz(src_pos, dest_pos)
                if m_glop.state.get("acquire_radius") is not None:
                    if distance > m_glop.state["acquire_radius"]:
                        choice_try_theta = get_angle_between_two_vec3_xz(src_pos, dest_pos)
                        choice_try_vel_multiplier[0], choice_try_vel_multiplier[2] = get_rect_from_polar_rad(1.0, choice_try_theta)
                    if m_glop.actor_dict["target_index"] is not None:
                        # If has weapon and attack target, auto-attack
                        # even if is player-controlled glop
                        #if m_glop.actor_dict["target_index"] is not None:
                            if m_glop.state["desired_item_index"] >= 0:
                                try:
                                    self.use_item_at(m_glop, m_glop.state["desired_item_index"], this_use=m_glop.state["desired_use"])
                                except:
                                    print("[ KivyGlops ] ERROR in update--could not finish using item " + str(m_glop.state.get("desired_item_index")))
                                    view_traceback()
                            else:
                                if not m_glop.actor_dict["unarmed_melee_enable"]:
                                    m_glop.actor_dict["target_index"] = None
                        # else in range but can't attack
                else:
                    print("[ KivyGlops ] ERROR in update: 'target_pos' was set but the engine forgot to calculate 'acquire_radius'")
            elif motivated_index == self.get_player_glop_index(1):
                # for keycode strings, see  http://kivy.org/docs/_modules/kivy/core/window.html
                if self.player1_controller.get_pressed(self.ui.get_keycode("a")):
                    #if self.player1_controller.get_pressed(self.ui.get_keycode("shift")):
                    choice_try_vel_multiplier[0] = 1.0
                    #else:
                    #    rotation_multiplier_y = -1.0
                if self.player1_controller.get_pressed(self.ui.get_keycode("d")):
                    #if self.player1_controller.get_pressed(self.ui.get_keycode("shift")):
                    choice_try_vel_multiplier[0] = -1.0
                    #else:
                    #    rotation_multiplier_y = 1.0
                if self.player1_controller.get_pressed(self.ui.get_keycode("w")):
                    if self.get_fly_by_name(m_glop.name):
                        #intentionally use z,y:
                        choice_try_vel_multiplier[2], choice_try_vel_multiplier[1] = get_rect_from_polar_rad(1.0, m_glop._r_ins_x.angle)
                    else:
                        choice_try_vel_multiplier[2] = 1.0

                if self.player1_controller.get_pressed(self.ui.get_keycode("s")):
                    if self.get_fly_by_name(m_glop.name):
                        #intentionally use z,y:
                        choice_try_vel_multiplier[2], choice_try_vel_multiplier[1] = get_rect_from_polar_rad(1.0, m_glop._r_ins_x.angle)
                        choice_try_vel_multiplier[2] *= -1.0
                        choice_try_vel_multiplier[1] *= -1.0
                    else:
                        choice_try_vel_multiplier[2] = -1.0

                if self.player1_controller.get_pressed(self.ui.get_keycode("enter")):
                    self.use_selected(m_glop)

                if self.player1_controller.get_pressed(self.ui.get_keycode("spacebar")):
                    if m_glop.state["at_rest_enable"]:
                        #TODO: double-jump
                        choice_try_vel_multiplier[1] = 1.
                    #    if get_verbose_enable():
                    #        print("[ KivyGlops ] (verbose message " + \
                    #              "in update: jumped (tried maximum)")
                    else:
                    #    if get_verbose_enable():
                    #        print("[ KivyGlops ] (verbose message " + \
                    #              "in update: can't jump while not " + \
                    #              "on ground.")
                        pass

            # ACTUAL MOVEMENT is done only if the object is at rest
            # (see else case below).
            check_pos_enable = False
            choice_moved_enable = False
            choice_result_deltas = [0.0, 0.0, 0.0]
            if m_glop.state["at_rest_enable"] or \
                    self.get_fly_by_name(m_glop.name):
                # can control own movement
                if rotation_multiplier_y != 0.0:
                    delta_y = land_radians_per_frame * rotation_multiplier_y
                    m_glop._r_ins_y.angle += delta_y
                    #origin_distance = math.sqrt(m_glop._t_ins.x*m_glop._t_ins.x + m_glop._t_ins.z*m_glop._t_ins.z)
                    #m_glop._t_ins.x -= origin_distance * math.cos(delta_y)
                    #m_glop._t_ins.z -= origin_distance * math.sin(delta_y)

                #xz coords of edges of 16x16 square are:
                # move in the direction you are facing
                choice_result_turn_theta = None
                choice_result_move_theta = None
                if choice_try_vel_multiplier[0] != 0.0 or choice_try_vel_multiplier[1] != 0.0 or choice_try_vel_multiplier[2] != 0.0:
                    #makes movement relative to rotation (which alaso limits speed when moving diagonally):
                    choice_result_move_theta = theta_radians_from_rectangular(choice_try_vel_multiplier[0], choice_try_vel_multiplier[2])
                    moving_r_multiplier = math.sqrt((choice_try_vel_multiplier[0]*choice_try_vel_multiplier[0])+(choice_try_vel_multiplier[2]*choice_try_vel_multiplier[2]))
                    if moving_r_multiplier > 1.0:
                        moving_r_multiplier = 1.0  # Limited so that you can't move faster when moving diagonally
                        #print("[ KivyGlops ] WARNING in update: (if" + \
                        #      " math were correct, this should " + \
                        #      "never happen) clipped >100% movement")
                    choice_result_r_vel = land_units_per_frame * moving_r_multiplier
                    radial_xz_velocity = math.sqrt((m_glop.velocity[0]*m_glop.velocity[0])+(m_glop.velocity[2]*m_glop.velocity[2]))
                    if choice_result_r_vel + radial_xz_velocity > land_units_per_frame:
                        choice_result_r_vel -= (choice_result_r_vel + radial_xz_velocity) - land_units_per_frame
                    if choice_result_r_vel < kEpsilon:
                        choice_result_r_vel = 0.0

                    #TODO: reprogram so adding math.radians(-90) is not needed (?) or remove these comments if works now
                    #choice_result_deltas[0] = land_units_per_frame*moving_r_multiplier * math.cos(m_glop._r_ins_y.angle+choice_result_move_theta+math.radians(-90))
                    #choice_result_deltas[1] = land_units_per_frame*choice_try_vel_multiplier[1]
                    #choice_result_deltas[2] = land_units_per_frame*moving_r_multiplier * math.sin(m_glop._r_ins_y.angle+choice_result_move_theta+math.radians(-90))
                    choice_result_deltas[0] = choice_result_r_vel * math.cos(choice_result_move_theta)
                    choice_result_deltas[1] = land_units_per_frame * choice_try_vel_multiplier[1]
                    choice_result_deltas[2] = choice_result_r_vel * math.sin(choice_result_move_theta)

                    # if (m_glop._t_ins.x + move_by_x > self._world_cube.get_max_x()):
                    #     move_by_x = self._world_cube.get_max_x() - m_glop._t_ins.x
                    #     print(str(m_glop._t_ins.x)+" of max_x:"+str(self._world_cube.get_max_x()))
                    # if (m_glop._t_ins.z + move_by_z > self._world_cube.get_max_z()):
                    #     move_by_z = self._world_cube.get_max_z() - m_glop._t_ins.z
                    #     print(str(m_glop._t_ins.z)+" of max_z:"+str(self._world_cube.get_max_z()))
                    # if (m_glop._t_ins.x + move_by_x < self._world_cube.get_min_x()):
                    #     move_by_x = self._world_cube.get_min_x() - m_glop._t_ins.x
                    #     print(str(m_glop._t_ins.x)+" of max_x:"+str(self._world_cube.get_max_x()))
                    # if (m_glop._t_ins.z + move_by_z < self._world_cube.get_min_z()):
                    #     move_by_z = self._world_cube.get_min_z() - m_glop._t_ins.z
                    #     print(str(m_glop._t_ins.z)+" of max_z:"+str(self._world_cube.get_max_z()))

                    #print(str(m_glop._t_ins.xz)+" each coordinate should be between matching one in "+str(self._world_cube.get_min_x())+","+str(self._world_cube.get_min_z())+" and "+str(self._world_cube.get_max_x())+","+str(self._world_cube.get_max_z()))
                    #print(str( (m_glop._t_ins.xyz) )+" each coordinate should be between matching one in "+str(self.world_boundary_min)+" and "+str(self.world_boundary_max))
                if choice_try_theta is not None:
                    choice_result_turn_theta = choice_try_theta
                for axis_i in range(0,3):
                    if choice_result_deltas[axis_i] != 0.0:
                        choice_moved_enable = True
                        m_glop.velocity[axis_i] += choice_result_deltas[axis_i]
            #end if at rest can move self
            ## NO HIT DETECTION SHOULD BE DONE AFTER 1ST CHANGE (ABOVE)

                for axis_i in range(0,3):
                    if m_glop.velocity[axis_i] != 0.0:
                        #set _t_ins via set_coord:
                        m_glop.set_coord(axis_i,
                                         m_glop.velocity[axis_i])


                #self.prev_inbounds_camera_translate = self.camera_glop._t_ins.x, self.camera_glop._t_ins.y, self.camera_glop._t_ins.z

                # else:
                #     self.camera_glop._t_ins.x += self.land_units_per_frame * choice_try_vel_multiplier[0]
                #     self.camera_glop._t_ins.z += self.land_units_per_frame * choice_try_vel_multiplier[2]
                if choice_result_turn_theta is not None:
                #if land_units_per_frame is not None:
                    m_glop._r_ins_y.angle = choice_result_turn_theta  # TODO: use land_radians_per_frame instead of turning instantly
                #    m_glop._t_ins.x += choice_try_vel_multiplier[0]
                #    m_glop._t_ins.z += choice_try_vel_multiplier[2]
                #else:
                #    print("[ KivyGlops ] ERROR in update: choice_result_turn_theta was set for unit, but engine forgot to set land_units_per_frame")


            if m_glop.look_target_glop is not None:
                m_glop.look_at(m_glop.look_target_glop) # TODO: use land_radians_per_frame instead of turning instantly
                #print(str(m_glop.name)+" looks at "+str(m_glop.look_target_glop.name))
                #print("  at "+str((self.camera_glop._t_ins.x, self.camera_glop._t_ins.y, self.camera_glop._t_ins.z)))
            #end else at rest and can control own movement
            if choice_moved_enable:
                check_pos_enable = True
            if (not m_glop.state["at_rest_enable"]) or \
               choice_moved_enable:
                #if not m_glop.state["at_rest_enable"]:
                #if m_glop._cached_floor_y is None:
                #    m_glop._cached_floor_y = self._world_min_y
                #    #TODO: get from walkmesh instead and eliminate _cached_floor_y
                if m_glop.physics_enable:
                    if m_glop.state.get("show_physics_msg_enable") is None:
                        if get_verbose_enable():
                            print("[ KivyGlops ] (verbose message " + \
                                "in update) processing first run of" + \
                                " physics for " + m_glop.name)
                        m_glop.state["show_physics_msg_enable"] = True

                    #walk_info = self.constrain_glop_to_walkmesh(m_glop)
                    #at_rest_enable = walk_info.get("at_rest_enable")
                    #if at_rest_enable is not None:
                    #    if m_glop.state["at_rest_enable"] != at_rest_enable:
                    #        m_glop.state["at_rest_enable"] = at_rest_enable
                    #        m_glop.state["at_rest_event_enable"] = True
                    #deprecated this_glop_free_enable = False
                    #if m_glop._cached_floor_y is not None:
                    #    if m_glop._t_ins.y - m_glop.hit_radius - kEpsilon > m_glop._cached_floor_y:
                    #        #this_glop_free_enable = True
                    #        pass
                    #    else: # STOP object (remove owner and projectile_dict)
                    #        m_glop.state["at_rest_enable"] = True
                    #else:
                    #    pass
                    #    #no cached floor, so move without regard to ground
                    #    #this_glop_free_enable = True

                    if m_glop.state["at_rest_event_enable"]:  # HIT GROUND (or target if m_glop.state.get("bumped_by_index") is not None
                        m_glop.state["at_rest_event_enable"] = False
                        bumper_index = item_glop.state.get("bumped_by_index")
                        self.on_bump(motivated_index, bumper_index)
                        #TODO: optionally, such as for bottom-heavy items: m_glop._r_ins_x.angle = 0.
                        #if m_glop.velocity[2] > kEpsilon:
                        #if (m_glop.velocity[1] < 0.0 - (kEpsilon + m_glop.hit_radius)):
                        #print("  HIT GROUND Y:"+str(m_glop._cached_floor_y))
                        # bump_sound_paths is guaranteed by PyGlop _init_glop to exist
                        if len(m_glop.properties["bump_sound_paths"]) > 0:
                            rand_i = random.randrange(0,len(m_glop.properties["bump_sound_paths"]))
                            self.play_sound(m_glop.properties["bump_sound_paths"][rand_i])

                        bumpable_index = motivated_index
                        item_glop = self.glops[bumpable_index]
                        actor_glop = None
                        actor_glop_name = None
                        if bumper_index is not None:
                            actor_glop = self.glops[bumper_index]
                            actor_glop_name = actor_glop.name
                        #NOTE: already checked
                        # bumpable_index bump_enable above
                        #print("distance:" + str(total_hit_radius) + " <= total_hit_radius:" + str(total_hit_radius))
                        if item_glop.projectile_dict is None or \
                           ("owner" not in item_glop.projectile_dict) or \
                           (item_glop.projectile_dict["owner"] != actor_glop_name):
                            self._internal_bump_glop(bumpable_index, bumper_index)
                            if get_verbose_enable():
                                if actor_glop is not None:
                                    print("[ KivyGlops ] (verbose message in update) " + str(actor_glop.name) + " bumped " + str(item_glop.name))
                                elif actor_glop is not None:
                                    print("[ KivyGlops ] (verbose message in update) " + str(actor_glop.name) + " bumped world")
                        else:
                            if get_verbose_enable():
                                print("[ KivyGlops ] (verbose message) cannot bump own projectile")

                        # NOTE: projectile_dict is already removed above
                        # by _internal_bump_glop if relevant
                        if m_glop.item_dict is not None:
                            if m_glop.item_dict["state"].get("owner") is not None:
                                del m_glop.item_dict["state"]["owner"]
                            if m_glop.item_dict["state"].get("owner_index") is not None:
                                del m_glop.item_dict["state"]["owner_index"]

                        #m_glop._t_ins.y = m_glop._cached_floor_y + m_glop.hit_radius
                        #check_pos_enable = True
                        #if m_glop.velocity[0] != 0.0 or \
                        #   m_glop.velocity[1] != 0.0 or \
                        #   m_glop.velocity[2] != 0.0:
                        #    if get_verbose_enable():
                        #        print("[ KivyGlops ] stopped glop {" + \
                        #              "hit_radius:" + \
                        #              str(m_glop.hit_radius) + \
                        #              "; glop._cached_floor_y:" + \
                        #              str(m_glop._cached_floor_y) + \
                        #              "}")
                        m_glop.velocity[1] = 0.0
                    if m_glop.velocity[1] < kEpsilon:
                        #if no vertical velocity, assume friction
                        if m_glop.velocity[0] > kEpsilon:
                            m_glop.velocity[0] /= 2.
                        else:
                            m_glop.velocity[0] = 0.
                        #y is done based on gravity above
                        if m_glop.velocity[2] > kEpsilon:
                            m_glop.velocity[2] /= 2.
                        else:
                            m_glop.velocity[2] = 0.
                        #this_glop_free_enable = False
                    if not m_glop.state["at_rest_enable"]:
                        m_glop._r_ins_x.angle += math.radians(15.) * got_frame_delay #TODO: why does chaning rotation make things stop above ground(?)
                        if (m_glop._r_ins_x.angle > 2.0*math.pi):
                            m_glop._r_ins_x.angle -= 2.0*math.pi
                        m_glop._t_ins.x += m_glop.velocity[0] * got_frame_delay
                        m_glop._t_ins.y += m_glop.velocity[1] * got_frame_delay
                        m_glop._t_ins.z += m_glop.velocity[2] * got_frame_delay
                        #don't do hit detection again until user (& ai at top of this method) sees this frame
                        if got_frame_delay > 0.0:
                            check_pos_enable = True
                            #print("[ KivyGlops ] (verbose message) GRAVITY AFFECTED:"+str(m_glop._t_ins.y)+" += "+str(m_glop.velocity[1]))
                            m_glop.velocity[1] -= self.settings["world_gravity_acceleration"] * got_frame_delay
                            #print("[ KivyGlops ] (verbose message) THEN VELOCITY CHANGED TO:"+str(m_glop.velocity[1]))
                            #print("[ KivyGlops ] (verbose message) FRAME INTERVAL:"+str(got_frame_delay))
                        else:
                            if self._delay_is_available_enable:
                                print("[ KivyGlops ] WARNING in update: no frame delay is detectable (update normally runs automatically once per frame but seems to be running more often)")
                    else:
                        if m_glop.item_dict is not None:
                            #TODO: rolling friction?
                            #TODO: make roll_enable instead
                            # roll if moving forward
                            # see also friction above
                            m_glop._r_ins_x.angle += math.radians(15.) * got_frame_delay * m_glop.velocity[2]
                            m_glop._r_ins_z.angle += math.radians(15.) * got_frame_delay * m_glop.velocity[0]
                            pass
                #end if physics_enable

                #if choice_try_vel_multiplier[0] != 0.0 or \
                #   choice_try_vel_multiplier[1] != 0.0 or \
                #   choice_try_vel_multiplier[2] != 0.0:
                    #did NOT necessarily move (deltas already checked)
                if (not m_glop.state["at_rest_enable"]):
                    if choice_result_deltas[0] != 0.0 or \
                       choice_result_deltas[1] != 0.0 or \
                       choice_result_deltas[2] != 0.0:
                        #then already did check_pos_enable = True when set
                        if get_verbose_enable():
                            prev_at_rest_enable = m_glop.state.get("prev_at_rest_enable")
                            if prev_at_rest_enable != m_glop.state["at_rest_enable"]:
                                print("[ KivyGlops ] (verbose message in update) glop " + m_glop.name + " tried to move, but was not at rest (was affected by physics)")
                m_glop.state["prev_at_rest_enable"] = m_glop.state["at_rest_enable"]
                m_glop.state["constrained_enable"] = False
                #deprecated this_glop_free_enable
                #deprecated stop_this_bumpable_enable
                for rel in m_glop.state["links"]:
                    if rel["r_type"] == "carry":
                        if m_glop._t_ins.xyz != rel["state"]["parent_glop"]._t_ins.xyz:
                            m_glop._t_ins.x = rel["state"]["parent_glop"]._t_ins.x
                            m_glop._t_ins.y = rel["state"]["parent_glop"]._t_ins.y
                            m_glop._t_ins.z = rel["state"]["parent_glop"]._t_ins.z
                            check_pos_enable = True
                        m_glop.state["at_rest_enable"] = True
                        m_glop.state["constrained_enable"] = True
                    else:
                        print("[ KivyGlops ] ERROR in update: " + \
                              "unknown link r_type " + str(rel.get("r_type")))

                #if m_glop.physics_enable:
                if motivated_index == self.get_player_glop_index(1):
                    if not "player_glop" in debug_dict:
                        debug_dict["player_glop"] = {}
                    debug_dict["player_glop"]["check_pos_enable"] = check_pos_enable
                if check_pos_enable and m_glop.properties["clip_enable"]:
                    world_bottom_enable = True
                    walk_info = None
                    walkmesh_enable = True  # false for debug only
                    if walkmesh_enable:
                        if len(self._walkmeshes) > 0:
                            world_bottom_enable = False
                            #constrained_pos = [m_glop._t_ins.x,
                            #                   m_glop._t_ins.y,
                            #                   m_glop._t_ins.z]
                            if m_glop.hitbox is not None:
                                walk_info = self.get_walk_info(
                                    m_glop._t_ins.xyz,
                                    (m_glop.hitbox.maximums[0], -m_glop.minimums[1]))
                            else:
                                walk_info = self.get_walk_info(
                                    m_glop._t_ins.xyz,
                                    (m_glop.hit_radius, m_glop.hit_radius))
                            if motivated_index == self.get_player_glop_index(1):
                                if "player_glop" not in debug_dict:
                                    debug_dict["player_glop"] = {}
                                debug_dict["player_glop"]["walkmesh_found_by"] = walk_info["walkmesh_found_by"]
                                debug_dict["player_glop"]["feet_y"] = walk_info["feet_y"]

                        else:
                            walkmesh_enable = False
                    if world_bottom_enable:
                        walk_info = {}
                        walk_info["pos"] = [ m_glop._t_ins.x, m_glop._t_ins.y, m_glop._t_ins.z ]
                        walk_info["change_enable"] = False
                        height_only_enable = True
                        corrected_pos = [ m_glop._t_ins.x, m_glop._t_ins.y, m_glop._t_ins.z ]
                        if corrected_pos[1] < self.settings["no_walkmesh_world_bottom"]:
                            corrected_pos[1] = self.settings["no_walkmesh_world_bottom"]
                        hit_bottom_enable = None
                        if not height_only_enable:
                            walk_info["change_enable"] = True
                            walk_info["pos"][0] = corrected_pos[0]
                            walk_info["pos"][2] = corrected_pos[2]   # TODO: check y (vertical) axis against eye height and jump height etc
                        #region pasted from get_walk_info
                        if walk_info["pos"][1] - corrected_pos[1] < kEpsilon:
                            walk_info["at_rest_enable"] = True
                        else:
                            # Hovering higher than kEpsilon--
                            # use kEpsilon as a deadzone so that floating
                            # point errors don't cause physics and hence many
                            # at_rest events
                            walk_info["at_rest_enable"] = False
                            pass

                        if corrected_pos[1] > walk_info["pos"][1]:
                            walk_info["change_enable"] = True
                            walk_info["pos"][1] = corrected_pos[1]
                        else:
                            # Hovering, but previous if-else flags for physics
                            pass
                        #endregion pasted from get_walk_info

                    at_rest_enable = walk_info.get("at_rest_enable")
                    if at_rest_enable is not None:
                        if m_glop.state["at_rest_enable"] != at_rest_enable:
                            m_glop.state["at_rest_enable"] = at_rest_enable
                            if at_rest_enable:
                                m_glop.state["at_rest_event_enable"] = True
                                # Do it here so that frame of hit
                                # is shown to player and ai
                                # BEFORE event happens
                            else:
                                pass
                                #m_glop.state["not_at_rest_event_enable"] = True
                                #TODO: (?) make an on_not_at_rest event
                    if walk_info["change_enable"]:
                        m_glop._t_ins.x = walk_info["pos"][0]
                        #if at_rest_enable is True:
                        m_glop._t_ins.y = walk_info["pos"][1]
                        m_glop._t_ins.z = walk_info["pos"][2]


        #end for index in glops
        #movitated_glop out of scope
        #for index in self._bumper_indices:
        #    m_glop = self.glops[index]
        #    walk_info = self.constrain_glop_to_walkmesh(m_glop)
        #    at_rest_enable = walk_info.get("at_rest_enable")
        #    if at_rest_enable is not None:
        #        if m_glop.state["at_rest_enable"] != at_rest_enable:
        #            m_glop.state["at_rest_enable"] = at_rest_enable
        #            print("[ KivyGlops ] WARNING: update changed rest state of " + m_glop.name + " to " + str(at_rest_enable) + " but at_rest events were not fired nor was manual programming done (not yet implemented)")
        #endregion choice-based movement and physics

        if self.settings["camera_perspective_number"] == self.CAMERA_FIRST_PERSON():
            self.camera_glop._t_ins.x = self.player_glop._t_ins.x
            self.camera_glop._t_ins.y = self.player_glop._t_ins.y + self.player_glop.eye_height
            self.camera_glop._t_ins.z = self.player_glop._t_ins.z
            self.camera_glop._r_ins_x.angle = self.player_glop._r_ins_x.angle
            self.camera_glop._r_ins_y.angle = self.player_glop._r_ins_y.angle
            self.camera_glop._r_ins_z.angle = self.player_glop._r_ins_z.angle
        elif self.settings["camera_perspective_number"] == self.CAMERA_FREE():
            pass
        else:
            print("[ KivyGlops ] ERROR in update: " + \
                  "settings['camera_perspective_number'] " + \
                  str(self.settings["camera_perspective_number"]) + \
                  " is not yet implemented. Try setting number to " + \
                  " in scene to one of the self.CAMERA_*()" + \
                  " methods' returns.")



        asp = float(self.ui.width) / float(self.ui.height)

        clip_top = 0.06  #NOTE: 0.03 is ~1.72 degrees, if that matters
        # formerly field_of_view_factor
        # was changed to .03 when projection_near was changed from 1 to .1
        # was .3 when projection_near was 1

        clip_right = asp*clip_top  # formerly overwrote asp
        self.projectionMatrix = Matrix()
        self.modelViewMatrix = Matrix()

        #self.modelViewMatrix.rotate(self.camera_glop._r_ins_x.angle,1.0,0.0,0.0)
        #self.modelViewMatrix.rotate(self.camera_glop._r_ins_y.angle,0.0,1.0,0.0)
        #look_at(eyeX, eyeY, eyeZ, centerX, centerY, centerZ, upX, upY, upZ)  $http://kivy.org/docs/api-kivy.graphics.transformation.html
        #self.modelViewMatrix.rotate(self.camera_glop._r_ins_z.angle,0.0,0.0,1.0)
        previous_look_point = None
        if self.look_point is not None:
            previous_look_point = self.look_point[0], self.look_point[1], self.look_point[2]

        self.look_point = [0.0, 0.0, 0.0]

        #0 is the angle (1, 2, and 3 are the matrix)
        self.look_point[0] = self.focal_distance * math.cos(self.camera_glop._r_ins_y.angle)
        self.look_point[2] = self.focal_distance * math.sin(self.camera_glop._r_ins_y.angle)
        #print("self.camera_glop._r_ins_y.angle: "+str(self.camera_glop._r_ins_y.angle))

        #self.look_point[1] = 0.0  #(changed in "for" loop below) since y is up, and 1 is y, ignore index 1 when we are rotating on that axis
        self.look_point[1] = self.focal_distance * math.sin(self.camera_glop._r_ins_x.angle)


        #self.modelViewMatrix = self.modelViewMatrix.look_at(0,self.camera_glop._t_ins.y,0, self.look_point[0], self.look_point[1], self.look_point[2], 0, 1, 0)

        #Since camera's target should be relative to camera, add camera's position:

        self.look_point[0] += self.camera_glop._t_ins.x
        self.look_point[1] += self.camera_glop._t_ins.y
        self.look_point[2] += self.camera_glop._t_ins.z

        #must translate first, otherwise look_at will override position on rotation axis ('y' in this case)
        self.modelViewMatrix.translate(self.camera_glop._t_ins.x, self.camera_glop._t_ins.y, self.camera_glop._t_ins.z)
        self.modelViewMatrix = self.modelViewMatrix.look_at(self.camera_glop._t_ins.x, self.camera_glop._t_ins.y, self.camera_glop._t_ins.z, self.look_point[0], self.look_point[1], self.look_point[2], 0, 1, 0)



        #projectionMatrix.view_clip(left, right, bottom, top, near, far, perspective)
        #"In OpenGL, a 3D point in eye space is projected onto the near plane (projection plane)"
        # -http://www.songho.ca/opengl/gl_projectionmatrix.html
        #The near plane and far plane distances are in the -z direction but are
        # expressed as positive values since they are distances from the camera
        # then they are compressed to -1 to 1
        # -https://www.youtube.com/watch?v=frtzb2WWECg
        self.projectionMatrix = self.projectionMatrix.view_clip(-clip_right, clip_right, -1*clip_top, clip_top, self.projection_near, 100, 1)  # last params: far, perspective
        top_theta = theta_radians_from_rectangular(self.projection_near, clip_top)
        right_theta = theta_radians_from_rectangular(self.projection_near, clip_right)
        self.ui.screen_w_arc_theta = right_theta*2.0
        self.ui.screen_h_arc_theta = top_theta*2.0

        self.ui.gl_widget.canvas['projection_mat'] = self.projectionMatrix
        self.ui.gl_widget.canvas['modelview_mat'] = self.modelViewMatrix
        self.ui.gl_widget.canvas["camera_world_pos"] = self.camera_glop._t_ins.xyz
        #if get_verbose_enable():
        #    Logger.debug("ok (update_glsl)")

        #is_look_point_changed = False
        #if previous_look_point is not None:
        #    for axis_index in range(3):
        #        if self.look_point[axis_index] != previous_look_point[axis_index]:
        #            is_look_point_changed = True
        #            #print(str(self.look_point)+" was "+str(previous_look_point))
        #            break
        #else:
        #    is_look_point_changed = True
        #
        #if is_look_point_changed:
        #    #print("Now looking at "+str(self.look_point))
        #    #print ("position: "+str( (self.camera_glop._t_ins.x, self.camera_glop._t_ins.y, self.camera_glop._t_ins.z) )+"; self.camera_glop._r_ins_y.angle:"+str(self.camera_glop._r_ins_y.angle) +"("+str(math.degrees(self.camera_glop._r_ins_y.angle))+"degrees); moving_theta:"+str(math.degrees(moving_theta))+" degrees")

        if (self._previous_world_light_dir is None
            or self._previous_world_light_dir[0]!=self.ui.gl_widget.canvas["_world_light_dir"][0]
            or self._previous_world_light_dir[1]!=self.ui.gl_widget.canvas["_world_light_dir"][1]
            or self._previous_world_light_dir[2]!=self.ui.gl_widget.canvas["_world_light_dir"][2]
            or self._previous_camera_rotate_y_angle is None
            or self._previous_camera_rotate_y_angle != self.camera_glop._r_ins_y.angle
            ):
            #self.ui.gl_widget.canvas["_world_light_dir"] = (0.0,.5,1.0);
            #self.ui.gl_widget.canvas["_world_light_dir_eye_space"] = (0.0,.5,1.0);
            world_light_theta = theta_radians_from_rectangular(self.ui.gl_widget.canvas["_world_light_dir"][0], self.ui.gl_widget.canvas["_world_light_dir"][2])
            light_theta = world_light_theta+self.camera_glop._r_ins_y.angle
            light_r = math.sqrt((self.ui.gl_widget.canvas["_world_light_dir"][0]*self.ui.gl_widget.canvas["_world_light_dir"][0])+(self.ui.gl_widget.canvas["_world_light_dir"][2]*self.ui.gl_widget.canvas["_world_light_dir"][2]))
            self.ui.gl_widget.canvas["_world_light_dir_eye_space"] = light_r * math.cos(light_theta), self.ui.gl_widget.canvas["_world_light_dir_eye_space"][1], light_r * math.sin(light_theta)
            self._previous_camera_rotate_y_angle = self.camera_glop._r_ins_y.angle
            self._previous_world_light_dir = self.ui.gl_widget.canvas["_world_light_dir"][0], self.ui.gl_widget.canvas["_world_light_dir"][1], self.ui.gl_widget.canvas["_world_light_dir"][2]
        self._delay_is_available_enable = True
        self.update_view_visual_debug()
    # end update
    def append_wobject(self, this_wobject, pivot_to_geometry_enable=True):
        super(KivyGlop, self).append_wobject(this_wobject, pivot_to_geometry_enable=pivot_to_geometry_enable)
        if self.material is not None:
            self._color_instruction = Color(self.material.diffuse_color[0], self.material.diffuse_color[1], self.material.diffuse_color[2], self.material.diffuse_color[3])
        else:
            print("[ KivyGlops ] WARNING in append_wobject: self.material is None for " + str(self.name))


class GLWidget(Widget):
    pass


class HudForm(BoxLayout):
    pass


class ContainerForm(BoxLayout):
    pass


class KivyGlopsWindow(ContainerForm):  # formerly a subclass of Widget

    scene = None  # only use for drawing frames and sending input
    frames_per_second = None
    _fps_last_frame_tick = None
    _fps_accumulated_time = None
    _fps_accumulated_count = None
    _average_fps = None
    _contexts = None # InstructionGroup so gl operations can be added in realtime (after resetCallback is added, but so resetCallback is on the stack after them)
    #region Window TODO: rename to _*
    use_button = None
    hud_bg_rect = None
    screen_w_arc_theta = None
    screen_h_arc_theta = None
    #endregion Window TODO: rename to _*
    #region Window
    hud_form = None
    hud_buttons_form = None
    gl_widget = None
    #endregion Window
    dummy_glop = None

    def __init__(self, **kwargs):
        #self.scene = KivyGlops()
        #self.scene.ui = self
        self.debug_label_suspended_level = 0
        dummy_glop = KivyGlop()
        self._fps_accumulated_time = 0.0
        self._fps_accumulated_count = 0
        self.frames_per_second = 60.0
        self.gl_widget = GLWidget()
        self.hud_form = HudForm(orientation="vertical",
                                size_hint=(1.0, 1.0))
        self.hud_buttons_form = BoxLayout(orientation="horizontal",
                                          size_hint=(1.0, 0.1))

        #fix incorrect keycodes if present (such as in kivy <= 1.8.0):
        if (Keyboard.keycodes["-"]==41):
            Keyboard.keycodes["-"]=45
        if (Keyboard.keycodes["="]==43):
            Keyboard.keycodes["="]=61

        try:
            self._keyboard = Window.request_keyboard(
                self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
            self._keyboard.bind(on_key_up=self._on_keyboard_up)
        except:
            print("[ KivyGlopsWindow ] Could not finish loading " + \
                  "keyboard (keyboard may not be present).")

        #self.bind(on_touch_down=self.canvasTouchDown)

        self.gl_widget.canvas = RenderContext(compute_normal_mat=True)
        self.gl_widget.canvas["_world_light_dir"] = (0.0, 0.5, 1.0)
        self.gl_widget.canvas["_world_light_dir_eye_space"] = (0.0, 0.5, 1.0)  # rotated in update*
        self.gl_widget.canvas["camera_light_multiplier"] = (1.0, 1.0, 1.0, 1.0)
        #self.gl_widget.canvas.shader.source = resource_find('simple1b.glsl')
        #self.gl_widget.canvas.shader.source = resource_find('shade-kivyglops-standard.glsl')  # NOT working
        #self.gl_widget.canvas.shader.source = resource_find('shade-normal-only.glsl') #partially working
        #self.gl_widget.canvas.shader.source = resource_find('shade-texture-only.glsl')
        #self.gl_widget.canvas.shader.source = resource_find(os.path.join('shaders','fresnel.glsl'))
        shader_path = None
        if _multicontext_enable:
            #self.gl_widget.canvas.shader.source = resource_find('kivyglops-testing.glsl')  # NOT working
            shader_path = os.path.join('shaders','kivyglops.glsl')
        else:
            shader_path = os.path.join('shaders','kivyglops-singlecontext.glsl')
        print("[ KivyGlopsWindow ] default shader has been set to '" + \
              shader_path + "'")
        self.gl_widget.canvas.shader.source = resource_find(shader_path)

        #formerly, .obj was loaded here using load_obj (now calling program does that)

        #print(self.gl_widget.canvas.shader)  #just prints type and memory address
        if dump_enable:
            glopsYAMLLines = []
            #self.scene.emit_yaml(glopsYAMLLines)
            try:
                thisFile = open('glops-dump.yml', 'w')
                for i in range(0,len(glopsYAMLLines)):
                    thisFile.write(glopsYAMLLines[i] + "\n")
                thisFile.close()
            except:
                print("[ KivyGlopsWindow ] Could not finish writing dump.")
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
        self._contexts = InstructionGroup() #RenderContext(compute_normal_mat=True)
        self.gl_widget.canvas.add(self._contexts)

        self.finalize_canvas()
        self.add_widget(self.gl_widget)
        #self.hud_form.rows = 1
        self.add_widget(self.hud_form)

        self.debug_label = Factory.Label(text="...", color=(.5,.5,.5,1.0))
        self.hud_form.add_widget(self.debug_label)
        self.hud_form.add_widget(self.hud_buttons_form)
        self.inventory_prev_button = Factory.Button(text="<", id="inventory_prev_button", size_hint=(.2,1.0), on_press=self.inventory_prev_button_press)
        self.use_button = Factory.Button(text="0: Empty", id="use_button", size_hint=(.2,1.0), on_press=self.inventory_use_button_press)
        self.inventory_next_button = Factory.Button(text=">", id="inventory_next_button", size_hint=(.2,1.0), on_press=self.inventory_next_button_press)
        self.hud_buttons_form.add_widget(self.inventory_prev_button)
        self.hud_buttons_form.add_widget(self.use_button)
        self.hud_buttons_form.add_widget(self.inventory_next_button)

        #Window.bind(on_motion=self.on_motion)  #TODO ?: formerly didn't work, but maybe failed since used Window. instead of self--see <https://kivy.org/docs/api-kivy.input.motionevent.html>

        Clock.schedule_interval(self.update_glsl, 1.0 / self.frames_per_second)

        self._touches = []

    def get_class_name(self):
        return "KivyGlopsWindow"

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
                print("[ KivyGlopsWindow ] ERROR in set_hud_image: could not find " + original_path)
        else:
            print("[ KivyGlopsWindow ] ERROR in set_hud_image: path is None")

    def set_primary_item_caption(self, name):
        self.use_button.text=name

    def get_keycode(self, key_name):
        try:
            return Keyboard.keycodes[key_name]
        except:
            # no keyboard attached
            pass
        return None

    def spawn_pex_particles(self, path, pos, radius=1.0, duration_seconds=None):
        if path is not None:
            if os.path.isfile(path):
                print("[ KivyGlopsWindow ] found '" + path + "'" + \
                      "  (not yet implemented)")
                #Range is 0 to 250px for size, so therefore translate to meters:
                # divide by 125 to get meters, then multiply by radius,
                # so that pex file can determine "extra" (>125)
                # or "reduced" (<125) size while retaining pixel-based sizing.
            else:
                print("[ KivyGlopsWindow ] missing '" + path + "'")
        else:
            print("[ KivyGlopsWindow ] ERROR in spawn_pex_particles: path is None")

    def inventory_prev_button_press(self, instance):
        event_dict = self.scene.player_glop.select_next_inventory_slot(False)
        self.scene.after_selected_item(event_dict)

    def inventory_use_button_press(self, instance):
        event_dict = self.scene.use_selected(self.scene.player_glop)

    def inventory_next_button_press(self, instance):
        event_dict = self.scene.player_glop.select_next_inventory_slot(True)
        self.scene.after_selected_item(event_dict)

    def get_view_angles_by_pos_rad(self, pos):
        global debug_dict  # from common.py
        x_angle = -math.pi + (float(pos[0])/float(self.width-1))*(2.0*math.pi)
        y_angle = -(math.pi/2.0) + (float(pos[1])/float(self.height-1))*(math.pi)
        if "camera_glop" not in debug_dict:
            debug_dict["camera_glop"] = {}
        if "View" not in debug_dict:
            debug_dict["View"] = {}
        debug_dict["View"]["NOTE"] = "should match camera_glop"
        debug_dict["View"]["mouse_pos"] = str(pos)
        debug_dict["View"]["size"] = str( (self.width, self.height) )
        debug_dict["View"]["pitch,yaw"] = str((int(math.degrees(x_angle)),
                                                    int(math.degrees(y_angle))))
        if self.screen_w_arc_theta is not None and self.screen_h_arc_theta is not None:
            debug_dict["View"]["field of view"] = \
                str((int(math.degrees(self.screen_w_arc_theta)),
                     int(math.degrees(self.screen_h_arc_theta))))
        else:
            if "field of view" in debug_dict["View"]:
                debug_dict["View"]["field of view"] = None
        self.update_debug_label()
        return x_angle, y_angle

    #def hide_glop(self, this_glop):
    #    self.scene.hide_glop(this_glop)

    #def show_glop(self, this_glop_index):
    #    self.scene.show_glop(this_glop_index)

    def add_glop(self, this_glop, set_visible_enable=None):
        participle="initializing"
        try:
            if this_glop.name is None:
                this_glop.name = str(uuid.uuid4())
                if get_verbose_enable():
                    print("[ KivyGlopsWindow ] WARNING in " + \
                          "add_glop: missing name so generated '" + \
                          this_glop.name + "'")
            if set_visible_enable is not None:
                this_glop.visible_enable = set_visible_enable
            #context = self._contexts
            #context = self.gl_widget.canvas
            #if self.scene.selected_glop_index is None:
            #    self.scene.selected_glop_index = this_glop_index
            #    self.scene.selected_glop = this_glop
            if self.scene.glops is None:
                self.scene.glops = []
            if self.scene.selected_glop_index is None or \
                self.scene.selected_glop_index < 0:
                self.scene.selected_glop_index = len(self.scene.glops)
                self.scene.selected_glop = this_glop
            this_glop.glop_index = len(self.scene.glops)
            self.scene.glops.append(this_glop)
            if self.scene.glops[this_glop.glop_index] is not this_glop:
                # then deal with multithreading paranoia:
                print("[ KivyGlopsWindow ] index was wrong, correcting...")
                this_glop.glop_index = None
                for i in range(len(self.scene.glops)):
                    if self.scene.glops[i] is this_glop:
                        self.scene.glops[i].glop_index = i
                        break
                if this_glop.glop_index is None:
                    print("                      ERROR: unable to correct index")
            #self.scene.glops[len(self.scene.glops)-1].glop_index = len(self.scene.glops) - 1
            #this_glop.glop_index = len(self.scene.glops) - 1

            self._contexts.add(this_glop.get_context())  # _contexts is a visible instruction group
            if get_verbose_enable():
                print("[ KivyGlopsWindow ] Appended Glop (count:" + str(len(self.scene.glops)) + ").")
            if _multicontext_enable:
                if not this_glop._own_shader_enable:
                    this_glop.canvas.shader.source = self.gl_widget.canvas.shader.source
                #NOTE: projectionMatrix and modelViewMatrix don't exist yet if add_glop was called before first frame!
                #this_glop.set_uniform("projection_mat", self.scene.projectionMatrix)
                #this_glop.set_uniform("modelview_mat", self.scene.modelViewMatrix)
                this_glop.set_uniform("camera_world_pos", self.scene.camera_glop._t_ins.xyz)

        except:
            print("[ KivyGlopsWindow ] ERROR: Could not finish " + \
                  participle + " in KivyGlops load_obj")
            view_traceback()

    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)

    def finalize_canvas(self):
        self.gl_widget.canvas.add(PopMatrix())
        self.resetCallback = Callback(self.reset_gl_context)
        self.gl_widget.canvas.add(self.resetCallback)

    def update_glsl(self, *largs):
        actual_fps = None
        actual_frame_interval = None
        update_enable = False
        try:
            if self.scene._loaded_glops_enable:
                update_enable = True
        except:
            print("[ KivyGlopsWindow ] ERROR: Could not finish accessing scene. You must:")
            print("# Create your main program class like:")
            print("class MainScene(KivyGlops):")
            print("# Then create your scene like:")
            print("scene = MainScene(KivyGlopsWindow())")
            print("# You do not save the mainform class, scene does that, so")
            print("# hand over your scene to Kivy in your App's build method:")
            print("return scene.ui  # (not mainform)")
            sys.exit(1)
        if update_enable:
            if self.scene._loaded_glops_enable:
                if self._fps_last_frame_tick is not None:
                    #NOTE: best_timer() is a second
                    actual_frame_interval = best_timer() - self._fps_last_frame_tick
                    self._fps_accumulated_time += actual_frame_interval
                    self._fps_accumulated_count += 1
                    if self._fps_accumulated_time > .5:
                        self._average_fps = 1.0 / (self._fps_accumulated_time/float(self._fps_accumulated_count))
                        self._fps_accumulated_time = 0.0
                        self._fps_accumulated_count = 0
                    if actual_frame_interval > 0.0:
                        actual_fps = 1.0 / actual_frame_interval
                self._fps_last_frame_tick = best_timer()
                if not self.scene._visual_debug_enable:
                    self.debug_label.opacity = 0.0
                else:
                    self.debug_label.opacity = 1.0

                if self.scene.env_rectangle is not None:
                    if self.screen_w_arc_theta is not None and self.screen_h_arc_theta is not None:
                        #then calculate environment mapping variables
                        #region old way (does not repeat)
                        #env_h_ratio = (2 * math.pi) / self.screen_h_arc_theta
                        #env_w_ratio = env_h_ratio * math.pi
                        #self.scene.env_rectangle.size = (Window.size[0]*env_w_ratio,
                                                   #Window.size[1]*env_h_ratio)
                        #self.scene.env_rectangle.pos = (-(self.camera_glop._r_ins_y.angle/(2*math.pi)*self.scene.env_rectangle.size[0]),
                                                  #-(self.camera_glop._r_ins_x.angle/(2*math.pi)*self.scene.env_rectangle.size[1]))
                        #engregion old way (does not repeat)
                        self.scene.env_rectangle.size = Window.size
                        self.scene.env_rectangle.pos = 0.0, 0.0
                        view_right = self.screen_w_arc_theta / 2.0 + self.scene.camera_glop._r_ins_y.angle
                        view_left = view_right - self.screen_w_arc_theta
                        view_top = self.screen_h_arc_theta / 2.0 + self.scene.camera_glop._r_ins_x.angle # + math.radians(90.0)
                        view_bottom = view_top - self.screen_h_arc_theta
                        circle_theta = 2*math.pi
                        view_right_ratio = view_right / circle_theta
                        view_left_ratio = view_left / circle_theta
                        view_top_ratio = view_top / circle_theta
                        view_bottom_ratio = view_bottom / circle_theta
                        #tex_coords order: u,      v,      u + w,  v,
                        #                  u + w,  v + h,  u,      v + h
                        # as per https://kivy.org/planet/2014/02/using-tex_coords-in-kivy-for-fun-and-profit/
                        self.scene.env_rectangle.tex_coords = view_left_ratio, view_bottom_ratio, view_right_ratio, view_bottom_ratio, \
                                                        view_right_ratio, view_top_ratio, view_left_ratio, view_top_ratio

                x_rad, y_rad = self.get_view_angles_by_pos_rad(Window.mouse_pos)
                self.scene.player_glop._r_ins_y.angle = x_rad
                self.scene.player_glop._r_ins_x.angle = y_rad
                if "camera_glop" not in debug_dict:
                    debug_dict["camera_glop"] = dict()
                if "View" not in debug_dict:
                    debug_dict["View"] = dict()

                debug_dict["View"]["camera xyz: "] = fixed_width(self.scene.camera_glop._t_ins.xyz, 4, " ")
                if self._average_fps is not None:
                    debug_dict["View"]["fps"] = str(self._average_fps)
                #global debug_dict
                #if "player_glop" not in debug_dict:
                #    debug_dict["player_glop"] = {}
                #debug_dict["player_glop"]["_r_ins_x.angle"] = str(_r_ins_x.angle)
                #debug_dict["player_glop"]["_r_ins_y.angle"] = str(_r_ins_y.angle)
                #debug_dict["player_glop"]["_r_ins_z.angle"] = str(_r_ins_z.angle)
                #self.ui.update_debug_label()

                self.hud_form.pos = 0.0, 0.0
                self.hud_form.size = Window.size
                if self.hud_bg_rect is not None:
                    self.hud_bg_rect.size = self.hud_form.size
                    self.hud_bg_rect.pos=self.hud_form.pos

                self.scene.update()

                #forcibly use parent info (should not be needed if use_parent_projection use_parent_modelview use_parent_frag_modelview options of RenderContext constructor for canvas of children)
                #for i in range(len(self.scene.glops)):
                    #this_glop = self.scene.glops[i]
                    #this_glop.set_uniform("modelview_mat", self.scene.modelViewMatrix)
                    #this_glop.set_uniform("camera_world_pos", self.scene.camera_glop._t_ins.xyz)
            #else not loaded yet so don't try to use gl_widget or glops
        if not self.scene._loaded_glops_enable:
            self.debug_label.opacity = 1.0
            self.scene._load_glops_enable = False
            self.debug_label.text = "Welcome to KivyGlops\n" + \
                                    "Controls:\n" + \
                                    "* F3: debug screen\n\n" + \
                                    "\n" + \
                                    "busy loading glops...\n"
            if not self.scene._loading_glops_enable:
                self.scene._loading_glops_enable = True
                Clock.schedule_once(self._deferred_load_glops, 0.)

    def _deferred_load_glops(self, dt):
        if get_verbose_enable():
            print("_deferred_load_glops: " + str(type(dt)) + \
                  " dt = " + str(dt))
        self.scene.on_load_glops()  # also moved from ui
        self.scene._loaded_glops_enable = True
        self.debug_label.text = ""



    #def get_view_angles_by_touch_deg(self, touch):
    #    # formerly define_rotate_angle(self, touch):
    #    x_angle = (touch.dx/self.width)*360
    #    y_angle = -1*(touch.dy/self.height)*360
    #    return x_angle, y_angle

    #def get_view_angles_by_pos_deg(self, pos):
    #    x_angle = (pos[0]/self.width)*360
    #    y_angle = -1*(pos[1]/self.height)*360
    #    return x_angle, y_angle

    def toggle_visual_debug(self):
        if not self.scene._visual_debug_enable:
            self.scene._visual_debug_enable = True
            self.debug_label.opacity = 1.0
            #self._contexts.clear()
            for this_glop in self.scene.glops:
                if this_glop._axes_mesh is not None:
                    this_glop.prepare_canvas([this_glop._axes_mesh], axes_index=0)
                    context = this_glop.get_context()
                    this_glop.set_uniform("texture0_enable", False)
                else:
                    print("[ KivyGlopsWindow ] ERROR: no _axes_mesh" + \
                          " for glop '" + str(this_glop.name) + "'")
            print("[ KivyGlopsWindow ] set _visual_debug_enable: True")
        else:
            self.scene._visual_debug_enable = False
            self.debug_label.opacity = 0.0
            #self._contexts.clear()
            for this_glop in self.scene.glops:
                this_glop.prepare_canvas([this_glop._mesh])
                if this_glop._mesh is not None:
                    if this_glop._mesh.texture is not None:
                        this_glop.set_uniform("texture0_enable", True)
                else:
                    #doesn't actually matter
                    if get_verbose_enable():
                        if this_glop.show_next_no_mesh_warning_enable:
                            this_glop.show_next_no_mesh_warning_enable = False
                            print("[ " + str(type(self)) + " ] WARNING: _mesh is None for " + str(this_glop.name))
            print("[ KivyGlopsWindow ] set _visual_debug_enable: False")

    def set_debug_label(self, text):
        self.debug_label.text = text

    def suspend_debug_label_update(self, enable):
        if enable:
            if self.debug_label_suspended_level < 0:
                print("[ KivyGlopsWindow ] WARNING: "
                      "self.debug_label_suspended_level was " + \
                      str(self.debug_label_suspended_level) + \
                      "so forcing to 0")
                self.debug_label_suspended_level = 0
            self.debug_label_suspended_level += 1
        else:
            self.debug_label_suspended_level -= 1

    def update_debug_label(self):
        if self.debug_label_suspended_level <= 0:
            yaml = ""
            indent = ""
            for key in debug_dict.keys():
                yaml += indent + key + ":\n"
                yaml = push_yaml_text(yaml, key, debug_dict[key], indent)
                #if debug_dict[key] is None:
                #    self.debug_label.text = key + ": None"
                #elif type(debug_dict[key]) is dict:
            self.debug_label.text = yaml

    #     def canvasTouchDown(self, touch, *largs):
    #         touchX, touchY = largs[0].pos
    #         #self.player_glop.targetX = touchX
    #         #self.player_glop.targetY = touchY
    #         print("\n")
    #         print(str(largs).replace("\" ", "\"\n"))

    def on_touch_down(self, touch):
        super(KivyGlopsWindow, self).on_touch_down(touch)
        #touch.grab(self)
        #self._touches.append(touch)

#         thisTouch = MouseMotionEvent(touch)
#         thisTouch.
        if touch.is_mouse_scrolling:
            event_dict = None
            if touch.button == "scrolldown":
                event_dict = self.scene.player_glop.select_next_inventory_slot(True)
            else:
                event_dict = self.scene.player_glop.select_next_inventory_slot(False)
            self.scene.after_selected_item(event_dict)
        else:
            if get_verbose_enable():
                print("[ KivyGlopsWindow ] (verbose message) touch down")
            event_dict = self.scene.use_selected(self.scene.player_glop)

    def on_touch_up(self, touch):
        super(KivyGlopsWindow, self).on_touch_up(touch)
        #touch.ungrab(self)
        #self._touches.remove(touch)
        #self.scene.player1_controller.dump()

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
#         print('The key' + str(keycode) + ' pressed')
#         print(' - text is ' + text)
#         print(' - modifiers are ' + str(modifiers))

        #print("pressed keycode " + str(keycode[0]) + " (should match keycode constant: " + str(Keyboard.keycodes[keycode[1]]) + ")")

        #if len(keycode[1])>0:
        self.scene.player1_controller.set_pressed(keycode[0], keycode[1], True)

        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if keycode[1] == 'escape':
            pass  #keyboard.release()
        # elif keycode[1] == 'w':
        #     self.scene.player_glop._t_ins.z += self.land_units_per_frame
        # elif keycode[1] == 's':
        #     self.scene.player_glop._t_ins.z -= self.land_units_per_frame
        # elif text == 'a':
        #     self.scene.player1_controller["left"] = True
        #     self.choice_try_vel_multiplier[0] = -1.0
        # elif text == 'd':
        #     self.choice_try_vel_multiplier[0] = 1.0
        #     self.scene.player1_controller["right"] = True
#         elif keycode[1] == '.':
#             self.look_at_center()
#         elif keycode[1] == 'numpadadd':
#             pass
#         elif keycode[1] == 'numpadsubtract' or keycode[1] == 'numpadsubstract':  #since is mispelled as numpadsubstract in kivy
#             pass
        elif keycode[1] == "tab":
            self.scene.select_mesh_at(self.scene.selected_glop_index+1)
            #if get_verbose_enable():
            this_name = None
            if self.scene.selected_glop_index is not None:
                this_name = "[" + str(self.scene.selected_glop_index) + "]"
            if self.scene.selected_glop is not None and self.scene.selected_glop.name is not None:
                this_name = self.scene.selected_glop.name
            if this_name is not None:
                print('[ KivyGlopsWindow ] Selected glop: ' + this_name)
            else:
                print('[ KivyGlopsWindow ] Select glop failed (maybe there are no glops loaded.')
        elif keycode[1] == "x":
            event_dict = self.scene.player_glop.select_next_inventory_slot(True)
            self.scene.after_selected_item(event_dict)
        elif keycode[1] == "z":
            event_dict = self.scene.player_glop.select_next_inventory_slot(False)
            self.scene.after_selected_item(event_dict)
        elif keycode[1] == "f3":
            self.toggle_visual_debug()
        # else:
        #     print('Pressed unused key: ' + str(keycode) + "; text:"+text)
        self.scene.update_view_visual_debug()

        #if get_verbose_enable():
            #print("[ KivyGlopsWindow ] scene.camera_glop._r_ins_y.angle: " + str(self.scene.camera_glop._r_ins_y.angle))
            #print("[ KivyGlopsWindow ] modelview_mat: " + str(self.gl_widget.canvas['modelview_mat']))
        #self.update_glsl()
        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

    def _on_keyboard_up(self, keyboard, keycode):
        self.scene.player1_controller.set_pressed(keycode[0], keycode[1], False)
        #print('[ KivyGlopsWindow ] Released key ' + str(keycode))

    def _keyboard_closed(self):
        print('[ KivyGlopsWindow ] Keyboard disconnected!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    #def on_motion(self, etype, motionevent):
        #print("[ KivyGlopsWindow ] coords:" + str(motionevent.dx) + "," + str(motionevent.dx))
        # will receive all motion events.
        #pass

    def on_touch_move(self, touch):
        #print("[ KivyGlopsWindow ] touch.dx:" + str(touch.dx) + " touch.dy:" + str(touch.dx))
        pass
#         print ("[ KivyGlopsWindow ] on_touch_move")
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
#                 self.camera_walk_units_per_frame = self.camera_walk_units_per_second / self.frames_per_second
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
#                     self.scene.camera_glop._t_ins.z += scale
#                     print(str(scale) + " " + (self.scene.camera_glop._t_ins.x, self.scene.camera_glop._t_ins.y, self.scene.camera_glop._t_ins.z) )
#             self.update_glsl()

