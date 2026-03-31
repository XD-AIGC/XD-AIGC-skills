# XD-AIGC-skills

AIGC 技能库，存放供 AI 编程工具调用的 Skill。

## 技能

### ip-character-gen
IP 角色图片生成。角色 config.json 遵循 TapIP 标准格式：`anchor` / `description` / `referenceImage` / `refConstraint`。风格 styles.json 使用英文 key（flat / impasto / 3d / 2d），字段为 `keywords` + `suffix`。角色描述与美术风格三层分离，prompt 拼接时才合并。

### submit-xd-ailab
XD-AIGC AI 实验室工具提交助手。工具分 C1-C4 四类，通过 `tool.yaml` 驱动配置生成。流程：分类 → tool.yaml → 代码检查 → 配置生成 → 封面图 → PR。

## 环境

- Python 3.10+，依赖：`google-genai`、`python-dotenv`
- API key 配置在 `.env`（不入库），模板见 `.env.example`
