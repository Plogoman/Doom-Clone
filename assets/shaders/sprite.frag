#version 330 core

in vec2 TexCoord;

out vec4 FragColor;

uniform sampler2D textureSampler;

void main() {
    vec4 texColor = texture(textureSampler, TexCoord);

    // Discard fully transparent pixels
    if (texColor.a < 0.1)
        discard;

    FragColor = texColor;
}
