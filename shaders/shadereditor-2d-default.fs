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
