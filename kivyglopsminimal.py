'''
3D Rotating PyGlop
==================
based on Kivy-1.9.0-py3.4-win32-x86\kivy34\examples\3Drendering\main.py

This example demonstrates using OpenGL to display a rotating mesh (first mesh of obj file). This
includes loading a Blender OBJ file, shaders written in OpenGL's Shading
Language (GLSL), and using scheduled callbacks.

The monkey.obj file is an OBJ file output from the Blender free 3D creation
software. The file is text, listing vertices and faces and is loaded
using a class in the file objloader.py. The file simple.glsl is
a simple vertex and fragment shader written in GLSL.
'''

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import *
from kivy.graphics import *
from kivyglops import *


class Renderer(Widget):
    scene = None
    def __init__(self, **kwargs):
        self.canvas = RenderContext(compute_normal_mat=True)

        #self.canvas.shader.source = resource_find('simple.glsl')
        self.canvas.shader.source = resource_find('simple1b.glsl')
        #self.canvas.shader.source = resource_find('shade-kivyglops-standard.glsl')
        #self.canvas.shader.source = resource_find('shade-normal-only.glsl')
        #self.canvas.shader.source = resource_find('shade-texture-only.glsl')
        #self.canvas.shader.source = resource_find('shade-kivyglops-minimal.glsl')

        self.scene = KivyGlops()
        #self.scene = ObjFile(resource_find("monkey.obj"))
        #self.scene.load_obj(resource_find("barrels triangulated (Costinus at turbosquid).obj"))
        #self.scene.load_obj(resource_find("barrel.obj"))
        #self.scene.load_obj(resource_find("KivyGlopsDemoScene.obj"))
        self.scene.load_obj(resource_find("testnurbs-all-textured.obj"))

        super(Renderer, self).__init__(**kwargs)
        with self.canvas:
            self.cb = Callback(self.setup_gl_context)
            PushMatrix()
            self.setup_scene()
            PopMatrix()
            self.cb = Callback(self.reset_gl_context)
        Clock.schedule_interval(self.update_glsl, 1 / 60.)

    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)

    def update_glsl(self, *largs):
        asp = self.width / float(self.height)
        proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 100, 1)
        self.canvas['projection_mat'] = proj
        self.canvas['diffuse_light'] = (1.0, 1.0, 0.8)
        self.canvas['ambient_light'] = (0.1, 0.1, 0.1)
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
        

    def setup_scene(self):
        Color(1, 1, 1, 1)
        PushMatrix()
        Translate(0, 0, -3)
        self.rot = Rotate(1, 0, 1, 0)
        #for i in range(0,len(self.scene)):
        #    self.scene.glops[i].append_dump(thisList, tabString)
        #m = list(self.scene.objects.values())[0]
        m = self.scene.glops[0]
        #self.dump_pyglop(m)
        
        UpdateNormalMatrix()
        self.mesh = Mesh(
            vertices=m.vertices,
            indices=m.indices,
            fmt=m.vertex_format,
            mode='triangles',
        )
        PopMatrix()


class RendererApp(App):
    def build(self):
        return Renderer()

if __name__ == "__main__":
    RendererApp().run()
