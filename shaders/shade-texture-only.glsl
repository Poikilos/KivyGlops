---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

attribute vec4  a_position;
attribute vec4  a_color;
attribute vec4  a_texcoord0;

uniform mat4 modelview_mat;
uniform mat4 projection_mat;

varying vec4 frag_color;
varying vec2 uv_vec;

void main (void) {
    vec4 pos = modelview_mat * a_position; //vec4(v_pos,1.0);
    gl_Position = projection_mat * pos;
    frag_color = a_color;
    uv_vec = a_texcoord0;
}


---FRAGMENT SHADER-----------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

varying vec4 frag_color;
varying vec2 uv_vec;

uniform sampler2D tex;

void main (void){
    vec4 color = texture2D(tex, uv_vec);
    gl_FragColor = color;
}