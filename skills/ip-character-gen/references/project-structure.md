# Project Structure

Character data lives in the project directory (not in this skill):

```
project-root/
├── characters.json              # Registry: maps names → folders
├── styles.json                  # Global style definitions (平涂/厚涂/3D/2D)
├── muffin/                      # One folder per character
│   ├── config.json              # Character description + prompt template
│   └── *.png / *.jpg            # Reference images
├── talala/
│   ├── config.json
│   └── *.png
├── pululu/                      # 噗噜噜 — 机器人角色
│   ├── config.json
│   └── *.png
├── xinghuo/                     # 星星火 — 火焰角色（参考图待补充）
│   └── config.json
└── output/                      # Generated images land here
```

## characters.json (Registry)

Maps character names (including aliases) to their folder:

```json
{
  "characters": {
    "嗒啦啦": { "dir": "talala", "aliases": ["talala", "嗒拉拉", "塔啦啦", "塔啦拉", "嗒啦拉", "塔拉拉", "dalalala", "tarara"] },
    "麦芬": { "dir": "muffin", "aliases": ["muffin", "gogo muffin", "GOGO麦芬", "麦芬猫"] },
    "噗噜噜": { "dir": "pululu", "aliases": ["pululu", "噗鲁鲁", "噗噜鲁"] },
    "星星火": { "dir": "xinghuo", "aliases": ["xinghuo", "星火"] }
  }
}
```

Matching is case-insensitive. Check both primary name and all aliases.

## config.json 标准规范

角色 config 采用三层分离设计：角色身份（anchor/description）、参考图约束（ref_constraint）、美术风格（styles.json）各自独立，prompt 拼接时才合并。

| 字段 | 必填 | 层级 | 说明 |
|------|------|------|------|
| `name` | ✅ | 身份 | 角色中文名 |
| `name_en` | ✅ | 身份 | 角色英文名 |
| `anchor` | ✅ | 身份 | 一句话定义角色（如"一个绝美的嗒啦啦IP形象"） |
| `description` | ✅ | 身份 | 角色外观细节（如"黄色腮红，白色符号眼睛"），无则留空字符串 |
| `ref_constraint` | ✅ | 约束 | 参考图约束（告诉模型如何参照参考图） |
| `available_styles` | ✅ | 风格 | 该角色支持的风格列表，对应 `styles.json` 的 key |
| `default_style` | 可选 | 风格 | 默认风格（单风格角色建议填写） |
| `require_style_selection` | 可选 | 风格 | 多风格角色设为 true，用户必须先选风格 |
| `primary_reference` | 可选 | 参考图 | 主参考图文件名 |
| `reference_images` | ✅ | 参考图 | 兜底参考图列表 |
| `style_reference_images` | 可选 | 参考图 | 每个风格对应的参考图列表 |
| `reference_roles` | 可选 | 参考图 | 给参考图加语义标签（expression/proportions 等） |

---

## config.json 示例

**多风格角色（嗒啦啦）：**
```json
{
  "name": "嗒啦啦",
  "name_en": "Dalalala",
  "anchor": "一个绝美的嗒啦啦iP形象",
  "description": "",
  "ref_constraint": "保持图1角色的画面风格、精致细节、人物身材比例完全一致，为该IP设计全新形象，服装风格与图1风格保持一致。",
  "require_style_selection": true,
  "available_styles": ["平涂", "厚涂", "3D"],
  "reference_images": ["嗒啦啦-平涂.png", "嗒啦啦-厚涂.png", "嗒啦啦-3D.png"],
  "style_reference_images": { "平涂": ["嗒啦啦-平涂.png"], "厚涂": ["嗒啦啦-厚涂.png"], "3d": ["嗒啦啦-3D.png"] }
}
```

**单风格角色（麦芬）：**
```json
{
  "name": "麦芬",
  "name_en": "Muffin",
  "anchor": "一个可爱的麦芬猫咪IP形象",
  "description": "尾巴形状严格参照参考图",
  "ref_constraint": "保持图1的画面风格、颜色细节、角色比例完全一致，生成图1的IP形象。",
  "available_styles": ["2D"],
  "default_style": "2D",
  "reference_images": ["麦芬15.png", "麦芬02.png", "麦芬08.png"],
  "reference_roles": { "expression": ["麦芬02.png"], "proportions": ["麦芬08.png"] }
}
```

**共用参考图角色（噗噜噜）：**
```json
{
  "name": "噗噜噜",
  "name_en": "Pululu",
  "anchor": "一个机器人IP形象",
  "description": "黄色圆形腮红，白色符号眼睛（n n型）",
  "ref_constraint": "保持图1的画面风格、颜色细节、角色比例完全一致，生成图1的IP形象。",
  "available_styles": ["平涂", "厚涂", "3D"],
  "default_style": "平涂",
  "reference_images": ["噗噜噜-平涂.png"],
  "style_reference_images": { "平涂": ["噗噜噜-平涂.png"], "厚涂": ["噗噜噜-平涂.png"], "3d": ["噗噜噜-平涂.png"] }
}
```

## styles.json（全局风格库）

风格定义独立于角色，所有角色共享。`description` 用于拼接提示词，`suffix` 附加在风格描述之后。

```json
{
  "平涂": {
    "label": "平涂（极简平涂 · 无描边 · 矢量艺术）",
    "description": "大师级别插画设计，无描边插画，矢量艺术，极简平涂...",
    "suffix": "灵巧的动作设计。"
  }
}
```

## Environment Requirements

- `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variable must be set
- Python 3.10+ with `google-genai` package (`pip install google-genai`)
- Reference images: PNG or JPG, 512px–2048px recommended
