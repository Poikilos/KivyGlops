'''
This does 3D stuff with Kivy without using glops, for testing purposes.
This may not work on any given release or commit.
'''
import sys
import traceback
import math

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.window import Keyboard
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import *
from kivy.graphics import *
from kivy.factory import Factory


no_width_error_enable = True

#region globals pasted from PyGlops
#from kivyops import *
V_POS_INDEX = 0
V_TC0_INDEX = 1
V_TC1_INDEX = 2
V_DIFFUSE_INDEX = 3
V_NORMAL_INDEX = 4
#see also pyopsmesh.vertex_depth below

#indices of tuples inside vertex_format (see PyGlop)
VFORMAT_NAME_INDEX = 0
VFORMAT_VECTOR_LEN_INDEX = 1
VFORMAT_TYPE_INDEX = 2

def normalize_3d_by_ref(this_vec3):
    #see <https://stackoverflow.com/questions/23303598/3d-vector-normalization-issue#23303817>
    length = math.sqrt(this_vec3[0] * this_vec3[0] + this_vec3[1] * this_vec3[1] + this_vec3[2] * this_vec3[2])
    if length > 0:
        this_vec3[0] /= length
        this_vec3[1] /= length
        this_vec3[2] /= length
    else:
        this_vec3[1] = 1.0  # give some kind of normal for 0,0,0

#endregion globals pasted from PyGlops


#class GLWidget(Widget):
#    pass

#class HudForm(BoxLayout):
#    pass

#class ContainerForm(BoxLayout):
#    pass

class Testing3DWidget(Widget):
    def __init__(self):
        
        #name must be bytestring (must be specified if using python3, since default string is unicode in python3)
        self.vertex_format = [(b'a_position', 4, 'float'),  # Munshi prefers vec4 (Kivy prefers vec3)
                              (b'a_texcoord0', 4, 'float'),  # Munshi prefers vec4 (Kivy prefers vec2); vTexCoord0; available if enable_tex[0] is true
                              (b'a_texcoord1', 4, 'float'),  # Munshi prefers vec4 (Kivy prefers vec2);  available if enable_tex[1] is true
                              (b'a_color', 4, 'float'),  # vColor (diffuse color of vertex)
                              (b'a_normal', 3, 'float')  # vNormal; Munshi prefers vec3 (Kivy also prefers vec3)
                              ]
        self.on_vertex_format_change()
        
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
        self._color_instruction = Color(1.0, 0.0, 1.0, 1.0)  # TODO: eliminate this in favor of canvas["mat_diffuse_color"]
        
        #_axes_vertices, _axes_indices = self.generate_plane()
        _axes_vertices, _axes_indices = self.generate_axes()
        
        print("[ Testing3DWidget ] __init__ got " + str(len(_axes_vertices)/self.vertex_depth) + " verts, " + str(len(_axes_indices)/3) + " faces")
        self._axes_mesh = Mesh(
                               vertices=_axes_vertices,
                               indices=_axes_indices,
                               fmt=self.vertex_format,
                               mode='triangles',
                               #texture=None,
                              )

    def new_vertex(self, set_coords, set_color):
        # NOTE: assumes vertex format is ok (should be checked by generate_axes)
        # assumes normal should be point relative to 0,0,0
        vertex_components = [0.0]*self.vertex_depth
        if len(vertex_components) != self.vertex_depth:
            print("FATAL ERROR: vertex length " + str(len(vertex_components)) + "does not match vertex depth " + str(len(self.vertex_depth)) + "")
            sys.exit(1)
        for i in range(0, 3):
            vertex_components[self._POSITION_OFFSET+i] = set_coords[i]
        if set_color is not None:
            for i in range(0, len(set_color)):
                vertex_components[self.COLOR_OFFSET+i] = set_color[i]
        normals = [0.0]*3;
        for i in range(0, 3):
            normals[i] = set_coords[i]
        normalize_3d_by_ref(normals)
        for i in range(0, 3):
            vertex_components[self._NORMAL_OFFSET+i] = normals[i]
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

        offset = 0
        white = (1.0, 1.0, 1.0, 1.0)
        self.append_vertex(_axes_vertices, (0.0, 0.0, 0.0), white)
        self.append_vertex(_axes_vertices, (0.0, 1.0, 0.0), white)
        self.append_vertex(_axes_vertices, (1.0, 0.0, 0.0), white)
        self.append_vertex(_axes_vertices, (1.0, 1.0, 0.0), white)
        _axes_indices.extend([0,1,3, 0,2,3])
        
        return _axes_vertices, _axes_indices
        
        
    def generate_axes(self):
        # NOTE: This is a full solid (3 boxes) where all axes can always
        # be seen except when another is in the way (some vertices are
        # doubled so that vertex color can be used).
        _axes_vertices = []
        _axes_indices = []
        
        IS_SELF_VFORMAT_OK = True
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

        offset = 0
        red = (1.0, 0.0, 0.0, 1.0)
        green = (0.0, 1.0, 0.0, 1.0)
        blue = (0.0, 0.0, 1.0, 1.0)
        self.append_vertex(_axes_vertices, (0.0, 0.0, 0.0), green)  # 0
        self.append_vertex(_axes_vertices, (0.1, 0.0, 0.0), green)  # 1
        self.append_vertex(_axes_vertices, (0.0, 0.0, 0.1), green)  # 2
        self.append_vertex(_axes_vertices, (0.1, 0.0, 0.1), green)  # 3
        self.append_vertex(_axes_vertices, (0.0, 1.0, 0.0), green)  # 4
        self.append_vertex(_axes_vertices, (0.1, 1.0, 0.0), green)  # 5
        self.append_vertex(_axes_vertices, (0.0, 1.0, 0.1), green)  # 6
        self.append_vertex(_axes_vertices, (0.1, 1.0, 0.1), green)  # 7
        
        _axes_indices.extend([0,1,3, 0,2,3, 0,2,6, 0,4,6,  # bottom & right
                              0,4,5, 0,1,5, 4,5,7, 4,6,7,  # back & top
                              1,5,7, 1,3,7, 2,3,7, 2,6,7  # left & front
                              ])
        
        self.append_vertex(_axes_vertices, (0.1, 0.0, 0.0), red)  # 8
        self.append_vertex(_axes_vertices, (0.1, 0.0, 0.1), red)  # 9
        self.append_vertex(_axes_vertices, (0.1, 0.1, 0.0), red)  # 10
        self.append_vertex(_axes_vertices, (1.0, 0.1, 0.1), red)  # 11
        self.append_vertex(_axes_vertices, (1.0, 0.0, 0.0), red)  # 12
        self.append_vertex(_axes_vertices, (1.0, 0.1, 0.0), red)  # 13
        self.append_vertex(_axes_vertices, (1.0, 0.0, 0.1), red)  # 14
        self.append_vertex(_axes_vertices, (1.0, 0.1, 0.1), red)  # 15
        
        _axes_indices.extend([8,9,11, 8,10,11, 8,10,13, 8,12,13,  # back & outside
                              8,9,14, 8,12,14,  9,14,15, 9,11,15,  # bottom & inside
                              11,10,13, 11,15,13, 12,13,15, 12,14,15  # top & front
                              ])
        
        self.append_vertex(_axes_vertices, (0.0, 0.0, 0.1), blue)  # 16
        self.append_vertex(_axes_vertices, (0.1, 0.0, 0.1), blue)  # 17
        self.append_vertex(_axes_vertices, (0.0, 0.1, 0.1), blue)  # 18
        self.append_vertex(_axes_vertices, (1.0, 0.1, 0.1), blue)  # 19
        self.append_vertex(_axes_vertices, (0.0, 0.0, 1.0), blue)  # 20
        self.append_vertex(_axes_vertices, (0.1, 0.0, 1.0), blue)  # 21
        self.append_vertex(_axes_vertices, (0.0, 0.1, 1.0), blue)  # 22
        self.append_vertex(_axes_vertices, (0.1, 0.1, 1.0), blue)  # 23
        
        _axes_indices.extend([16,17,19, 16,18,19, 16,18,22, 16,20,22,  # back & outside
                              16,17,21, 16,20,21, 16,18,22, 16,20,22,  # bottom & inside
                              19,18,22, 19,23,22, 20,21,23, 20,22,23  # top & front
                              ])
        
        #new_texcoord = new_tuple(self.vertex_format[self.TEXCOORD0_INDEX][VFORMAT_VECTOR_LEN_INDEX])
        
        return _axes_vertices, _axes_indices

    def on_vertex_format_change(self):
        self.vertex_depth = 0
        for i in range(0,len(self.vertex_format)):
            self.vertex_depth += self.vertex_format[i][VFORMAT_VECTOR_LEN_INDEX]
        
        self._POSITION_OFFSET = -1
        self._NORMAL_OFFSET = -1
        self._TEXCOORD0_OFFSET = -1
        self._TEXCOORD1_OFFSET = -1
        self.COLOR_OFFSET = -1

        self.POSITION_INDEX = -1
        self.NORMAL_INDEX = -1
        self.TEXCOORD0_INDEX = -1
        self.TEXCOORD1_INDEX = -1
        self.COLOR_INDEX = -1

        #this_pyglop.vertex_depth = 0
        offset = 0
        temp_vertex = list()
        for i in range(0,len(self.vertex_format)):
            #first convert from bytestring to str
            vformat_name_lower = str(self.vertex_format[i][VFORMAT_NAME_INDEX]).lower()
            if "pos" in vformat_name_lower:
                self._POSITION_OFFSET = offset
                self.POSITION_INDEX = i
            elif "normal" in vformat_name_lower:
                self._NORMAL_OFFSET = offset
                self.NORMAL_INDEX = i
            elif ("texcoord" in vformat_name_lower) or ("tc0" in vformat_name_lower):
                if self._TEXCOORD0_OFFSET<0:
                    self._TEXCOORD0_OFFSET = offset
                    self.TEXCOORD0_INDEX = i
                elif self._TEXCOORD1_OFFSET<0 and ("tc0" not in vformat_name_lower):
                    self._TEXCOORD1_OFFSET = offset
                    self.TEXCOORD1_INDEX = i
                #else ignore since is probably the second index such as a_texcoord1
            elif "color" in vformat_name_lower:
                self.COLOR_OFFSET = offset
                self.COLOR_INDEX = i
            offset += self.vertex_format[i][VFORMAT_VECTOR_LEN_INDEX]
        if offset > self.vertex_depth:
            print("ERROR: The count of values in vertex format chunks (chunk_count:"+str(len(self.vertex_format))+"; value_count:"+str(offset)+") is greater than the vertex depth "+str(self.vertex_depth))
        elif offset != self.vertex_depth:
            print("WARNING: The count of values in vertex format chunks (chunk_count:"+str(len(self.vertex_format))+"; value_count:"+str(offset)+") does not total to vertex depth "+str(self.vertex_depth))
        participle = "(before initializing)"

    def get_context(self):
        return self.canvas


class TestingKivy3D(BoxLayout):
    scene = None
    ops = None
    this_op = None

    def __init__(self, **kwargs):
        self.player_velocity = [0.0, 0.0, 0.0]
        self.ops = []
        
        self.frames_per_second = 60.0
        self.gl_widget = Widget()
        self.hud_form = BoxLayout(orientation="vertical", size_hint=(1.0, 1.0))
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
            print("Could not finish loading keyboard" +
                  "(keyboard may not be present).")
            #view_traceback()
            ex_type, ex, tb = sys.exc_info()
            print(str(ex_type)+" "+str(ex)+": ")
            traceback.print_tb(tb)
            del tb
            print("")

        #self.bind(on_touch_down=self.canvasTouchDown)

        self.gl_widget.canvas = RenderContext(compute_normal_mat=True)
        self.gl_widget.canvas["_world_light_dir"] = (0.0, 0.5, 1.0)
        self.gl_widget.canvas["_world_light_dir_eye_space"] = (0.0, 0.5, 1.0) #rotated in update_glsl
        self.gl_widget.canvas["camera_light_multiplier"] = (1.0, 1.0, 1.0, 1.0)
        #self.gl_widget.canvas.shader.source = resource_find('simple1b.glsl')
        #self.gl_widget.canvas.shader.source = resource_find('shade-kivyops-standard.glsl')  # NOT working
        #self.gl_widget.canvas.shader.source = resource_find('shade-normal-only.glsl') #partially working
        #self.gl_widget.canvas.shader.source = resource_find('shade-texture-only.glsl')
        #self.gl_widget.canvas.shader.source = resource_find('shade-kivyops-minimal.glsl')  # NOT working

        
        #self.canvas.shader.source = resource_find('simple.glsl')
        #self.canvas.shader.source = resource_find('simple1b.glsl')
        #self.canvas.shader.source = resource_find('shade-kivyops-standard.glsl')
        #self.canvas.shader.source = resource_find('shade-normal-only.glsl')
        #self.canvas.shader.source = resource_find('shade-texture-only.glsl')
        #self.canvas.shader.source = resource_find('shade-kivyops-minimal.glsl')
        #self.canvas.shader.source = resource_find('fresnel.glsl')

        #self.gl_widget.canvas.shader.source = resource_find('simple1b.glsl')
        self.gl_widget.canvas.shader.source = resource_find('fresnel.glsl')

        #formerly, .obj was loaded here using load_obj (now calling program does that)

        #print(self.gl_widget.canvas.shader)  #just prints type and memory address
        super(TestingKivy3D, self).__init__(**kwargs)
        self.cb = Callback(self.setup_gl_context)
        self.gl_widget.canvas.add(self.cb)

        self.gl_widget.canvas.add(PushMatrix())

        self._meshes = InstructionGroup() #RenderContext(compute_normal_mat=True)
        self.gl_widget.canvas.add(self._meshes)

        self.finalize_canvas()
        self.add_widget(self.gl_widget)
        #self.hud_form.rows = 1
        self.add_widget(self.hud_form)
        
        self.debug_label = Factory.Label(text="...")
        self.hud_form.add_widget(self.debug_label)
        self.hud_form.add_widget(self.hud_buttons_form)
        #self.inventory_prev_button = Factory.Button(text="<", id="inventory_prev_button", size_hint=(.2,1.0), on_press=self.inventory_prev_button_press)
        self.use_button = Factory.Button(text="0: Empty", id="use_button", size_hint=(.2,1.0), on_press=self.inventory_use_button_press)
        #self.inventory_next_button = Factory.Button(text=">", id="inventory_next_button", size_hint=(.2,1.0), on_press=self.inventory_next_button_press)
        #self.hud_buttons_form.add_widget(self.inventory_prev_button)
        self.hud_buttons_form.add_widget(self.use_button)
        #self.hud_buttons_form.add_widget(self.inventory_next_button)

        #Window.bind(on_motion=self.on_motion)  #TODO ?: formerly didn't work, but maybe failed since used Window. instead of self--see <https://kivy.org/docs/api-kivy.input.motionevent.html>
        
        Clock.schedule_interval(self.update_glsl, 1.0 / self.frames_per_second)
        
        #self._touches = []
        
        #self.scene = KivyGlops()
        #self.scene = ObjFile(resource_find("monkey.obj"))
        #self.scene.load_obj(resource_find("barrels triangulated (Costinus at turbosquid).obj"))
        #self.scene.load_obj(resource_find("barrel.obj"))
        #self.scene.load_obj(resource_find("KivyGlopsDemoScene.obj"))
        #self.scene.load_obj("testnurbs-all-textured.obj")

        self.this_op = Testing3DWidget()
        #with self.canvas:
        #    self.cb = Callback(self.setup_gl_context)
        #    PushMatrix()
        #    self.setup_scene()
        #    PopMatrix()
        #    self.cb = Callback(self.reset_gl_context)
        self.add_op(self.this_op)
        
        self.camera_translate_instruction = Translate()
        self.camera_translate_instruction.x = -1.0
        self.look_point = [0, 0, 0]
        self.rot = Rotate(1, 0, 1, 0)
        
        Clock.schedule_interval(self.update_glsl, 1 / 60.)
        
    def add_op(self, this_op):
        this_glop = this_op
        context = this_glop.get_context()
        #region pasted from KivyGlops add_glop
        this_glop._pushmatrix = PushMatrix()
        this_glop._updatenormalmatrix = UpdateNormalMatrix()
        this_glop._popmatrix = PopMatrix()

        context.add(this_glop._pushmatrix)
        context.add(this_glop._translate_instruction)
        context.add(this_glop._rotate_instruction_x)
        context.add(this_glop._rotate_instruction_y)
        context.add(this_glop._rotate_instruction_z)
        context.add(this_glop._scale_instruction)
        context.add(this_glop._updatenormalmatrix)
        #context.add(this_glop._color_instruction)  #TODO: asdf add as uniform instead
        #not needed for Testing3DWidget since _axes_mesh is already a Mesh of axes
        #if this_glop._mesh is None:
        #    this_glop.generate_kivy_mesh()
        #    print("WARNING: glop had no mesh, so was generated when added to render context. Please ensure it is a KivyGlop and not a PyGlop (however, vertex indices misread could also lead to missing Mesh object).")
        #print("_color_instruction.r,.g,.b,.a: "+str( [this_glop._color_instruction.r, this_glop._color_instruction.g, this_glop._color_instruction.b, this_glop._color_instruction.a] ))
        #print("u_color: "+str(this_glop.material.diffuse_color))
        if this_glop._axes_mesh is not None:
            context.add(this_glop._axes_mesh)  # debug only unless in testingkivy3d.py
        #if this_glop._mesh is not None:
            #context.add(this_glop._mesh)  # commented for debug only unless in testingkivy3d.py
        #    if get_verbose_enable():
        #        print("Added mesh to render context.")
        #else:
        #    print("NOT adding mesh.")
        context.add(this_glop._popmatrix)
        #if self.scene.glops is None:
        #    self.scene.glops = list()
        #endregion pasted from KivyGlops add_glop
        
        #self._meshes.add(this_glop.get_context())  # really just self.this_op.canvas (in testingkivy3d.py)
        try:
            #self._meshes.add(this_glop.canvas)
            self._meshes.add(context)
            pass
        except:
            print("[ TestingKivy3D ] add_op could not finish adding instructiongroup")
            #view_traceback()
            ex_type, ex, tb = sys.exc_info()
            print(str(ex_type)+" "+str(ex)+": ")
            traceback.print_tb(tb)
            del tb
            print("")
            
        #self._meshes.remove(this_glop.get_context()) #  to hide
        
    def inventory_use_button_press(self, instance):
        print("Pressed button " + instance.text)

    def finalize_canvas(self):
        self.gl_widget.canvas.add(PopMatrix())

        self.resetCallback = Callback(self.reset_gl_context)
        self.gl_widget.canvas.add(self.resetCallback)

    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)

    
    def update_glsl(self, *largs):
        global no_width_error_enable
        if self.player_velocity[0] != 0:
            self.camera_translate_instruction.x += self.player_velocity[0]
        if self.player_velocity[1] != 0:
            self.camera_translate_instruction.y += self.player_velocity[1]
        if self.player_velocity[2] != 0:
            self.camera_translate_instruction.z += self.player_velocity[2]
        if self.height > 0:
            asp = self.width / float(self.height)
        else:
            if no_width_error_enable:
                print("[ TestingKivy3D ] ERROR in update_glsl: Failed to get width.")
                no_width_error_enable = False
                
        clip_top = 0.06  #NOTE: 0.03 is ~1.72 degrees, if that matters
        # formerly field_of_view_factor
        # was changed to .03 when projection_near was changed from 1 to .1
        # was .3 when projection_near was 1

        clip_right = asp*clip_top  # formerly overwrote asp
        self.projection_near = 0.1
        proj = Matrix().view_clip(-clip_right, clip_right, -1*clip_top, clip_top, self.projection_near, 100, 1)  # last params: far, perspective
        #proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 100, 1) last params: far, perspective
        modelViewMatrix = Matrix()
        modelViewMatrix.translate(self.camera_translate_instruction.x, self.camera_translate_instruction.y, self.camera_translate_instruction.z)
        if (self.camera_translate_instruction.x != self.look_point[0] or
            self.camera_translate_instruction.y != self.look_point[1] or
            self.camera_translate_instruction.z != self.look_point[2]):
            try:
                modelViewMatrix = modelViewMatrix.look_at(self.camera_translate_instruction.x, self.camera_translate_instruction.y, self.camera_translate_instruction.z, self.look_point[0], self.look_point[1], self.look_point[2], 0, 1, 0)  # 0,1,0 is y-up orientation
            except:
                print("[ TestingKivy3D ] Could not finish modelViewMatrix.look_at:")
        else:
            print("[ TestingKivy3D ] Can't run modelViewMatrix.look_at since camera is at look_point")
                
        self.gl_widget.canvas['projection_mat'] = proj
        self.gl_widget.canvas['modelview_mat'] = modelViewMatrix
        self.gl_widget.canvas["camera_world_pos"] = [self.camera_translate_instruction.x, self.camera_translate_instruction.y, self.camera_translate_instruction.z]
        self.gl_widget.canvas['ambient_light'] = (0.1, 0.1, 0.1)
        
        #self.canvas['projection_mat'] = proj
        #self.canvas['diffuse_light'] = (1.0, 1.0, 0.8)
        #self.canvas['ambient_light'] = (0.1, 0.1, 0.1)
        self.rot.angle += 1

    def dump_pyglop(self, m):
        this_list = list()
        m.append_dump(this_list, "")
        dump_path = m.name+".pyglop"
        outs = open(dump_path, 'w')
        for line in this_list:
            outs.write(line+"\n")
        outs.close()
        print("dumped object to '"+dump_path+"'")

    # def setup_scene(self):
        # Color(1, 1, 1, 1)
        # PushMatrix()
        # Translate(0, 0, -3)
        # self.rot = Rotate(1, 0, 1, 0)
        # #for i in range(0,len(self.scene)):
        # #    self.scene.ops[i].append_dump(thisList, tabString)
        # #m = list(self.scene.objects.values())[0]
        # m = self.scene.ops[0]
        # #self.dump_pyglop(m)

        # UpdateNormalMatrix()
        # self.mesh = Mesh(
            # vertices=m.vertices,
            # indices=m.indices,
            # fmt=m.vertex_format,
            # mode='triangles',
        # )
        # PopMatrix()

    def _on_keyboard_up(self, keyboard, keycode):
        #self.scene.player1_controller.set_pressed(keycode[0], keycode[1], False)
        #print('Released key ' + str(keycode))
        self.player_velocity[0] = 0.0
        self.player_velocity[1] = 0.0
        self.player_velocity[2] = 0.0
        pass

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'delete':
            print("Pressed delete.")
            pass  #keyboard.release()
        elif keycode[1] == 'a':
            self.player_velocity[0] = -1.0
        elif keycode[1] == 'd':
            self.player_velocity[0] = 1.0
        elif keycode[1] == 'w':
            self.player_velocity[1] = -1.0
        elif keycode[1] == 's':
            self.player_velocity[1] = 1.0
            
        self.update_glsl()
        return True

    def _keyboard_closed(self):
        print('Keyboard disconnected!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

class TestingKivy3DApp(App):
    def build(self):
        return TestingKivy3D()

if __name__ == "__main__":
    TestingKivy3DApp().run()
