
"""
This module is the Kivy implementation of PyGlops.
It provides features that are specific to display method
(Kivy's OpenGL-like API in this case).
"""

#TODO: try adding captions and 2d axis indicators in canvas.after, or try RenderContext

# from pyglops import PyGlops
# from pyglops import PyGlopsMaterial
# from pyglops import PyGlop
from pyglops import *
from kivy.resources import resource_find
from kivy.graphics import *
from kivy.uix.widget import Widget
from kivy.core.image import Image

class KivyGlopsMaterial(PyGlopsMaterial):
    
    def __init__(self):
        super(KivyGlopsMaterial, self).__init__()
        
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

    def __init__(self): #, pyglop=None):
        super(KivyGlop, self).__init__()
        #self.freeAngle = 0.0
        #self.degreesPerSecond = 0.0
        #self.freePos = (10.0,100.0)
        self.canvas = RenderContext()
        #TODO:? self.canvas = RenderContext(compute_normal_mat=True)
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
        self._color_instruction = Color(Color(1.0,1.0,1.0,1.0))

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

    def _on_change_pivot(self):
        super(KivyGlop, self)._on_change_pivot()
        self._on_change_scale_instruction()

    def get_scale(self):
        return (self._scale_instruction.x + self._scale_instruction.y + self._scale_instruction.z) / 3.0;

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


class KivyGlops(PyGlops):
    
    def angles_to_angle_and_matrix(self, anglesXYZ):
        angleAndMatrix = [0.0,0.0,0.0,0.0]
        for axisIndex in range(len(anglesXYZ)):
            while anglesXYZ[axisIndex]<0:
                anglesXYZ[axisIndex] += 360.0
            if anglesXYZ[axisIndex] > angleAndMatrix[0]:
                angleAndMatrix[0] = anglesXYZ[axisIndex]
        if angleAndMatrix[0] > 0:
            for axisIndex in range(len(anglesXYZ)):
                angleAndMatrix[1+axisIndex] = anglesXYZ[axisIndex] / angleAndMatrix[0]
        else:
            angleAndMatrix[3] = .000001
        return angleAndMatrix

    def __init__(self):
        super(KivyGlops, self).__init__()

    def createMesh(self):
        #return PyGlops.createMesh(self)
        return KivyGlop()

    def createMaterial(self):
        return KivyGlopsMaterial()
        
    def load_obj(self,obj_path):
        obj_path = resource_find(obj_path)
        super(KivyGlops, self).load_obj(obj_path)
        if self.glops is None:
            self.glops = list()
            print("FAILED TO LOAD '"+obj_path+"'")
        elif len(self.glops)<1:
            print("NO VALID OBJECTS FOUND in '"+obj_path+"'")
        for index in range(0,len(self.glops)):
            this_glop = self.glops[index]
            #this_glop = KivyGlop(pyglop=self.glops[index])
            #if len(self.glops<=index):
                #self.glops.append(this_glop)
            #else:
                #self.glops[index]=this_glop
                
            this_texture_image = Image(this_glop.get_texture_diffuse_filename())
            this_texture = None
            if len(this_glop.vertices)>0:
                if (this_texture_image is not None):
                    this_texture = this_texture_image.texture
                self.glops[index]._mesh = Mesh(
                        vertices=this_glop.vertices,
                        indices=this_glop.indices,
                        fmt=this_glop.vertex_format,
                        mode='triangles',
                        texture=this_texture,
                    )
                print(str(len(this_glop.vertices))+" vert(ex/ices)")
            else:
                print("WARNING: 0 vertices in glop")
                if this_glop.name is not None:
                    print("  named "+this_glop.name)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                              

