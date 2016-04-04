#from kivy.uix.boxlayout import BoxLayout
#from kivy.app import App
#from kivy.factory import Factory
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
kivy.require('1.0.6')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.graphics import RenderContext, Color
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock  
from pygments.lexers import GLShaderLexer

#aka MainForm
class ShaderEditor(FloatLayout):
    
    source = StringProperty('data/logo/kivy-icon-512.png')

#---VERTEX SHADER-------------------------------------------------------
    vs = StringProperty('''
#ifdef GL_ES
    precision highp float;
#endif

attribute vec3  a_position; //set by vertex (named by vertex_format)
attribute vec3  a_normal; //formerly vNormal; set by vertex (named by vertex_format)
attribute vec4  a_color; //formerly vColor; TODO: oops noone set this (neither kivy nor nskrypnik [C:\Kivy-1.8.0-py3.3-win32\kivy\examples\3Drendering\simple.glsl doesn't even mention the variable ])--vertex_format should name it. No wonder having no texture (or multiplying by vColor) makes object invisible. 
attribute vec2  a_texcoord0; //formerly vTexCoord0; set by vertex (named by vertex_format)

uniform mat4 modelview_mat; 
uniform mat4 projection_mat; 

varying vec4 normal_vec; //set by vertex shader below
varying vec4 vertex_pos; 
uniform mat4 normal_mat; //normal-only
varying vec4 frag_color; //set by vertex shader below (according to a_color)
varying vec2 uv_vec; 


varying vec2 uv; //http://www.kickjs.org/example/shader_editor/shader_editor.html
varying vec3 n; //http://www.kickjs.org/example/shader_editor/shader_editor.html


void main()
{
    //compute vertex position in eye_sapce and normalize normal vector
    vec4 pos = modelview_mat * vec4(a_position,1.0);
    vertex_pos = pos;
    normal_vec = vec4(vNormal,0.0);
    //gl_Position = projection_mat * pos;
    
    // Transforming The Vertex
    /* gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex; this is the c++ way*/
    //vec4 pos = modelview_mat * vec4(a_position,1.0);
    gl_Position = projection_mat * pos;
    frag_color = a_color;
    uv_vec = a_texcoord0;

    //uv = a_texcoord0; //uv = uv1; //http://www.kickjs.org/example/shader_editor/shader_editor.html
    // compute light info
    //n = normalize (normal_mat * vNormal); //n = normalize(_norm * normal); //http://www.kickjs.org/example/shader_editor/shader_editor.html
    
}
''')

#---FRAGMENT SHADER-------------------------------------------------------

    fs = StringProperty('''
#ifdef GL_ES
    precision highp float;
#endif
//according to http://nehe.gamedev.net/article/glsl_an_introduction/25007/
//fragment shader replaces all fragment functions in the fixed-function OpenGL pipeline, so you would (as standard practice) do your own:
// * Texture access and application (Texture environments)
// * Fog
// sampler types (have to be declared uniform [which is read-only])
//sampler1D, sampler2D, sampler3D       1D, 2D and 3D texture
//samplerCube                           Cube Map texture
//sampler1Dshadow, sampler2Dshadow  1D and 2D depth-component texture

uniform vec4 camera_light_multiplier;


//#region normal-only
varying vec4 normal_vec;
varying vec4 vertex_pos;

uniform mat4 normal_mat;
//#endregion normal-only

//#region texture-only
varying vec4 frag_color;
varying vec2 uv_vec;

uniform sampler2D tex;
//#endregion texture-only
uniform vec3 _world_light_dir_eye_space;

varying vec3 n; //http://www.kickjs.org/example/shader_editor/shader_editor.html
varying vec2 uv; //http://www.kickjs.org/example/shader_editor/shader_editor.html

void main()
{
    // Setting Each Pixel To Red
    //gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
    
    //correct normal, and compute light vector (assume light at the eye)
    vec4 vNormal = normalize( normal_mat * normal_vec ) ;
    vec4 v_light = normalize( vec4(0,0,0,1) - vertex_pos );
    //reflectance based on lamberts law of cosine
    float theta = clamp(dot(vNormal, v_light), 0.02, 1.0);
    vec4 color = texture2D(tex, uv_vec);
    ///gl_FragColor = vec4(theta, theta, theta, 1.0); //normal-only
    gl_FragColor = vec4(theta, theta, theta, 1.0) * camera_light_multiplier * color;
    
    //below is from http://www.kickjs.org/example/shader_editor/shader_editor.html
    //float diffuse = max(0.0,dot(normalize(n),_world_light_dir_eye_space));
    //gl_FragColor = vec4(texture2D(tex,uv).xyz*diffuse,1.0);
    
}
''')
#---END SHADERS-------------------------------------------------------

    viewer = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(ShaderEditor, self).__init__(**kwargs)
        self.test_canvas = RenderContext()
        s = self.test_canvas.shader
        self.trigger_compile = Clock.create_trigger(self.compile_shaders, -1)
        self.bind(fs=self.trigger_compile, vs=self.trigger_compile)
    
    def compile_shaders(self, *largs):
        print('try compile')
        if not self.viewer:
            return
        fs = self.fs  # fs_header + self.fs
        vs = self.vs  # vs_header + self.vs
        print('-->', fs)
        self.viewer.fs = fs
        print('-->', vs)
        self.viewer.vs = vs
    
    def update_vs_to_vs_codeinput(self, instance, value):
        #self.vs = self.vs_codeinput.text
        self.vs = value  # self.vs_codeinput.text
        print("update_vs_to_vs_codeinput")
        
    def update_fs_to_fs_codeinput(self, instance, value):
        #self.fs = self.fs_codeinput.text
        self.fs = value  # self.fs_codeinput.text
        print("update_fs_to_fs_codeinput")

    def interruptClick(self, instance):
        instance.disabled = True
        instance.opacity = 0.0
        continueButton = Factory.Button(text="Continue", id="continueButton")
        popup = Factory.Popup(
            title="The button is gone.",
            size_hint=(.25, .25),
            content=continueButton,
            auto_dismiss=False
            )
        continueButton.bind(on_press=popup.dismiss)
        popup.open()

form=None

class ShaderViewer(FloatLayout):
    fs = StringProperty(None)
    vs = StringProperty(None)

    def __init__(self, **kwargs):
        self.canvas = RenderContext()
        super(ShaderViewer, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_shader, 0)

    def update_shader(self, *args):
        s = self.canvas
        s['projection_mat'] = Window.render_context['projection_mat']
        s['time'] = Clock.get_boottime()
        s['resolution'] = list(map(float, self.size))
        #if form.viewer.pos is not None:
        form.image_rect.pos=form.viewer.pos
        #if form.viewer.size is not None:
        form.image_rect.size=form.viewer.size
        form.vs_label.height=form.vs_label.texture_size[1] + 10
        form.fs_label.height=form.fs_label.texture_size[1] + 10
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
        example_path = 'richmond-bridge-512x512-rgba-CC0.png'
        if len(sys.argv) > 1:
            kwargs['source'] = sys.argv[1]
        form = ShaderEditor(**kwargs)
        if (not (os.path.isfile(form.source))) and os.path.isfile(example_path):
            form.source = example_path
        print("using image: '"+form.source+"'")
        form.main_layout = Factory.BoxLayout(orientation="horizontal")
        form.add_widget(form.main_layout)
        form.input_layout = Factory.BoxLayout(orientation="vertical")

        form.vs_label = Factory.Label(text='Vertex Shader', size_hint_y=None)
        form.vs_label.height=form.vs_label.texture_size[1] + 10
        form.input_layout.add_widget(form.vs_label)
        form.vs_codeinput = Factory.CodeInput(text=form.vs)
        form.vs_codeinput.lexer=GLShaderLexer()
        form.vs_codeinput.bind(text=form.update_vs_to_vs_codeinput)  # on_text=root.vs = args[1]
        form.input_layout.add_widget(form.vs_codeinput)
        
        form.fs_label = Factory.Label(text='Fragment Shader', size_hint_y=None)
        form.fs_label.height=form.fs_label.texture_size[1] + 10
        form.input_layout.add_widget(form.fs_label)
        form.fs_codeinput = Factory.CodeInput(text=form.fs)
        form.fs_codeinput.lexer=GLShaderLexer()
        form.fs_codeinput.bind(text=form.update_fs_to_fs_codeinput)  # on_text=root.fs = args[1]
        form.input_layout.add_widget(form.fs_codeinput)
        
        form.viewer = Factory.ShaderViewer()
        form.image_color = Color(1.0,1.0,1.0,1.0)
        form.viewer.canvas.add(form.image_color)
        #form.viewer.canvas.add(Factory.Rectangle(pos=form.viewer.pos, size=form.viewer.size, source=form.source))
        form.image_rect = Factory.Rectangle(pos=(200,0), size=(512,512), source=form.source)
        form.viewer.canvas.add(form.image_rect)
        form.main_layout.add_widget(form.input_layout)
        form.main_layout.add_widget(form.viewer)
        
        #form.cols = 1
        #form.orientation = "vertical"
        #form.okButton = Factory.Button(text="Hide Button", id="okButton")
        #form.add_widget(form.okButton)
        #form.okButton.bind(on_press=form.interruptClick)
        return form

if __name__ == '__main__':
    Imperative_ShaderEditorApp().run()

