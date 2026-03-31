---
name: ip-character-gen
description: "Generate images of cartoon IP characters using Gemini image generation. Use this skill whenever the user mentions a character name with a scene or action (e.g., 嗒啦啦在海边玩水, 麦芬在海边散步, 噗噜噜在操场打球, 星星火在跳舞, 画嗒啦啦厚涂风格, draw muffin playing guitar), wants to generate character artwork in any style (平涂/厚涂/3D/2D), or asks to write character copy/introductions. Registered characters include 嗒啦啦 (talala), 麦芬 (muffin), 噗噜噜 (pululu), 星星火 (xinghuo). Trigger immediately when you see any of these character names combined with any creative task — drawing, styling, writing about them. Do NOT trigger for updating reference files, formatting configs, comparing AI tools, or IP legal topics."
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

### Step 2: Confirm Style

**Available styles** are defined in `{skill_path}/assets/styles.json` (平涂/厚涂/3D/2D).

**If any character has `require_style_selection: true`** (e.g. 嗒啦啦), always pause and show options from their `available_styles`:

> 找到角色「嗒啦啦」，请选择风格：
>
> 1. 平涂（极简平涂 · 无描边 · 矢量艺术）
> 2. 厚涂（手绘纹理 · 厚涂笔触）
> 3. 3D（手办质感 · 哑光橡胶）

**Multi-character scenes**: if characters have different `available_styles`, show the intersection (styles supported by all). User picks one unified style for the whole image.

**If user already specified style** or all characters have a `default_style`, skip selection.

### Step 3: Structured Prompt (handled by script)

The script `generate_image.py` builds a three-layer prompt automatically:

**Single character:**
```
[anchor]，[description]，              ← 角色层：角色身份 + 外观
[ref_constraint]                       ← 角色层：参考图约束
[style.description]                    ← 风格层：统一美术风格
[style.suffix]                         ← 风格层：动作/构图补充
[scene]                                ← 场景层
```

**Multi-character fusion:**
```
绝美的嗒啦啦与麦芬IP形象设计，          ← 角色层：融合开头
图1是嗒啦啦的角色参考，[ref_constraint]  ← 角色层：各角色独立约束
图2是麦芬的角色参考（[description]），[ref_constraint]
保持每个角色各自的形象...一起进行互动，
[style.description]                    ← 风格层：只出现一次，统一画面
[style.suffix]
[scene]                                ← 场景层
```

Key: character identity (anchor/description/ref_constraint) and art style (styles.json) are fully separated. Multi-character scenes apply ONE unified style regardless of each character's native style.

### Step 4: Generate

Character data is bundled at `{skill_path}/assets/`. Output saves to current working directory.

**Single character:**
```bash
python {skill_path}/scripts/generate_image.py \
  --character "嗒啦啦" \
  --scene "在海边" \
  --project-root "{skill_path}/assets" \
  --output "{cwd}/output/" \
  --style "厚涂" \
  --model "gemini-3-pro-image-preview"
```

**Multiple characters:**
```bash
python {skill_path}/scripts/generate_image.py \
  --characters "麦芬,嗒啦啦" \
  --scene "在公园野餐" \
  --project-root "{skill_path}/assets" \
  --output "{cwd}/output/" \
  --style "厚涂" \
  --model "gemini-3-pro-image-preview"
```

After generation, output the file path to the user. Do NOT use the Read tool to display the image — it wastes tokens and is not visible in CLI.

### Step 5: Iterate

- Happy → done
- Wants adjustments → modify prompt, regenerate
- Character looks wrong → try different reference images or emphasize consistency in prompt
