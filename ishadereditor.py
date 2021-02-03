#!/usr/bin/env python

# from kivy.uix.boxlayout import BoxLayout
# from kivy.app import App
# from kivy.factory import Factory

# based on a very old version of
# https://kivy.org/docs/examples/gen__demo__shadereditor__main__py.html
# which is MIT licensed
'''
Live Shader Editor
==================

This provides a live editor for vertex and fragment editors.
You should see a window with two editable panes on the left
and a large kivy logo on the right.The top pane is the
Vertex shader and the bottom is the Fragment shader. The file shadereditor.kv
describes the interface.

On each keystroke to either shader, declarations are added and the shaders
are compiled. If there are no errors, the screen is updated. Otherwise,
the error is visible as logging message in your terminal.
'''
import sys
import os  # isfile etc
import kivy

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.graphics import RenderContext, Color
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from pygments.lexers import GLShaderLexer
from kivyglops import *

kivy.require('1.0.6')


def get_verbose_enable():
    return False


class ShaderEditor(KivyGlopsWindow):  # FloatLayout
    # aka MainForm
    pass
    # source = StringProperty('data/logo/kivy-icon-512.png')


# ---VERTEX SHADER------------------------------------------------------
    vs = StringProperty('''
#ifdef GL_ES
    precision highp float;
# endif

attribute vec4  a_position;
attribute vec4  a_color;
attribute vec2  a_texcoord0;
attribute vec4  a_normal;

uniform mat4 modelview_mat;
uniform mat4 projection_mat;
//uniform material  material_state;

varying vec4 frag_color;
varying vec2 uv_vec;
varying vec3 v_normal;
varying vec4 v_pos;

// struct VertextInput {  //sic
    // vec3 vertex : POSITION;
    // vec3 normal : NORMAL;
// };
// struct VertexOutput {
    // vec4 pos : SV_POSITION;
// };

void main (void) {
    vec4 pos = modelview_mat * a_position; //vec4(v_pos,1.0);
    v_pos = projection_mat * pos;
    gl_Position = v_pos;
    frag_color = a_color;
    uv_vec = a_texcoord0;
    v_normal = a_normal.xyz;
}

''')

# ---FRAGMENT SHADER-------------------------------------------------------

    fs = StringProperty('''
//https://www.youtube.com/watch?v=WMHpBpjWUlY
#ifdef GL_ES
    precision highp float;
# endif

varying vec4 frag_color;
varying vec2 uv_vec;
varying vec3 v_normal;
varying vec4 v_pos;
uniform vec3 camera_world_pos;

uniform sampler2D tex;

// should have default sharpness otherwise must always set it in calling
// program.
// uniform fresnel_sharpness; //uniform _sharpness;


void main (void){
    float default_fresnel_sharpness = .2;
    //if (fresnel_sharpness==null) {
        //fresnel_sharpness = default_fresnel_sharpness;
    //}
    float fresnel_sharpness = default_fresnel_sharpness;
    vec4 color = texture2D(tex, uv_vec);
    vec3 V = normalize( camera_world_pos.xyz - v_pos.xyz );
    // ^ was normalize( _WorldSpaceCameraPos.xyz - i.posWorld );
    vec3 N = normalize(v_normal); //normalize( i.normalDir );
    float fresnel = pow( 1.0 - dot( N, V), fresnel_sharpness );
    // ^ was pow( 1.0 - dot( N, V), _sharpness );
    vec4 fresnel_color = vec4(fresnel, fresnel, fresnel, 1.0);
    gl_FragColor = color * fresnel_color;
}
''')
# ---END SHADERS-------------------------------------------------------

    gl_widget = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ShaderEditor, self).__init__(**kwargs)
        self._contexts = InstructionGroup()
        self.test_canvas = RenderContext()
        s = self.test_canvas.shader
        self.trigger_compile = Clock.create_trigger(self.compile_shaders, -1)
        self.bind(fs=self.trigger_compile, vs=self.trigger_compile)

    scene = None
    frames_per_second = 30.0

    def suspend_debug_label_update(self, enable):
        # TODO: do something useful here
        pass

    def set_debug_label(self, text):
        # TODO: do something useful here
        pass

    def add_glop(self, this_glop, set_visible_enable=None):
        if set_visible_enable is not None:
            this_glop.state["visible_enable"] = set_visible_enable
        # context = self._contexts
        # context = self.gl_widget.canvas
        # if self.scene.selected_glop_index is None:
        #     self.scene.selected_glop_index = this_glop_index
        #     self.scene.selected_glop = this_glop
        self.scene.selected_glop_index = len(self.scene.glops)
        self.scene.selected_glop = this_glop
        context = this_glop.get_context()
        # TODO set shader
        # KivyGlops does: self.gl_widget.canvas.shader.source = filename
        print("dir(context):{}".format(dir(context)))
        # context.shader.source = self.gl_widget.canvas.shader.source
        # context.shader.source = self.vs + self.fs
        this_mesh_name = ""
        if this_glop.name is not None:
            this_mesh_name = this_glop.name
        # this_glop._s_ins = Scale(0.6)
        this_glop._pushmatrix = PushMatrix()
        this_glop._updatenormalmatrix = UpdateNormalMatrix()
        this_glop._popmatrix = PopMatrix()

        context.add(this_glop._pushmatrix)
        context.add(this_glop._t_ins)
        context.add(this_glop._r_ins_x)
        context.add(this_glop._r_ins_y)
        context.add(this_glop._r_ins_z)
        context.add(this_glop._s_ins)
        context.add(this_glop._updatenormalmatrix)

        # context.add(this_glop._color_instruction)
        # ^ TODO: asdf add as uniform instead
        if this_glop._mesh is None:
            # verts, indices = this_glop.generate_kivy_mesh()
            print("WARNING: glop had no mesh, so was generated when"
                  " added to render context. Please ensure it is a"
                  " KivyGlop and not a PyGlop (however, vertex indices"
                  " misread could also lead to missing Mesh object).")

        if this_glop._mesh is not None:
            context.add(this_glop._mesh)
            if get_verbose_enable():
                print("Added mesh to render context.")
        else:
            print("NOT adding mesh.")
        context.add(this_glop._popmatrix)
        if self.scene.glops is None:
            self.scene.glops = list()

        # context.add(PushMatrix())
        # context.add(this_glop._t_ins)
        # context.add(this_glop._r_ins_x)
        # context.add(this_glop._r_ins_y)
        # context.add(this_glop._r_ins_z)
        # context.add(this_glop._s_ins)
        # context.add(this_glop._updatenormalmatrix)
        # context.add(this_glop._axes_mesh)
        # context.add(PopMatrix())

        self.scene.glops.append(this_glop)
        this_glop.glop_index = len(self.scene.glops) - 1
        if self.scene.glops[this_glop.glop_index] is not this_glop:
            # deal with multithreading paranoia:
            print("[ ishadereditor.py ] glop_index was wrong,"
                  " correcting...")
            this_glop.glop_index = None
            for i in range(len(self.scene.glops)):
                if self.scene.glops[i] is this_glop:
                    self.scene.glops[i].glop_index = i
                    break
            if this_glop.glop_index is None:
                print("                      ERROR:"
                      " unable to correct index")
        # this_glop.glop_index = len(self.scene.glops) - 1
        this_glop.state["glop_index"] = this_glop.glop_index
        lastI = len(self.scene.glops) - 1
        self._contexts.add(self.scene.glops[lastI].get_context())
        # ^ _contexts is a visible instruction group
        self.scene.glops[lastI].state["visible_enable"] = True

        if get_verbose_enable():
            print("Appended Glop (count:" + str(len(self.scene.glops))
                  + ").")

    def compile_shaders(self, *largs):
        print('try compile')
        if not self.gl_widget:
            return
        fs = self.fs  # fs_header + self.fs
        vs = self.vs  # vs_header + self.vs
        print('-->', fs)
        self.gl_widget.fs = fs
        print('-->', vs)
        self.gl_widget.vs = vs

    def update_vs_to_vs_codeinput(self, instance, value):
        # self.vs = self.vs_codeinput.text
        self.vs = value  # self.vs_codeinput.text
        print("update_vs_to_vs_codeinput")

    def update_fs_to_fs_codeinput(self, instance, value):
        # self.fs = self.fs_codeinput.text
        self.fs = value  # self.fs_codeinput.text
        print("update_fs_to_fs_codeinput")

    def interruptClick(self, instance):
        instance.disabled = True
        instance.opacity = 0.0
        continueButton = Factory.Button(
            text="Continue",
            # id="continueButton"
        )
        popup = Factory.Popup(
            title="The button is gone.",
            size_hint=(.25, .25),
            content=continueButton,
            auto_dismiss=False
        )
        continueButton.bind(on_press=popup.dismiss)
        popup.open()


form = None


class ShaderViewer(FloatLayout):
    fs = StringProperty(None)
    vs = StringProperty(None)

    def __init__(self, **kwargs):
        self.canvas = RenderContext()
        super(ShaderViewer, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_shader, 0)

    def update_shader(self, *args):
        s = self.canvas
        # s['projection_mat'] = Window.render_context['projection_mat']
        s['projection_mat'] = Window.render_context['projection_mat']
        s['time'] = Clock.get_boottime()
        s['resolution'] = list(map(float, self.size))
        # if form.gl_widget.pos is not None:
        # form.image_rect.pos=form.gl_widget.pos
        # if form.gl_widget.size is not None:
        # form.image_rect.size=form.gl_widget.size
        form.vs_label.height = form.vs_label.texture_size[1] + 10
        form.fs_label.height = form.fs_label.texture_size[1] + 10
        s.ask_update()

    def on_fs(self, instance, value):
        self.canvas.shader.fs = value

    def on_vs(self, instance, value):
        self.canvas.shader.vs = value


Factory.register('ShaderViewer', cls=ShaderViewer)


class Imperative_ShaderEditorApp(App):

    title = "ShaderEditor (Imperative)"

    def build(self):
        global form
        kwargs = {}
        # example_path = 'richmond-bridge-512x512-rgba-CC0.png'
        # if len(sys.argv) > 1:
        #     kwargs['source'] = sys.argv[1]
        form = ShaderEditor(**kwargs)
        # if ((not (os.path.isfile(form.source)))
        #         and os.path.isfile(example_path)):
        #     form.source = example_path
        # print("using image: '"+form.source+"'")
        form.main_layout = Factory.BoxLayout(orientation="horizontal")
        form.add_widget(form.main_layout)
        form.input_layout = Factory.BoxLayout(orientation="vertical")

        form.vs_label = Factory.Label(text='Vertex Shader',
                                      size_hint_y=None)
        form.vs_label.height = form.vs_label.texture_size[1] + 10
        form.input_layout.add_widget(form.vs_label)
        form.vs_codeinput = Factory.CodeInput(text=form.vs)
        form.vs_codeinput.lexer = GLShaderLexer()
        form.vs_codeinput.bind(text=form.update_vs_to_vs_codeinput)
        # ^ on_text=root.vs = args[1]
        form.input_layout.add_widget(form.vs_codeinput)

        form.fs_label = Factory.Label(text='Fragment Shader',
                                      size_hint_y=None)
        form.fs_label.height = form.fs_label.texture_size[1] + 10
        form.input_layout.add_widget(form.fs_label)
        form.fs_codeinput = Factory.CodeInput(text=form.fs)
        form.fs_codeinput.lexer = GLShaderLexer()
        form.fs_codeinput.bind(text=form.update_fs_to_fs_codeinput)
        # ^ on_text=root.fs = args[1]
        form.input_layout.add_widget(form.fs_codeinput)

        form.gl_widget = Factory.ShaderViewer()
        # form.image_color = Color(1.0,1.0,1.0,1.0)
        # form.gl_widget.canvas.add(form.image_color)
        # form.gl_widget.canvas.add(Factory.Rectangle(
        #     pos=form.gl_widget.pos,
        #     size=form.gl_widget.size,
        #     source=form.source
        # ))
        # form.image_rect = Factory.Rectangle(pos=(200,0),
        #                                     size=(512,512),
        #                                     source=form.source)

        form.scene = KivyGlops(form)
        form.scene.load_obj(os.path.join("meshes", "shader-test.obj"))

        # form.gl_widget.canvas.add(form.image_rect)
        form.main_layout.add_widget(form.input_layout)
        form.main_layout.add_widget(form.gl_widget)

        # form.cols = 1
        # form.orientation = "vertical"
        # form.okButton = Factory.Button(text="Hide Button", id="okButton")
        # form.add_widget(form.okButton)
        # form.okButton.bind(on_press=form.interruptClick)
        return form


if __name__ == '__main__':
    Imperative_ShaderEditorApp().run()
