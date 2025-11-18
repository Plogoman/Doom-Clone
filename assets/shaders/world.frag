#version 330 core

in vec2 TexCoord;
in vec3 FragPos;

out vec4 FragColor;

uniform sampler2D textureSampler;
uniform float lightLevel;

void main() {
    vec4 texColor = texture(textureSampler, TexCoord);

    // Apply lighting
    vec3 lit = texColor.rgb * lightLevel;

    FragColor = vec4(lit, texColor.a);
}
