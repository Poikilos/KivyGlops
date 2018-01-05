---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

attribute vec4  a_position;
attribute vec4  a_color;
attribute vec2  a_texcoord0;
attribute vec2  a_texcoord1;
attribute vec4  a_normal;

uniform mat4 modelview_mat;
uniform mat4 projection_mat;
uniform bool texture0_enable;
//uniform material  material_state;

varying vec4 v_color;
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
    v_color = a_color;
    uv_vec = a_texcoord0;
    v_normal = a_normal.xyz;
}


---FRAGMENT SHADER-----------------------------------------------------
//https://www.youtube.com/watch?v=WMHpBpjWUlY
#ifdef GL_ES
    precision highp float;
#endif

varying vec4 v_color;
varying vec2 uv_vec;
varying vec3 v_normal;
varying vec4 v_pos;
uniform vec3 camera_world_pos;
uniform bool texture0_enable;

uniform sampler2D tex;

//should have default sharpness otherwise must always set it in calling program
//uniform fresnel_sharpness; //uniform _sharpness;


void main (void){
    float default_fresnel_sharpness = .2;
    //if (fresnel_sharpness==null) {
        //fresnel_sharpness = default_fresnel_sharpness;
    //}
    float fresnel_sharpness = default_fresnel_sharpness;
    vec4 tex_color = texture2D(tex, uv_vec);
    vec4 color = v_color;
    if (texture0_enable) {
        if (tex_color.a>0.0) {
            color = mix(v_color, tex_color, tex_color.a);
        }
    }
    vec3 V = normalize( camera_world_pos.xyz - v_pos.xyz );  // normalize( _WorldSpaceCameraPos.xyz - i.posWorld );
    vec3 N = normalize(v_normal); //normalize( i.normalDir );
    float fresnel = pow( 1.0 - dot( N, V), fresnel_sharpness ); //pow( 1.0 - dot( N, V), _sharpness );
    vec4 fresnel_color = vec4(fresnel, fresnel, fresnel, 1.0);
    gl_FragColor = color * fresnel_color;
}
