---VERTEX SHADER-------------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif

attribute vec3  v_pos;
attribute vec4  v_color;
attribute vec2  v_tc0;

uniform mat4 modelview_mat;
uniform mat4 projection_mat;

varying vec4 frag_color;
varying vec2 uv_vec;

struct VertextInput {
	float3 vertex : POSITION;
	float3 normal : NORMAL;
};
struct VertexOutput {
	float4 pos : SV_POSITION;
};

void main (void) {
    vec4 pos = modelview_mat * vec4(v_pos,1.0);
    gl_Position = projection_mat * pos;
    frag_color = v_color;
    uv_vec = v_tc0;
}


---FRAGMENT SHADER-----------------------------------------------------
//https://www.youtube.com/watch?v=WMHpBpjWUlY
#ifdef GL_ES
    precision highp float;
#endif

varying vec4 frag_color;
varying vec2 uv_vec;

uniform sampler2D tex;
//should have default sharpness above this
uniform _sharpness;


void main (void){
    vec4 color = texture2D(tex, uv_vec);
	float3 V = normalize( _WorldSpaceCameraPos.xyz - i.posWorld );
	float3 N = normalize( i.normalDir );
	float fresnel = pow( 1.0 - dot( N, V), _sharpness );
    gl_FragColor = color;
}