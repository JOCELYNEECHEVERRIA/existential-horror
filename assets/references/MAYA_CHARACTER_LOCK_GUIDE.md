# Character Anchor Lock Specification: Maya (Hero Model Sheet)

## Character Concept & Visual Signature
- **Name**: Maya
- **Age**: 18
- **Facial Geometry**: Sharp chin, angular jawline, sunken undereye hollows, dark expressive pupils, thin expressive lips.
- **Hair**: Untamed shoulder-length jet black hair, parted slightly off-center, loose ink-drawn strands falling across temple and forehead.
- **Wardrobe**: Oversized pastel-yellow knitted crewneck sweater with heavy drop-shoulder ribbed seams, loose wool cuffs extending past wrists.
- **Aesthetic**: Dark graphic novel illustration, heavy Indian ink line art, muted cel-shading, 1990s anime film aesthetic, desaturated palette, 35mm film grain.

---

## Primary Character Model Sheet Prompt

### Prompt for Google Gemini / Imagen 3 / Midjourney
```text
Dark graphic novel illustration, heavy ink line art, muted cel-shading, 1990s anime film aesthetic, desaturated palette, 35mm film grain. Maya, 18-year-old girl, sharp chin, untamed shoulder-length jet black hair, oversized pastel-yellow knitted crewneck sweater, character turnaround sheet, front view, 3/4 view, and profile view, neutral background.
```

### Midjourney v6 / Niji 6 Flag Recommendations
```text
Dark graphic novel illustration, heavy ink line art, muted cel-shading, 1990s anime film aesthetic, desaturated palette, 35mm film grain. Maya, 18-year-old girl, sharp chin, untamed shoulder-length jet black hair, oversized pastel-yellow knitted crewneck sweater, character turnaround sheet, front view, 3/4 view, and profile view, neutral background --ar 16:9 --stylize 250 --chaos 0
```

### Negative Prompt (Anti-Trope & Artifact Filtering)
```text
bright neon colors, glossy 3D render, Pixar style, Disney style, photorealism, high saturation, smooth airbrushed skin, glowing eyes, extra limbs, distorted hands, distorted fingers, blurry linework.
```

---

## Face-Locking & Video Generation Workflow (Kling / Runway / Luma)
1. **Model Sheet Lock**:
   - Run the turnaround prompt above in Google Gemini / Imagen 3 or Midjourney.
   - Select the output with the crispest ink linework and clearest 3-view turnaround.
   - Save this image as `assets/references/maya_hero.png`.
2. **Keyframe Seeding (Flux / Midjourney)**:
   - When generating Beat 01 to Beat 06 keyframes, pass `maya_hero.png` as an image reference (`--cref maya_hero.png` in Midjourney or as reference in Flux IP-Adapter).
3. **Image-to-Video Animation (Kling / Runway Gen-3)**:
   - Upload the generated Beat Keyframe as the first frame.
   - Paste the corresponding motion prompt from `output/episodes/episode_01_the_birthday_loop/prompts_kling_runway.txt`.
   - Maya's face and yellow sweater will remain 100% consistent across every cut!
