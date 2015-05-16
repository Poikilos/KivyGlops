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

# from kivymesher import KivyMesher
# from kivymesher import KivyMesherMesh
from kivymesher import *
from pyrealtime import *
from kivy.input.providers.mouse import MouseMotionEvent

class Renderer(Widget):
    IsVerbose = False
    IsVisualDebugMode = False
    mesher = None
    frames_per_second = 60.0
    camera_walk_units_per_second = None

    selectedMM = None
    selectedMMIndex = None

    focal_distance = None

    mode = None
    MODE_EDIT = "edit"
    MODE_GAME = "game"

    look_point = None

    # moving_x = 0.0
    # moving_z = 0.0
    # _turning_y = 0.0
    controllers = list()
    player1_controller = None


    def __init__(self, **kwargs):
        self.camera_walk_units_per_second = 12.0
        self.camera_turn_radians_per_second = math.radians(90.0)
        self.mode = self.MODE_EDIT
        self.player1_controller = PyRealTimeController()
        self.controllers.append(self.player1_controller)
        self.focal_distance = 2.0
        try:
            self._keyboard = Window.request_keyboard(
                self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
            self._keyboard.bind(on_key_up=self._on_keyboard_up)
        except:
            print("Could not finish loading keyboard (keyboard may not be present).")

        #self.bind(on_touch_down=self.canvasTouchDown)

        self.mesher = KivyMesher()
        self.canvas = RenderContext(compute_normal_mat=True)
        #self.canvas["_world_light_dir"]
        self.canvas["world_light_dir_eye_space"] = (0.0,.5,1.0);
        self.canvas["camera_light_multiplier"] = (1.0, 1.0, 1.0, 1.0)
        self.canvas.shader.source = resource_find('shade-kivymesher-standard.glsl')
        #self.canvas.shader.source = resource_find('shade-normal-only.glsl')
        #self.canvas.shader.source = resource_find('shade-texture-only.glsl')

        #self.mesher.load_obj(resource_find("barrels triangulated (Costinus at turbosquid).obj"))
        #self.mesher.load_obj(resource_find("barrel.obj"))
        #self.mesher.load_obj(resource_find("KivyMesherDemoScene.obj"))
        self.mesher.load_obj(resource_find("testnurbs-all-textured.obj"))
        #self.mesher.load_obj(resource_find("pyramid.obj"))
        #self.mesher.load_obj(resource_find("orion.obj"))
        print(self.canvas.shader)
        mesherYAMLLines = []
        self.mesher.dump(mesherYAMLLines)
        try:
            thisFile = open('mesher-dump.yml', 'w')
            for i in range(0,len(mesherYAMLLines)):
                thisFile.write(mesherYAMLLines[i]+"\n")
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
        for thisMeshIndex in range(0,len(self.mesher.meshes)):
            thisMeshName = ""
            #thisMesh = KivyMesherMesh()
            thisMM = self.mesher.meshes[thisMeshIndex]
            if self.selectedMMIndex is None:
                self.selectedMMIndex = thisMeshIndex
                self.selectedMM = thisMM
            if thisMM.name is not None:
                thisMeshName =  self.mesher.meshes[thisMeshIndex].name
            self.canvas.add(PushMatrix())
            self.canvas.add(thisMM._translate_instruction)
            self.canvas.add(thisMM._rotate_instruction_x)
            self.canvas.add(thisMM._rotate_instruction_y)
            self.canvas.add(thisMM._scale_instruction)
            #self.scale = Scale(0.6)
            #m = list(self.scene.meshes.values())[0]
            #self.canvas.add(m)
            self.canvas.add(UpdateNormalMatrix())

            self.lastLoadedFileName = thisMM.getTextureFileName()
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
                    if thisMM.material is not None:
                        if thisMM.material.name is not None:
                            materialName = thisMM.material.name
                            Logger.debug("(material named '"+materialName+"')")
                        else:
                            Logger.debug("(material with no name)")
                    else:
                        Logger.debug("(no material)")
            thisTexture = None
            if (thisTextureImage is not None):
                thisTexture = thisTextureImage.texture

            thisMesh = Mesh(
                vertices=thisMM.vertices,
                indices=thisMM.indices,
                fmt=thisMM.vertex_format,
                mode='triangles',
                texture=thisTexture,
            )
            self.canvas.add(thisMM._color_instruction)
            self.canvas.add(thisMesh)
            self.canvas.add(PopMatrix())

        self.canvas.add(PopMatrix())


        self.resetCallback = Callback(self.reset_gl_context)
        self.canvas.add(self.resetCallback)

        self.camera_translate = [0, 1.7, -25] #x,y,z where y is up  #1.7 since 5'10" person is ~1.77m, and eye down a bit
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


    def update_glsl(self, *largs):

        # NOTE: increased z moves object farther away

        rotation_multiplier_y = 0.0  #1.0 is maximum speed
        moving_x = 0.0  #1.0 is maximum speed
        moving_z = 0.0  #1.0 is maximum speed
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
            angle_y = self.camera_turn_radians_per_frame * rotation_multiplier_y
            self.camera_rotate_y[0] += angle_y
            #origin_distance = math.sqrt(self.camera_translate[0]*self.camera_translate[0] + self.camera_translate[2]*self.camera_translate[2])
            #self.camera_translate[0] -= origin_distance * math.cos(angle_y)
            #self.camera_translate[2] -= origin_distance * math.sin(angle_y)

        # move in the direction you are facing
        theta = 0.0
        if moving_x != 0.0 or moving_z != 0.0:
            #makes movement relative to rotation (which alaso limits speed when moving diagonally):
            theta = KivyMesher.theta_radians_from_rectangular(moving_x, moving_z)
            r_multiplier = math.sqrt((moving_x*moving_x)+(moving_z*moving_z))
            if r_multiplier > 1.0:
                r_multiplier = 1.0
            #TODO: reprogram so adding math.radians(-90) is not needed
            self.camera_translate[0] += self.camera_walk_units_per_frame*r_multiplier * math.cos(self.camera_rotate_y[0]+theta+math.radians(-90))
            self.camera_translate[2] += self.camera_walk_units_per_frame*r_multiplier * math.sin(self.camera_rotate_y[0]+theta+math.radians(-90))
        # else:
        #     self.camera_translate[0] += self.camera_walk_units_per_frame * moving_x
        #     self.camera_translate[2] += self.camera_walk_units_per_frame * moving_z

        #if self.IsVerbose:
        #    print("update_glsl...")
        asp = float(self.width) / float(self.height)
        field_of_view_factor = 0.3
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
        for axisIndex in range(3):
            self.look_point[axisIndex] += self.camera_translate[axisIndex]

        #must translate first, otherwise look_at will override position on rotation axis ('y' in this case)
        modelViewMatrix.translate(self.camera_translate[0], self.camera_translate[1], self.camera_translate[2])
        #theta = KivyMesher.theta_radians_from_rectangular(moving_x, moving_z)
        modelViewMatrix = modelViewMatrix.look_at(self.camera_translate[0], self.camera_translate[1], self.camera_translate[2], self.look_point[0], self.look_point[1], self.look_point[2], 0, 1, 0)



        #proj.view_clip(left, right, bottom, top, near, far, perspective)
        proj = proj.view_clip(-asp, asp, -1*field_of_view_factor, field_of_view_factor, 1, 100, 1)

        self.canvas['projection_mat'] = proj
        self.canvas['modelview_mat'] = modelViewMatrix
        #if self.IsVerbose:
        #    Logger.debug("ok (update_glsl)")

        is_look_point_changed = False
        if previous_look_point is not None:
            for axisIndex in range(3):
                if self.look_point[axisIndex] != previous_look_point[axisIndex]:
                    is_look_point_changed = True
                    #print(str(self.look_point)+" was "+str(previous_look_point))
                    break
        else:
            is_look_point_changed = True

        if is_look_point_changed:
            pass
            #print("Now looking at "+str(self.look_point))
            #print ("position: "+str(self.camera_translate)+"; self.camera_rotate_y[0]:"+str(self.camera_rotate_y[0]) +"("+str(math.degrees(self.camera_rotate_y[0]))+"degrees); theta:"+str(math.degrees(theta))+" degrees")



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
        self.player1_controller.dump()

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
            self.selectMeshByIndex(self.selectedMMIndex+1)
            if self.IsVerbose:
                meshNameString = None
                if self.selectedMMIndex is not None:
                    meshNameString = "["+str(self.selectedMMIndex)+"]"
                if self.selectedMM is not None and self.selectedMM.name is not None:
                    meshNameString = self.selectedMM.name
                if meshNameString is not None:
                    Logger.debug('Selected mesh: '+meshNameString)
                else:
                    Logger.debug('Select mesh failed (maybe there are no meshes loaded.')
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
        meshCount = len(self.mesher.meshes)
        if (index>=meshCount):
            index=0
        if self.IsVerbose:
            Logger.debug("trying to select index "+str(index)+" (count is "+str(meshCount)+")...")
        if (meshCount > 0):
            self.selectedMMIndex = index
            self.selectedMM = self.mesher.meshes[index]
        else:
            self.selectedMM = None
            self.selectedMMIndex = None

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


class KivyMesherExampleApp(App):
    def build(self):

        return Renderer()

if __name__ == "__main__":
    KivyMesherExampleApp().run()
