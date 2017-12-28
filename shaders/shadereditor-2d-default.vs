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
