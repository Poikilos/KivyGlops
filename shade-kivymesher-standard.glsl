---VERTEX SHADER-------------------------------------------------------
//according to http://nehe.gamedev.net/article/glsl_an_introduction/25007/
//vertex shader replaces all vertex functions in the fixed-function OpenGL pipeline, so you would (as standard practice) do your own:
// * Vertex Transformation
// * Normal Transformation, Normalization and Rescaling
// * Lighting
// * Texture Coordinate Generation and Transformation

// "Attributes are only available in vertex shader and they are input values which change every vertex, for example the vertex position or normals. Attributes are read-only."
// gl_Vertex				4D vector representing the vertex position
// gl_Normal				3D vector representing the vertex normal
// gl_Color				4D vector representing the vertex color
// gl_MultiTexCoordX			4D vector representing the texture coordinate of texture unit X

// There are some other built-in attributes, see reference [2], page 41 for a full list.

// GLSL also has some built-in uniforms:

// gl_ModelViewMatrix			4x4 Matrix representing the model-view matrix.
// gl_ModelViewProjectionMatrix		4x4 Matrix representing the model-view-projection matrix.
// gl_NormalMatrix				3x3 Matrix representing the inverse transpose model-view matrix.
					// This matrix is used for normal transformation.

// There are some other built-in uniforms, like lighting states. See reference [2], page 42 for a full list.
// GLSL Built-In Varyings:

// gl_FrontColor				4D vector representing the primitives front color
// gl_BackColor				4D vector representing the primitives back color
// gl_TexCoord[X]				4D vector representing the Xth texture coordinate

// There are some other built-in varyings. See reference [2], page 44 for a full list.

// And last but not least there are some built-in types which are used for shader output:

// gl_Position				4D vector representing the final processed vertex position. Only 
					// available in vertex shader.
// gl_FragColor				4D vector representing the final color which is written in the frame 
					// buffer. Only available in fragment shader.
// gl_FragDepth				float representing the depth which is written in the depth buffer.
					// Only available in fragment shader.
// The importance of built-in types is that they are mapped to the OpenGL states. For example if you call glLightfv(GL_LIGHT0, GL_POSITION, my_light_position) this value is available as a uniform using gl_LightSource[0].position in a vertex and/or fragment shader.
#ifdef GL_ES
    precision highp float;
#endif

attribute vec3  v_pos;
attribute vec3  v_normal;
attribute vec4  v_color;
attribute vec2  v_tc0;

uniform mat4 modelview_mat;
uniform mat4 projection_mat;

varying vec4 normal_vec;
varying vec4 vertex_pos;
uniform mat4 normal_mat; //normal-only
varying vec4 frag_color;
varying vec2 uv_vec;


varying vec2 uv; //http://www.kickjs.org/example/shader_editor/shader_editor.html
varying vec3 n; //http://www.kickjs.org/example/shader_editor/shader_editor.html


void main()
{
    //compute vertex position in eye_sapce and normalize normal vector
    vec4 pos = modelview_mat * vec4(v_pos,1.0);
    vertex_pos = pos;
    normal_vec = vec4(v_normal,0.0);
    //gl_Position = projection_mat * pos;
	
    // Transforming The Vertex
    /* gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex; this is the c++ way*/
    //vec4 pos = modelview_mat * vec4(v_pos,1.0);
    gl_Position = projection_mat * pos;
    frag_color = v_color;
    uv_vec = v_tc0;

	uv = v_tc0; //uv = uv1; //http://www.kickjs.org/example/shader_editor/shader_editor.html
	
	
	// compute light info
	//n = normalize (normal_mat * normal_vec); //n = normalize(_norm * normal); //http://www.kickjs.org/example/shader_editor/shader_editor.html
	
}

---FRAGMENT SHADER----------------------------------------------------
#ifdef GL_ES
    precision highp float;
#endif
//according to http://nehe.gamedev.net/article/glsl_an_introduction/25007/
//fragment shader replaces all fragment functions in the fixed-function OpenGL pipeline, so you would (as standard practice) do your own:
// * Texture access and application (Texture environments)
// * Fog
// sampler types (have to be declared uniform [which is read-only])
//sampler1D, sampler2D, sampler3D		1D, 2D and 3D texture
//samplerCube							Cube Map texture
//sampler1Dshadow, sampler2Dshadow	1D and 2D depth-component texture

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
uniform vec3 world_light_dir_eye_space;

varying vec3 n; //http://www.kickjs.org/example/shader_editor/shader_editor.html
varying vec2 uv; //http://www.kickjs.org/example/shader_editor/shader_editor.html

void main()
{
    // Setting Each Pixel To Red
    //gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
	
    //correct normal, and compute light vector (assume light at the eye)
    vec4 v_normal = normalize( normal_mat * normal_vec ) ;
    vec4 v_light = normalize( vec4(0,0,0,1) - vertex_pos );
    //reflectance based on lamberts law of cosine
    float theta = clamp(dot(v_normal, v_light), 0.0, 1.0);
	vec4 color = texture2D(tex, uv_vec);
    ///gl_FragColor = vec4(theta, theta, theta, 1.0); //normal-only
	gl_FragColor = vec4(theta, theta, theta, 1.0) * camera_light_multiplier * color;
	
	//below is from http://www.kickjs.org/example/shader_editor/shader_editor.html
	//float diffuse = max(0.0,dot(normalize(n),world_light_dir_eye_space));
	//gl_FragColor = vec4(texture2D(tex,uv).xyz*diffuse,1.0);
	
}
