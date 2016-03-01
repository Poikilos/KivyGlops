//from page 32 of https://www.khronos.org/assets/uploads/developers/library/siggraph2006/OpenKODE_Course/03_GLSL-for-OpenGL-ES.pdf
---VERTEX SHADER-------------------------------------------------------
uniform mat4 ModelViewProjectionMatrix, NormalMatrix;
uniform vec4 LightSourceDiffuse, LightSourcePosition, MaterialDiffuse;
attribute vec4 InputPosition, InputNormal, InputTextureCoordinates;
varying vec4 VertexColour;
varying vec4 TextureCoordinates;

void main() 
{
	vec3 normal, lightDirection;
	vec4 diffuse;
	float NdotL;
	
	normal = normalize(NormalMatrix * Normal); 
	lightDirection = normalize(vec3(LightSourcePosition)); 
	NdotL = max(dot(normal, lightDirection), 0.0);
	diffuse = MaterialDiffuse * LightSourceDiffuse;
	VertexColor = NdotL * diffuse;
	
	TextureCoordinates = InputTextureCoordinates;
	
	gl_Position = ModelViewProjectionMatrix * position;
} 

---FRAGMENT SHADER-----------------------------------------------------

uniform sampler2D TextureHandle;
varying vec2 TextureCoordinates;
varying vec4 VertexColour;
void main()
{ 
	vec4 texel = texture2D (TextureHandle, TextureCoordinates);
	gl_FragColor = texel * VertexColour;
} 