#version 330 core

in vec2 TexCoord;

out vec4 FragColor;

uniform sampler2D textureSampler;
uniform vec4 tintColor;

void main() {
    vec4 texColor = texture(textureSampler, TexCoord);
    FragColor = texColor * tintColor;
}
