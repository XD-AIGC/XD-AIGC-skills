# XD-AIGC-skills

TapTap XD 团队的 AIGC 技能库。

## 这是什么？

这个仓库存放的是 **AI Skill**（AI 技能） — 一种让 AI 编程助手（如 Claude Code、Gemini CLI、Cursor）自动完成特定任务的配置包。

你可以把 Skill 理解为 AI 的"工作手册"：它告诉 AI **做什么、怎么做、用什么素材**，AI 读取后就能自动执行，不需要你每次手动写提示词。

## 仓库里有哪些 Skill？

| Skill | 做什么 | 触发方式 |
|-------|--------|----------|
| [ip-character-gen](#ip-character-gen--ip-角色图片生成) | 生成 IP 角色插画 | `画嗒啦啦在海边玩水` |
| [submit-xd-ailab](#submit-xd-ailab--ai-实验室工具提交) | 提交工具到 AI 实验室 | `帮我提交工具` |

---

## ip-character-gen — IP 角色图片生成

通过角色参考图 + 场景描述，调用 Google Gemini API 生成风格一致的角色插画。支持单角色生成和多角色合图。

### 支持的角色

| 角色 | 说明 | 可用风格 |
|------|------|----------|
| 嗒啦啦 | 绝美 IP 形象，高扎单马尾，Q版 3.5 头身 | 平涂 / 厚涂 / 3D |
| 麦芬 | 可爱猫咪 IP | 2D |
| 噗噜噜 | 机器人 IP，黄色腮红，符号眼睛 | 平涂 / 厚涂 / 3D |
| 星星火 | 灵动火焰 | 平涂 / 厚涂 / 3D |

### 怎么用

在 Claude Code 里直接说自然语言：

```
画嗒啦啦在海边玩水，平涂风格
画麦芬在森林里探险
噗噜噜在操场打球，厚涂风格
画嗒啦啦和麦芬一起在公园野餐，平涂风格
```

AI 会自动：
1. 识别角色名 → 加载对应的参考图和角色配置
2. 识别风格 → 加载对应的美术风格提示词
3. 拼接三层 Prompt（角色 + 风格 + 场景）→ 调用 Gemini API 生图
4. 输出图片路径

### 核心设计：三层分离

```
┌─────────────────────────────────────────────┐
│ 角色层（每个角色独立）                         │
│  anchor:        "一个绝美的嗒啦啦iP形象"      │
│  description:   "高扎单马尾"                  │
│  refConstraint: "保持图1角色的画面风格..."      │
├─────────────────────────────────────────────┤
│ 风格层（所有角色共享，只应用一次）              │
│  keywords: "大师级别插画设计，无描边插画..."     │
│  suffix:   "灵巧的动作设计。"                  │
├─────────────────────────────────────────────┤
│ 场景层（用户输入）                             │
│  "在公园野餐"                                 │
└─────────────────────────────────────────────┘
```

**为什么这样设计？** 嗒啦啦原生是平涂/厚涂/3D 风格，麦芬原生是 2D 风格。当它们合到一张图时，需要统一成一种美术风格。三层分离让角色描述和美术风格互不干扰，多角色合图时只应用一种风格，画面统一。

### 添加新角色

1. 在 `skills/ip-character-gen/assets/` 下创建角色目录（如 `newchar/`）
2. 放入参考图（PNG/JPG，建议 512-2048px）
3. 创建 `config.json`：

```json
{
  "name": "新角色",
  "key": "newchar",
  "aliases": ["新角色", "newchar"],
  "anchor": "一个[角色描述]的IP形象",
  "description": "具体外观细节（可为空）",
  "referenceImage": {
    "flat": "新角色-平涂.png",
    "impasto": "新角色-厚涂.png",
    "3d": "新角色-平涂.png"
  },
  "refConstraint": "保持图1的画面风格、颜色细节、角色比例完全一致，生成图1的IP形象。"
}
```

4. 在 `characters.json` 中注册：

```json
"新角色": { "dir": "newchar", "aliases": ["newchar"] }
```

5. 测试：`画新角色在[场景]`

### 添加新风格

在 `styles.json` 中添加：

```json
"watercolor": {
  "name": "水彩",
  "nameEn": "Watercolor",
  "key": "watercolor",
  "keywords": "水彩画风格，柔和的色彩晕染...",
  "suffix": "灵巧的动作设计。"
}
```

---

## submit-xd-ailab — AI 实验室工具提交

帮助外部贡献者将工具接入 XD-AIGC AI 实验室平台。自动完成分类、`tool.yaml` 生成、代码规范检查、配置生成和 PR 创建。

### 工具分类

| 类型 | 适用场景 | 示例 |
|------|----------|------|
| C1 | 纯前端，无需后端 | 静态 HTML/JS 工具，Nginx 直接托管 |
| C2 | ComfyUI 工作流 | 共享 comfyui-proxy |
| C3 | 轻量 API 调用 | 共享 FastAPI api-server |
| C4 | 重型/自定义后端 | 独立端口 + watchdog 监控 |

### 怎么用

```
我要上传到 AI 实验室
帮我提交工具
```

AI 会引导你完成：分类 → 生成 tool.yaml → 检查代码 → 生成配置 → 创建 PR

---

## 项目结构

```
XD-AIGC-skills/
├── skills/
│   ├── ip-character-gen/              # IP 角色图片生成
│   │   ├── SKILL.md                   # Skill 入口（AI 读取此文件）
│   │   ├── assets/
│   │   │   ├── characters.json        # 角色注册表
│   │   │   ├── styles.json            # 风格库
│   │   │   ├── talala/                # 嗒啦啦：config + 参考图
│   │   │   ├── muffin/               # 麦芬
│   │   │   ├── pululu/               # 噗噜噜
│   │   │   └── xinghuo/              # 星星火
│   │   ├── scripts/
│   │   │   └── generate_image.py      # 生图脚本
│   │   └── references/                # 补充文档
│   └── submit-xd-ailab/              # AI 实验室工具提交
│       ├── SKILL.md
│       └── references/
│           └── tool-yaml-spec.md      # tool.yaml 字段规范
├── CLAUDE.md                          # AI 工具读取的项目约定
├── .env.example                       # API key 配置模板
└── README.md                          # 你正在看的这个文件
```

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/XD-AIGC/XD-AIGC-skills.git
```

### 2. 配置 API Key（仅 ip-character-gen 需要）

```bash
cp .env.example .env
# 编辑 .env，填入你的 Google API Key
# 从 https://aistudio.google.com/apikey 获取
```

### 3. 安装依赖（仅 ip-character-gen 需要）

```bash
pip install google-genai python-dotenv
```

### 4. 安装 Skill 到 Claude Code

将 `skills/` 目录下的技能复制到 `~/.claude/skills/`：

```bash
cp -r skills/ip-character-gen ~/.claude/skills/
cp -r skills/submit-xd-ailab ~/.claude/skills/
```

或者在 Claude Code 的 `settings.json` 中配置 skill 路径指向本仓库。

### 5. 开始使用

在 Claude Code 中直接说：

```
画嗒啦啦在海边玩水，平涂风格
```

## 常见问题

**Q: 什么是 SKILL.md？**
A: 每个 Skill 的入口文件，AI 工具读取它来了解这个 Skill 的功能和使用流程。相当于 AI 的"使用说明书"。

**Q: 什么是 CLAUDE.md？**
A: Claude Code 读取的项目级配置文件，告诉 AI 这个项目的约定和规范。

**Q: API Key 过期了怎么办？**
A: 去 [Google AI Studio](https://aistudio.google.com/apikey) 创建新的 Key，更新 `.env` 文件。

**Q: 可以用其他 AI 工具吗？**
A: Skill 的核心是 SKILL.md（Markdown）+ config.json + Python 脚本，不依赖特定 AI 工具。Gemini CLI、Cursor 等支持 Skill 的工具都可以使用，可能需要适配 Skill 加载方式。

**Q: 生成的图片在哪？**
A: 默认保存在当前工作目录的 `output/` 文件夹下。
