import math

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import *
from kivy.graphics import *
#from objloader import ObjFile
from kivy.logger import Logger
from kivy.vector import Vector
from kivy.core.image import Image
from kivy.core.window import Keyboard

import os

# from kivyglops import KivyGlops
# from kivyglops import KivyGlop
from kivyglops import *
from pyrealtime import *
from kivy.input.providers.mouse import MouseMotionEvent

MODE_EDIT = "edit"
MODE_GAME = "game"

class Renderer(Widget):
    IsVerbose = False
    IsVisualDebugMode = False
    glops = None  # TODO: eliminate this by finishing KivyGlops as window (Widget), and making Renderer a subclass of KivyGlops
    frames_per_second = 60.0
    camera_walk_units_per_second = None

    selected_glop = None
    selected_glopIndex = None

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

        self.glops = KivyGlops()
        self.canvas = RenderContext(compute_normal_mat=True)
        self.canvas["_world_light_dir"] = (0.0, 0.5, 1.0);
        self.canvas["_world_light_dir_eye_space"] = (0.0, 0.5, 1.0); #rotated in update_glsl
        self.canvas["camera_light_multiplier"] = (1.0, 1.0, 1.0, 1.0)
        self.canvas.shader.source = resource_find('simple1b.glsl')
        #self.canvas.shader.source = resource_find('shade-kivyglops-standard.glsl')
        #self.canvas.shader.source = resource_find('shade-normal-only.glsl')
        #self.canvas.shader.source = resource_find('shade-texture-only.glsl')
        #self.canvas.shader.source = resource_find('shade-kivyglops-minimal.glsl')

        #self.glops.load_obj(resource_find("barrels triangulated (Costinus at turbosquid).obj"))
        #self.glops.load_obj(resource_find("barrel.obj"))
        #self.glops.load_obj(resource_find("KivyGlopsDemoScene.obj"))
        self.glops.load_obj(resource_find("testnurbs-all-textured.obj"))
        

        #self.glops.load_obj(resource_find("pyramid.obj"))
        #self.glops.load_obj(resource_find("orion.obj"))
        print(self.canvas.shader)
        glopsYAMLLines = []
        self.glops.append_dump(glopsYAMLLines)
        try:
            thisFile = open('glops-dump.yml', 'w')
            for i in range(0,len(glopsYAMLLines)):
                thisFile.write(glopsYAMLLines[i]+"\n")
            thisFile.close()
        except:
            print("Could not finish writing dump.")
        #self.scene = ObjFile(resource_find("orion.obj"))
        super(Renderer, self).__init__(**kwargs)
        self.cb = Callback(self.setup_gl_context)
        self.canvas.add(self.cb)

        self.canvas.add(PushMatrix())
        #self.canvas.add(thisTexture)
        #self.canvas.add(Color(1, 1, 1, 1))
        for thisMeshIndex in range(0,len(self.glops.glops)):
            thisMeshName = ""
            #thisMesh = KivyGlop()
            this_glop = self.glops.glops[thisMeshIndex]
            if self.selected_glopIndex is None:
                self.selected_glopIndex = thisMeshIndex
                self.selected_glop = this_glop
            if this_glop.name is not None:
                thisMeshName =  self.glops.glops[thisMeshIndex].name
            self.canvas.add(PushMatrix())
            self.canvas.add(this_glop._translate_instruction)
            self.canvas.add(this_glop._rotate_instruction_x)
            self.canvas.add(this_glop._rotate_instruction_y)
            self.canvas.add(this_glop._scale_instruction)
            #self.scale = Scale(0.6)
            #m = list(self.scene.glops.values())[0]
            #self.canvas.add(m)
            self.canvas.add(UpdateNormalMatrix())

            self.lastLoadedFileName = this_glop.get_texture_diffuse_filename()
            thisTextureImage = None
            if self.lastLoadedFileName is not None:
                try:
                    thisTextureImage = Image(self.lastLoadedFileName)
                except:
                    print("missing texture: " + self.lastLoadedFileName)
            else:
                if self.IsVerbose:
                    Logger.debug("Warning: no texture specified for mesh named '"+thisMeshName+"'")
                    materialName = ""
                    if this_glop.material is not None:
                        if this_glop.material.name is not None:
                            materialName = this_glop.material.name
                            Logger.debug("(material named '"+materialName+"')")
                        else:
                            Logger.debug("(material with no name)")
                    else:
                        Logger.debug("(no material)")
            thisTexture = None
            if (thisTextureImage is not None):
                thisTexture = thisTextureImage.texture

            thisMesh = Mesh(
                vertices=this_glop.vertices,
                indices=this_glop.indices,
                fmt=this_glop.vertex_format,
                mode='triangles',
                texture=thisTexture,
            )
            self.canvas.add(this_glop._color_instruction)
            self.canvas.add(thisMesh)
            self.canvas.add(PopMatrix())

        self.canvas.add(PopMatrix())


        self.resetCallback = Callback(self.reset_gl_context)
        self.canvas.add(self.resetCallback)

        self.camera_translate = [0, 1.7, -25] #x,y,z where y is up  #1.7 since 5'10" person is ~1.77m, and eye down a bit
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
        self.camera_rotate_y = [math.radians(90.0), 0.0, 1.0, 0.0]
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

        rotation_multiplier_y = 0.0  # 1.0 is maximum speed
        moving_x = 0.0  # 1.0 is maximum speed
        moving_z = 0.0  # 1.0 is maximum speed; NOTE: increased z moves object farther away
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
        # else:
        #     self.camera_translate[0] += self.camera_walk_units_per_frame * moving_x
        #     self.camera_translate[2] += self.camera_walk_units_per_frame * moving_z

        #if self.IsVerbose:
        #    print("update_glsl...")
        asp = float(self.width) / float(self.height)
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
        #if self.IsVerbose:
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
        super(Renderer, self).on_touch_down(touch)
        #touch.grab(self)
        #self._touches.append(touch)

#         thisTouch = MouseMotionEvent(touch)
#         thisTouch.

        #if touch.is_mouse_scrolling:

    def on_touch_up(self, touch):
        super(Renderer, self).on_touch_up(touch)
        #touch.ungrab(self)
        #self._touches.remove(touch)
        #self.player1_controller.dump()

    def print_location(self):
        if self.IsVerbose:
            Logger.debug("self.camera_walk_units_per_second:"+str(self.camera_walk_units_per_second)+"; location:"+str(self.camera_translate))


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
            self.selectMeshByIndex(self.selected_glopIndex+1)
            if self.IsVerbose:
                this_name = None
                if self.selected_glopIndex is not None:
                    this_name = "["+str(self.selected_glopIndex)+"]"
                if self.selected_glop is not None and self.selected_glop.name is not None:
                    this_name = self.selected_glop.name
                if this_name is not None:
                    Logger.debug('Selected glop: '+this_name)
                else:
                    Logger.debug('Select glop failed (maybe there are no glops loaded.')
        # else:
        #     print('Pressed unused key: ' + str(keycode) + "; text:"+text)

        if self.IsVerbose:
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


    def selectMeshByIndex(self, index):
        glop_count = len(self.glops.glops)
        if (index>=glop_count):
            index=0
        if self.IsVerbose:
            Logger.debug("trying to select index "+str(index)+" (count is "+str(glop_count)+")...")
        if (glop_count > 0):
            self.selected_glopIndex = index
            self.selected_glop = self.glops.glops[index]
        else:
            self.selected_glop = None
            self.selected_glopIndex = None

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


class KivyGlopsExampleApp(App):
    def build(self):

        return Renderer()

if __name__ == "__main__":
    KivyGlopsExampleApp().run()
