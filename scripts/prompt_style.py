"""Shared prompt text for every generated video (owner, 2026-10-26: characters and settings must look photorealistic,
especially on the cheaper models). Video models on OpenRouter take no separate negative prompt, so the "no ..." list
lives inside the prompt. The presenter is described as fictional (not a real person) rather than "AI-generated":
the word pushed some models toward a synthetic look. Videos are still labelled as AI on TikTok.
"""

PRESENTER = "a fictional young adult woman (not any real person)"

REALISM = (
    "Photorealistic, indistinguishable from real iPhone footage filmed by a friend: real skin texture with visible "
    "pores and natural small imperfections, natural facial asymmetry, realistic individual hair strands and "
    "flyaways, anatomically correct hands with five fingers, natural blinking, true-to-life fabric texture, weight "
    "and creases, real-world lighting with soft natural shadows, a lived-in real home with ordinary everyday details, "
    "slight handheld camera movement and natural phone exposure. No CGI, 3D render, animation, illustration, "
    "painterly or airbrushed look; no plastic or waxy skin, no beauty filter, no over-smoothing, no glossy perfection; "
    "no warped, melting or morphing body parts or clothing, no extra fingers; no on-screen text, subtitles or logos."
)
