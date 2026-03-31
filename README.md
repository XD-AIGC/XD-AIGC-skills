# XD-AIGC-skills

TapTap XD 团队的 AI 生成内容（AIGC）技能库，供 Claude Code / Gemini CLI 等 AI 编程工具使用。

## 技能列表

### ip-character-gen

IP 角色图片生成器 — 通过角色参考图 + 场景描述，调用 Google Gemini API 生成风格一致的角色插画。

**支持的角色：**

| 角色 | 风格 | 参考图 |
|------|------|--------|
| 嗒啦啦 (tarara) | 平涂 / 厚涂 / 3D | 3 张（按风格区分） |
| 麦芬 (muffin) | 2D | 3 张 |
| 噗噜噜 (pululu) | 平涂 / 厚涂 / 3D | 2 张（按风格区分） |
| 星星火 (xinghuo) | 平涂 / 厚涂 / 3D | 2 张（按风格区分） |

**核心设计 — 三层分离：**

```
角色层：anchor + description + refConstraint（每个角色独立）
风格层：keywords + suffix（从 styles.json 读取，统一应用）
场景层：用户输入的场景描述
```

角色描述与美术风格完全解耦，多角色合图时只应用一种统一风格。

**使用方式（Claude Code）：**

```
画嗒啦啦在海边玩水，平涂风格
画嗒啦啦和麦芬一起在公园野餐，平涂风格
```

详细文档见 [`skills/ip-character-gen/SKILL.md`](skills/ip-character-gen/SKILL.md)

---

### submit-xd-ailab

XD-AIGC AI 实验室工具提交助手 — 帮助外部贡献者将工具接入 AI 实验室平台，自动完成分类、`tool.yaml` 生成、代码规范检查、配置生成和 PR 创建。

**工具分类体系：**

| 类型 | 场景 | 示例 |
|------|------|------|
| C1 | 纯前端，Nginx 直接托管 | 静态 HTML/JS 工具 |
| C2 | ComfyUI 工作流 | 共享 comfyui-proxy |
| C3 | 轻量 API 调用 | 共享 FastAPI api-server |
| C4 | 重型/自定义后端 | 独立端口 + watchdog |

**工作流程：** 分类 → tool.yaml → 代码检查 → 配置生成 → 封面图 → PR

**使用方式（Claude Code）：**

```
我要上传到 AI 实验室
帮我提交工具
```

详细文档见 [`skills/submit-xd-ailab/SKILL.md`](skills/submit-xd-ailab/SKILL.md)

---

## 项目结构

```
XD-AIGC-skills/
├── skills/
│   ├── ip-character-gen/           # IP 角色图片生成
│   │   ├── SKILL.md                # Skill 入口（AI 工具读取此文件）
│   │   ├── assets/
│   │   │   ├── characters.json     # 角色注册表
│   │   │   ├── styles.json         # 风格库（flat/impasto/3d/2d）
│   │   │   ├── talala/             # 嗒啦啦：config.json + 参考图
│   │   │   ├── muffin/             # 麦芬：config.json + 参考图
│   │   │   ├── pululu/             # 噗噜噜：config.json + 参考图
│   │   │   └── xinghuo/            # 星星火：config.json + 参考图
│   │   ├── scripts/
│   │   │   └── generate_image.py   # 生图脚本（Gemini API）
│   │   └── references/
│   └── submit-xd-ailab/            # AI 实验室工具提交
│       ├── SKILL.md                # Skill 入口
│       └── references/
│           └── tool-yaml-spec.md   # tool.yaml 字段规范
├── CLAUDE.md                       # AI 工具项目约定
├── .env.example                    # API key 配置模板
└── README.md
```

## 配置格式

### 角色 config.json（TapIP 标准格式）

```json
{
  "name": "嗒啦啦",
  "key": "tarara",
  "aliases": ["嗒啦啦", "tarara"],
  "anchor": "一个绝美的嗒啦啦iP形象",
  "description": "",
  "referenceImage": {
    "flat": "嗒啦啦-平涂.png",
    "impasto": "嗒啦啦-厚涂.png",
    "3d": "嗒啦啦-平涂.png"
  },
  "refConstraint": "保持图1角色的画面风格、精致细节..."
}
```

| 字段 | 说明 |
|------|------|
| `anchor` | 角色身份，一句话定义"这是什么" |
| `description` | 角色外观细节（可为空） |
| `refConstraint` | 参考图约束（告诉模型怎么参照参考图） |
| `referenceImage` | 参考图路径，按风格 key 区分 |

### 风格 styles.json

```json
{
  "flat": {
    "name": "平涂",
    "nameEn": "Flat",
    "key": "flat",
    "keywords": "大师级别插画设计，无描边插画，矢量艺术...",
    "suffix": "灵巧的动作设计。"
  }
}
```

## 环境要求

- Python 3.10+
- `pip install google-genai python-dotenv`
- 在 `.env` 中设置 `GOOGLE_API_KEY`（从 [Google AI Studio](https://aistudio.google.com/apikey) 获取）

## 如何新增角色

1. 在 `assets/` 下创建角色目录，放入参考图
2. 创建 `config.json`，填写 `name`、`key`、`aliases`、`anchor`、`description`、`referenceImage`、`refConstraint`
3. 在 `characters.json` 中注册角色名和目录
4. 测试：`画[角色名]在[场景]`

## 如何新增风格

1. 在 `styles.json` 中添加新条目
2. 填写 `name`、`nameEn`、`key`、`keywords`、`suffix`
