---
name: ip-character-gen
description: "Generate images of cartoon IP characters using Gemini image generation. Use this skill whenever the user mentions a character name with a scene or action (e.g., 嗒啦啦在海边玩水, 麦芬在海边散步, 画嗒啦啦厚涂风格, draw muffin playing guitar), wants to generate character artwork in any style (平涂/厚涂/3D), or asks to write character copy/introductions. Registered characters include 嗒啦啦 (talala), 麦芬 (muffin). Trigger immediately when you see any of these character names combined with any creative task — drawing, styling, writing about them. Do NOT trigger for updating reference files, formatting configs, comparing AI tools, or IP legal topics."
---

# IP Character Image Generator

Generate consistent cartoon character images by combining character reference materials with scene descriptions, powered by Google Gemini's image generation.

For project structure, config formats, and environment setup → read `references/project-structure.md`
For conversation patterns, adding characters, and troubleshooting → read `references/conversation-patterns.md`

---

## Workflow

### Step 1: Identify Characters

Parse the user's message for character names. Check against `characters.json` registry (both primary names and aliases).

- **Single character found**: proceed directly
- **Multiple characters found**: load all of them
- **No character found**: ask the user, list available characters

### Step 2: Confirm and Clarify

**If `require_style_selection: true` in config**, always pause and show style options before generating:

> 找到角色「嗒啦啦」，请选择风格：
>
> 1. 平涂（极简平涂 · 无描边 · 矢量艺术）
> 2. 厚涂（手绘纹理 · 厚涂笔触 · 高扎单马尾）
> 3. 3D（手办质感 · 哑光橡胶）

Once the user picks, use `style_options[choice].style_key` as `--style` and `style_options[choice].style_prompt` as the prompt override.

**If no `require_style_selection`**, confirm briefly and proceed (or skip if intent is clear).

**Quick mode**: If the user already specified a style, skip selection and generate directly.

### Step 3: Construct the Prompt

- If the selected style has `style_prompt` in config → use it directly as the full prompt, append `\n\n场景：{scene}` at the end. No translation needed.
- Otherwise → translate scene to English, build prompt from `prompt_template` in config.

### Step 4: Generate

Character data (images + configs) are bundled inside the skill at `{skill_path}/assets/`.
Output images are saved to the user's current working directory under `output/`.

```bash
python {skill_path}/scripts/generate_image.py \
  --character "嗒啦啦" \
  --scene "在海边" \
  --project-root "{skill_path}/assets" \
  --output "{cwd}/output/" \
  --style "厚涂" \
  --model "gemini-3.1-flash-image-preview"
```

After generation, output the file path to the user. Do NOT use the Read tool to display the image — it wastes tokens and is not visible in CLI.

### Step 5: Iterate

- Happy → done
- Wants adjustments → modify prompt, regenerate
- Character looks wrong → try different reference images or emphasize consistency in prompt
