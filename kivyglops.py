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

from kivy.logger import Logger
from kivy.vector import Vector
from common import *

#TODO: try adding captions and 2d axis indicators in canvas.after, or try RenderContext
sub_canvas_enable = False


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

    def translate_x_relative(self, distance):
        self._translate_instruction.x += distance

    def translate_y_relative(self, distance):
        self._translate_instruction.y += distance

    def translate_z_relative(self, distance):
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

    def generate_kivy_mesh(self):
        participle = "checking for texture"
        self.last_loaded_path = self.get_texture_diffuse_path()
        this_texture_image = None
        if self.last_loaded_path is not None:
            participle = "getting image filename"
            try:
                participle = "loading "+self.last_loaded_path
                this_texture_image = Image(self.last_loaded_path)
                print("Loaded texture '"+self.last_loaded_path+"'")
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
        participle = "assembling kivy Mesh"
        this_texture = None
        if len(self.vertices)>0:
            if (this_texture_image is not None):
                this_texture = this_texture_image.texture

            self._mesh = Mesh(
                    vertices=self.vertices,
                    indices=self.indices,
                    fmt=self.vertex_format,
                    mode='triangles',
                    texture=this_texture,
                )
            print(str(len(self.vertices))+" vert(ex/ices)")

        else:
            print("WARNING: 0 vertices in glop")
            if self.name is not None:
                print("  named "+self.name)


class KivyGlops(PyGlops):

    def __init__(self):
        super(KivyGlops, self).__init__()
        self.camera_glop = get_kivyglop_from_pyglop(self.camera_glop)

    def create_mesh(self):
        #return PyGlops.create_mesh(self)
        return KivyGlop()

    def create_material(self):
        return KivyGlopsMaterial()


class KivyGlopsWindow(Widget):
    IsVisualDebugMode = False
    scene = None
    frames_per_second = 60.0
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

    def load_glops(self):
        print("Warning: you should subclass KivyGlopsWindow and implement load_glops (and usually update_glops for changing objects each frame)")

    def update_glops(self):
        pass


    def __init__(self, **kwargs):
        self.world_boundary_min = [None,None,None]
        self.world_boundary_max = [None,None,None]
        self.camera_walk_units_per_second = 12.0
        self.camera_turn_radians_per_second = math.radians(90.0)
        self.mode = MODE_EDIT
        self.player1_controller = PyRealTimeController()
        self.controllers.append(self.player1_controller)
        self.focal_distance = 2.0
        self.projection_near = 0.1
        try:
            self._keyboard = Window.request_keyboard(
                self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
            self._keyboard.bind(on_key_up=self._on_keyboard_up)
        except:
            print("Could not finish loading keyboard (keyboard may not be present).")

        #self.bind(on_touch_down=self.canvasTouchDown)

        self.scene = KivyGlops()
        self.canvas = RenderContext(compute_normal_mat=True)
        self.canvas["_world_light_dir"] = (0.0, 0.5, 1.0)
        self.canvas["_world_light_dir_eye_space"] = (0.0, 0.5, 1.0) #rotated in update_glsl
        self.canvas["camera_light_multiplier"] = (1.0, 1.0, 1.0, 1.0)
        #self.canvas.shader.source = resource_find('simple1b.glsl')
        #self.canvas.shader.source = resource_find('shade-kivyglops-standard.glsl')  # NOT working
        #self.canvas.shader.source = resource_find('shade-normal-only.glsl') #partially working
        #self.canvas.shader.source = resource_find('shade-texture-only.glsl')
        #self.canvas.shader.source = resource_find('shade-kivyglops-minimal.glsl')  # NOT working
        self.canvas.shader.source = resource_find('fresnel.glsl')

        #formerly, .obj was loaded here using load_obj (now calling program does that)

        #print(self.canvas.shader)  #just prints type and memory address
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
        self.canvas.add(self.cb)

        self.canvas.add(PushMatrix())

        #self.canvas.add(PushMatrix())
        #self.canvas.add(this_texture)
        #self.canvas.add(Color(1, 1, 1, 1))
        #for this_glop_index in range(0,len(self.scene.glops)):
        #    this_mesh_name = ""
        #    #thisMesh = KivyGlop()
        #    this_glop = self.scene.glops[this_glop_index]
        #    add_glop(this_glop)
        #self.canvas.add(PopMatrix())
        self._meshes = InstructionGroup() #RenderContext(compute_normal_mat=True)
        self.canvas.add(self._meshes)

        self.finalize_scene()
        self.camera_translate = [0, self.scene.camera_glop.eye_height, 25] #x,y,z where y is up
        #This is done axis by axis--the only reason is so that you can do OpenGL 6 (boundary detection) lesson from expertmultimedia.com starting with this file
        if self.world_boundary_min[0] is not None:
            if self.camera_translate[0] < self.world_boundary_min[0]:
                self.camera_translate[0] = self.world_boundary_min[0]
        if self.world_boundary_min[1] is not None:
            if self.camera_translate[1] < self.world_boundary_min[1]: #this is done only for this axis, just so that you can do OpenGL 6 lesson using this file (boundary detection)
                self.camera_translate[1] = self.world_boundary_min[1]
        if self.world_boundary_min[2] is not None:
            if self.camera_translate[2] < self.world_boundary_min[2]: #this is done only for this axis, just so that you can do OpenGL 6 lesson using this file (boundary detection)
                self.camera_translate[2] = self.world_boundary_min[2]
        self.camera_rotate_x = [0.0, 1.0, 0.0, 0.0]
        self.camera_rotate_y = [math.radians(-90.0), 0.0, 1.0, 0.0]
        self.camera_rotate_z = [0.0, 0.0, 0.0, 1.0]
        self.camera_ax = 0
        self.camera_ay = 0
        Clock.schedule_interval(self.update_glsl, 1.0 / self.frames_per_second)
        #Clock.schedule_once(self.update_glsl, 1.0)
        #Clock.schedule_once(self.update_glsl, 1.0)
        self.camera_walk_units_per_frame = self.camera_walk_units_per_second / self.frames_per_second
        self.camera_turn_radians_per_frame = self.camera_turn_radians_per_second / self.frames_per_second

        self._touches = []

        #fix incorrect keycodes in kivy 1.8.0:
        if (Keyboard.keycodes["-"]==41):
            Keyboard.keycodes["-"]=45
        if (Keyboard.keycodes["="]==43):
            Keyboard.keycodes["="]=61

        self.load_glops()

    def finalize_scene(self):
        self.canvas.add(PopMatrix())

        self.resetCallback = Callback(self.reset_gl_context)
        self.canvas.add(self.resetCallback)

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

    def is_in_any_walkmesh_xz(self, pt):
        result = False
        X_i = 0
        Y_i = 2  # actually z since ignoring y
        pt_2d = pt[X_i], pt[Y_i]
        for this_glop in self.scene._walkmeshes:
            X_i = this_glop._POSITION_OFFSET + 0
            Y_i = this_glop._POSITION_OFFSET + 2
            poly_side_count = 3
            poly_count = int(len(this_glop.indices)/poly_side_count)
            poly_offset = 0
            for poly_index in range(0,poly_count):
                if (  is_in_triangle( pt_2d, (this_glop.vertices[this_glop.indices[poly_offset]*this_glop.vertex_depth+X_i],this_glop.vertices[this_glop.indices[poly_offset]*this_glop.vertex_depth+Y_i]), (this_glop.vertices[this_glop.indices[poly_offset+1]*this_glop.vertex_depth+X_i],this_glop.vertices[this_glop.indices[poly_offset+1]*this_glop.vertex_depth+Y_i]), (this_glop.vertices[this_glop.indices[poly_offset+2]*this_glop.vertex_depth+X_i],this_glop.vertices[this_glop.indices[poly_offset+2]*this_glop.vertex_depth+Y_i]) )  ):
                    result = True
                    break
                poly_offset += poly_side_count
        return result

    def use_walkmesh(self, name, hide=True):
        result = False
        for this_glop in self.scene.glops:
            if this_glop.name == name:
                result = True
                if this_glop not in self.scene._walkmeshes:
                    self.scene._walkmeshes.append(this_glop)
                    self._meshes.remove(this_glop.get_context())
                break
        return result

    def get_similar_names(self, partial_name):
        results = None
        checked_count = 0
        if partial_name is not None and len(partial_name)>0:
            results = list()
            for this_glop in self.scene.glops:
                checked_count += 1
                print("checked "+this_glop.name.lower())
                if partial_name in this_glop.name.lower():
                    results.append(this_glop.name)
        print("checked "+str(checked_count))
        return results

    def load_obj(self,source_path, swapyz_enable=False, centered=False):
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
                            new_glops[index].generate_kivy_mesh()
                            self.add_glop(new_glops[index])
                            print("")
                            if (favorite_pivot_point is None):
                                favorite_pivot_point = new_glops[index]._pivot_point

                        if centered:
                            #TODO: apply pivot point instead (change vertices as if pivot point were 0,0,0) to ensure translate 0 is world 0; instead of:
                            #center it (use only one pivot point, so all objects in obj file remain aligned with each other):
                            for index in range(0,len(new_glops)):
                                new_glops[index].translate_x_relative(-1.0*favorite_pivot_point[0])
                                new_glops[index].translate_y_relative(-1.0*favorite_pivot_point[1])
                                new_glops[index].translate_z_relative(-1.0*favorite_pivot_point[2])
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
            #context = self.canvas
            #if self.selected_glop_index is None:
            #    self.selected_glop_index = this_glop_index
            #    self.selected_glop = this_glop
            self.selected_glop_index = len(self.scene.glops)
            self.selected_glop = this_glop
            context = this_glop.get_context()
            this_mesh_name = ""
            if this_glop.name is not None:
                this_mesh_name = this_glop.name
            this_glop._pushmatrix=PushMatrix()
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
            print("_color_instruction: "+str( (this_glop._color_instruction.r, this_glop._color_instruction.g, this_glop._color_instruction.b) ))
            print("u_color: "+str(this_glop.material.diffuse_color))

            context.add(this_glop._color_instruction)  #TODO: asdf add as uniform instead
            if this_glop._mesh is not None:
                context.add(this_glop._mesh)
                print("Added mesh to render context.")
            else:
                print("NOT adding mesh.")
            this_glop._popmatrix = PopMatrix()
            context.add(this_glop._popmatrix)
            if self.scene.glops is None:
                self.scene.glops = list()
            self.scene.glops.append(this_glop)

            self._meshes.add(context)

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
        self.rotate_view_relative_around_point(angle, axis_index, self.camera_translate[0], self.camera_translate[1], self.camera_translate[2])

    def rotate_view_relative_around_point(self, angle, axis_index, around_x, around_y, around_z):
        if axis_index == 0:  #x
            # += around_y * math.tan(angle)
            self.camera_rotate_x[0] += angle
            # origin_distance = math.sqrt(around_z*around_z + around_y*around_y)
            # self.camera_translate[2] += origin_distance * math.cos(-1*angle)
            # self.camera_translate[1] += origin_distance * math.sin(-1*angle)
        elif axis_index == 1:  #y
            self.camera_rotate_y[0] += angle
            # origin_distance = math.sqrt(around_x*around_x + around_z*around_z)
            # self.camera_translate[0] += origin_distance * math.cos(-1*angle)
            # self.camera_translate[2] += origin_distance * math.sin(-1*angle)
        else:  #z
            #self.camera_translate[2] += around_y * math.tan(angle)
            self.camera_rotate_z[0] += angle
            # origin_distance = math.sqrt(around_x*around_x + around_y*around_y)
            # self.camera_translate[0] += origin_distance * math.cos(-1*angle)
            # self.camera_translate[1] += origin_distance * math.sin(-1*angle)

    def axis_index_to_string(self,index):
        result = "unknown axis"
        if (index==0):
            result = "x"
        elif (index==1):
            result = "y"
        elif (index==2):
            result = "z"
        return result

    def update_glsl(self, *largs):
        self.update_glops()
        rotation_multiplier_y = 0.0  # 1.0 is maximum speed
        moving_x = 0.0  # 1.0 is maximum speed
        moving_z = 0.0  # 1.0 is maximum speed; NOTE: increased z should move object closer to viewer in right-handed coordinate system
        moving_theta = 0.0
        position_change = [0.0, 0.0, 0.0]
        # for keycode strings, see  http://kivy.org/docs/_modules/kivy/core/window.html
        if self.player1_controller.get_pressed(Keyboard.keycodes["a"]):
            if self.player1_controller.get_pressed(Keyboard.keycodes["shift"]):
                moving_x = 1.0
            else:
                rotation_multiplier_y = -1.0
        if self.player1_controller.get_pressed(Keyboard.keycodes["d"]):
            if self.player1_controller.get_pressed(Keyboard.keycodes["shift"]):
                moving_x = -1.0
            else:
                rotation_multiplier_y = 1.0
        if self.player1_controller.get_pressed(Keyboard.keycodes["w"]):
            moving_z = 1.0
        if self.player1_controller.get_pressed(Keyboard.keycodes["s"]):
            moving_z = -1.0

        if rotation_multiplier_y != 0.0:
            delta_y = self.camera_turn_radians_per_frame * rotation_multiplier_y
            self.camera_rotate_y[0] += delta_y
            #origin_distance = math.sqrt(self.camera_translate[0]*self.camera_translate[0] + self.camera_translate[2]*self.camera_translate[2])
            #self.camera_translate[0] -= origin_distance * math.cos(delta_y)
            #self.camera_translate[2] -= origin_distance * math.sin(delta_y)

        #xz coords of edges of 16x16 square are:
        # move in the direction you are facing
        moving_theta = 0.0
        if moving_x != 0.0 or moving_z != 0.0:
            #makes movement relative to rotation (which alaso limits speed when moving diagonally):
            moving_theta = theta_radians_from_rectangular(moving_x, moving_z)
            moving_r_multiplier = math.sqrt((moving_x*moving_x)+(moving_z*moving_z))
            if moving_r_multiplier > 1.0:
                moving_r_multiplier = 1.0  # Limited so that you can't move faster when moving diagonally


            #TODO: reprogram so adding math.radians(-90) is not needed (?)
            position_change[0] = self.camera_walk_units_per_frame*moving_r_multiplier * math.cos(self.camera_rotate_y[0]+moving_theta+math.radians(-90))
            position_change[2] = self.camera_walk_units_per_frame*moving_r_multiplier * math.sin(self.camera_rotate_y[0]+moving_theta+math.radians(-90))

            # if (self.camera_translate[0] + move_by_x > self._world_cube.get_max_x()):
            #     move_by_x = self._world_cube.get_max_x() - self.camera_translate[0]
            #     print(str(self.camera_translate[0])+" of max_x:"+str(self._world_cube.get_max_x()))
            # if (self.camera_translate[2] + move_by_z > self._world_cube.get_max_z()):
            #     move_by_z = self._world_cube.get_max_z() - self.camera_translate[2]
            #     print(str(self.camera_translate[2])+" of max_z:"+str(self._world_cube.get_max_z()))
            # if (self.camera_translate[0] + move_by_x < self._world_cube.get_min_x()):
            #     move_by_x = self._world_cube.get_min_x() - self.camera_translate[0]
            #     print(str(self.camera_translate[0])+" of max_x:"+str(self._world_cube.get_max_x()))
            # if (self.camera_translate[2] + move_by_z < self._world_cube.get_min_z()):
            #     move_by_z = self._world_cube.get_min_z() - self.camera_translate[2]
            #     print(str(self.camera_translate[2])+" of max_z:"+str(self._world_cube.get_max_z()))

            #print(str(self.camera_translate[0])+","+str(self.camera_translate[2])+" each coordinate should be between matching one in "+str(self._world_cube.get_min_x())+","+str(self._world_cube.get_min_z())+" and "+str(self._world_cube.get_max_x())+","+str(self._world_cube.get_max_z()))
            #print(str(self.camera_translate)+" each coordinate should be between matching one in "+str(self.world_boundary_min)+" and "+str(self.world_boundary_max))

        for axis_index in range(0,3):
            if position_change[axis_index] is not None:
                self.camera_translate[axis_index] += position_change[axis_index]
        if len(self.scene._walkmeshes)>0:
            if not self.is_in_any_walkmesh_xz(self.camera_translate):
                #print("Out of bounds")
                if self.scene.prev_inbounds_camera_translate is not None:
                    self.camera_translate[0] = self.scene.prev_inbounds_camera_translate[0]
                    self.camera_translate[1] = self.scene.prev_inbounds_camera_translate[1]
                    self.camera_translate[2] = self.scene.prev_inbounds_camera_translate[2]
                else:
                    corrected_pos = self.get_nearest_walkmesh_vec3_using_xz( self.camera_translate )
                if corrected_pos is not None:
                    pushed_angle = get_angle_between_two_vec3_xz(self.camera_translate, corrected_pos)
                    corrected_pos = get_pushed_vec3_xz_rad(corrected_pos, self.scene.camera_glop.hit_radius, pushed_angle)
                    self.camera_translate[0] = corrected_pos[0]
                    self.camera_translate[1] = corrected_pos[1]   # TODO: check y (vertical) axis against eye height and jump height etc
                    #+ self.scene.camera_glop.eye_height #no longer needed since swizzled to xz (get_nearest_walkmesh_vec3_using_xz returns original's y in return's y)
                    self.camera_translate[2] = corrected_pos[2]
                else:
                    print("ERROR: could not find point to bring player in bounds.")
            else:
                #print("In bounds")
                pass
        else:
            #print("No bounds")
            pass
        self.scene.prev_inbounds_camera_translate = self.camera_translate[0], self.camera_translate[1], self.camera_translate[2]

        # else:
        #     self.camera_translate[0] += self.camera_walk_units_per_frame * moving_x
        #     self.camera_translate[2] += self.camera_walk_units_per_frame * moving_z

        #if verbose_enable:
        #    print("update_glsl...")
        asp = float(self.width) / float(self.height)
        #was .3 when projection_near was 1
        field_of_view_factor = 0.03
        asp = asp*field_of_view_factor
        proj = Matrix()
        modelViewMatrix = Matrix()

        #modelViewMatrix.rotate(self.camera_rotate_x[0],self.camera_rotate_x[1],self.camera_rotate_x[2],self.camera_rotate_x[3])
        #modelViewMatrix.rotate(self.camera_rotate_y[0],self.camera_rotate_y[1],self.camera_rotate_y[2],self.camera_rotate_y[3])
        #look_at(eyeX, eyeY, eyeZ, centerX, centerY, centerZ, upX, upY, upZ)  $http://kivy.org/docs/api-kivy.graphics.transformation.html
        #modelViewMatrix.rotate(self.camera_rotate_z[0],self.camera_rotate_z[1],self.camera_rotate_z[2],self.camera_rotate_z[3])
        previous_look_point = None
        if self.look_point is not None:
            previous_look_point = self.look_point[0], self.look_point[1], self.look_point[2]

        self.look_point = [0.0,0.0,0.0]

        #0 is the angle (1, 2, and 3 are the matrix)
        self.look_point[0] = self.focal_distance * math.cos(self.camera_rotate_y[0])
        self.look_point[2] = self.focal_distance * math.sin(self.camera_rotate_y[0])

        self.look_point[1] = 0.0  #(changed in "for" loop below) since y is up, and 1 is y, ignore index 1 when we are rotating on that axis


        #modelViewMatrix = modelViewMatrix.look_at(0,self.camera_translate[1],0, self.look_point[0], self.look_point[1], self.look_point[2], 0, 1, 0)

        #Since what you are looking at should be relative to yourself, add camera's position:
        for axis_index in range(3):
            self.look_point[axis_index] += self.camera_translate[axis_index]

        #must translate first, otherwise look_at will override position on rotation axis ('y' in this case)
        modelViewMatrix.translate(self.camera_translate[0], self.camera_translate[1], self.camera_translate[2])
        #moving_theta = theta_radians_from_rectangular(moving_x, moving_z)
        modelViewMatrix = modelViewMatrix.look_at(self.camera_translate[0], self.camera_translate[1], self.camera_translate[2], self.look_point[0], self.look_point[1], self.look_point[2], 0, 1, 0)



        #proj.view_clip(left, right, bottom, top, near, far, perspective)
        proj = proj.view_clip(-asp, asp, -1*field_of_view_factor, field_of_view_factor, self.projection_near, 100, 1)

        self.canvas['projection_mat'] = proj
        self.canvas['modelview_mat'] = modelViewMatrix
        self.canvas["camera_world_pos"] = self.camera_translate
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
            #print ("position: "+str(self.camera_translate)+"; self.camera_rotate_y[0]:"+str(self.camera_rotate_y[0]) +"("+str(math.degrees(self.camera_rotate_y[0]))+"degrees); moving_theta:"+str(math.degrees(moving_theta))+" degrees")

        if (self._previous_world_light_dir is None
            or self._previous_world_light_dir[0]!=self.canvas["_world_light_dir"][0]
            or self._previous_world_light_dir[1]!=self.canvas["_world_light_dir"][1]
            or self._previous_world_light_dir[2]!=self.canvas["_world_light_dir"][2]
            or self._previous_camera_rotate_y_angle is None
            or self._previous_camera_rotate_y_angle != self.camera_rotate_y[0]
            ):
            #self.canvas["_world_light_dir"] = (0.0,.5,1.0);
            #self.canvas["_world_light_dir_eye_space"] = (0.0,.5,1.0);
            world_light_theta = theta_radians_from_rectangular(self.canvas["_world_light_dir"][0], self.canvas["_world_light_dir"][2])
            light_theta = world_light_theta+self.camera_rotate_y[0]
            light_r = math.sqrt((self.canvas["_world_light_dir"][0]*self.canvas["_world_light_dir"][0])+(self.canvas["_world_light_dir"][2]*self.canvas["_world_light_dir"][2]))
            self.canvas["_world_light_dir_eye_space"] = light_r * math.cos(light_theta), self.canvas["_world_light_dir_eye_space"][1], light_r * math.sin(light_theta)
            self._previous_camera_rotate_y_angle = self.camera_rotate_y[0]
            self._previous_world_light_dir = self.canvas["_world_light_dir"][0], self.canvas["_world_light_dir"][1], self.canvas["_world_light_dir"][2]


    def define_rotate_angle(self, touch):
        x_angle = (touch.dx/self.width)*360
        y_angle = -1*(touch.dy/self.height)*360
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

        #if touch.is_mouse_scrolling:

    def on_touch_up(self, touch):
        super(KivyGlopsWindow, self).on_touch_up(touch)
        #touch.ungrab(self)
        #self._touches.remove(touch)
        #self.player1_controller.dump()

    def print_location(self):
        if verbose_enable:
            Logger.debug("self.camera_walk_units_per_second:"+str(self.camera_walk_units_per_second)+"; location:"+str(self.camera_translate))

    def get_pressed(self, key_name):
        return self.player1_controller.get_pressed(Keyboard.keycodes[key_name])

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
        #     self.camera_translate[2] += self.camera_walk_units_per_frame
        # elif keycode[1] == 's':
        #     self.camera_translate[2] -= self.camera_walk_units_per_frame
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
        # else:
        #     print('Pressed unused key: ' + str(keycode) + "; text:"+text)

        if verbose_enable:
            self.print_location()
            print("camera_rotate_y:"+str(self.camera_rotate_y))
            print("modelview_mat:"+str(self.canvas['modelview_mat']))
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

    def on_touch_move(self, touch):
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
#                     self.camera_translate[2] += scale
#                     print(scale, self.camera_translate)
#             self.update_glsl()

