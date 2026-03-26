# Project Structure

Character data lives in the project directory (not in this skill):

```
project-root/
├── characters.json              # Registry: maps names → folders
├── muffin/                      # One folder per character
│   ├── config.json              # Character description + prompt template
│   └── *.png / *.jpg            # Reference images
├── talala/
│   ├── config.json              # Includes style_options with Feishu prompts
│   └── *.png
└── output/                      # Generated images land here
```

## characters.json (Registry)

Maps character names (including aliases) to their folder:

```json
{
  "characters": {
    "嗒啦啦": { "dir": "talala", "aliases": ["talala", "嗒拉拉", "塔啦啦", "dalalala"] },
    "麦芬": { "dir": "muffin", "aliases": ["muffin", "gogo muffin", "GOGO麦芬"] }
  }
}
```

Matching is case-insensitive. Check both primary name and all aliases.

## config.json 标准规范

所有角色的 config.json 必须遵循以下字段规则：

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | ✅ | 角色中文名 |
| `name_en` | ✅ | 角色英文名 |
| `style_options` | ✅ | 风格配置，至少一个 |
| `style_reference_images` | ✅ | 每个风格对应的参考图列表 |
| `reference_images` | ✅ | 兜底参考图（无匹配风格时使用） |
| `require_style_selection` | 可选 | 多风格角色设为 true，单风格可省略 |
| `reference_roles` | 可选 | 给参考图加语义标签（expression/proportions 等） |

**`style_options` 每个条目：**
- `label`：展示给用户看的选项名称
- `style_key`：与 `style_reference_images` 的 key 对应
- `style_prompt`：完整提示词，末尾留逗号，场景会自动拼接在后面

---

## config.json (Standard character)

```json
{
  "name": "麦芬",
  "name_en": "Muffin",
  "description": "A cute chibi fox character...",
  "prompt_template": "Generate an image of {name}... Art style: {style}. Scene: {scene}",
  "default_style": "2D cartoon illustration, soft cel-shading, warm colors",
  "reference_images": ["麦芬01.png", "麦芬02.png"],
  "style_reference_images": {
    "2d": ["麦芬01.png", "麦芬02.png"],
    "3d": ["麦芬09.png"]
  }
}
```

## config.json (Character with style selection — e.g. 嗒啦啦)

When `require_style_selection: true`, the workflow pauses to ask the user to pick a style before generating.

```json
{
  "name": "嗒啦啦",
  "require_style_selection": true,
  "style_options": {
    "平涂": {
      "label": "平涂（极简平涂 · 无描边 · 矢量艺术）",
      "style_key": "平涂",
      "style_prompt": "一个绝美的嗒啦啦iP形象，保持图1角色的画面风格..."
    },
    "厚涂": {
      "label": "厚涂（手绘纹理 · 厚涂笔触 · 高扎单马尾）",
      "style_key": "厚涂",
      "style_prompt": "一个可爱的塔啦啦iP形象，保持图1角色的画面风格..."
    },
    "3D": {
      "label": "3D（手办质感 · 哑光橡胶）",
      "style_key": "3d",
      "style_prompt": "一个绝美的嗒啦啦iP形象...3D渲染..."
    }
  },
  "style_reference_images": {
    "平涂": ["嗒啦啦-平涂.png"],
    "厚涂": ["嗒啦啦-厚涂.png"],
    "3d": ["嗒啦啦-3D.png"]
  }
}
```

`style_prompt` is used as the full prompt override — passed directly to Gemini without translation. The reference image becomes "图1" in the prompt context.

## Environment Requirements

- `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variable must be set
- Python 3.10+ with `google-genai` package (`pip install google-genai`)
- Reference images: PNG or JPG, 512px–2048px recommended
