---
name: submit-xd-ailab
description: "帮助外部贡献者将工具提交到 XD-AIGC AI 实验室平台。自动完成分类、tool.yaml 生成、代码规范检查、配置生成、封面图、PR 创建。当用户提到上传、提交、接入 AI 实验室，或希望工具符合项目规范时触发。例如：'我要上传到 AI 实验室'、'帮我修正工具符合项目规范'、'提交工具'、'上架'、'submit tool'、'add my tool'。"
---

# Tool Onboarding

Get a tool onto the XD-AIGC platform: classify → tool.yaml → validate → configs → cover → PR.

## Step 1 — Classify

Ask what the tool does, then suggest a category. Confirm with the user before proceeding.

```
No backend needed?         → C1 (static files, nginx serves directly)
ComfyUI workflow?          → C2 (shared comfyui-proxy)
Light API calls?           → C3 (shared FastAPI api-server)
Heavy/custom backend?      → C4 (own port + watchdog)
```

When in doubt, start with C1 — upgrade later is easy, downgrade is hard.

## Step 2 — Create tool.yaml

Create `tools/<id>/tool.yaml`. This drives all auto-generated configs. For the complete field reference with examples, read `references/tool-yaml-spec.md`.

Minimal C1 example:
```yaml
id: my-tool
name: 我的工具
description: 一句话描述
type: C1
author: AuthorName    # always ask, never guess
icon: image
```

C4 tools also need: `port`, `start_cmd`, `health_url`. Check existing ports first: `grep -r 'port:' tools/*/tool.yaml`

## Step 3 — Review code (external imports only)

**Blocking:** remove `.env`, hardcoded keys, `__pycache__/`, `node_modules/`
**Non-blocking:** `ruff format` + `ruff check`; mivo_ui color tokens imported; C4 health endpoint

## Step 4 — Validate and generate

```bash
bash scripts/validate-tool-yaml.sh
bash scripts/sync-tools.sh
```

Generates: Portal cards (`tools-generated.js`), nginx routes (`tools-generated.conf`), watchdog entries (C4 only).

## Step 5 — Type-specific setup

- **C1:** Add volume mount in `gateway/docker-compose.yml` — sync-tools.sh does NOT do this automatically
  ```yaml
  - ../tools/<id>:/usr/share/nginx/html/<id>:ro
  ```
- **C2:** Place workflow JSON in `tools/<id>/workflows/`, follow per-client routing (see CLAUDE.md)
- **C3:** Add route module `shared/api-server/routes/<id>.py` with `APIRouter(prefix="/<id>")`; keys in `shared/api-server/.env`
- **C4:** See `/python-backend` for patterns (semaphore, to_thread, queue-status, health endpoint)

## Step 6 — Cover image + PR

Generate cover: invoke `/gen-tool-cover`

```bash
git checkout -b feat/<id>
git add tools/<id>/ tools/portal/src/data/ gateway/ shared/watchdog/
git commit -m "feat(<id>): add <tool name>"
git push -u origin feat/<id>
gh pr create --title "feat(<id>): add <tool name>" --body "..."
```

## Quick mode

User says "快速提交" or tool already has valid tool.yaml → validate + sync + cover + PR, skip code review.

## Watch out for

- **Port conflicts (C4):** always grep before assigning
- **C1 volume mount:** easy to forget, sync-tools.sh won't remind you
- **`tools/hy-motion/`:** git submodule, don't touch
- **Large files:** validator warns >5MB, discuss git LFS
- **Secrets:** never commit `.env` or API keys

## Always ask the user

- `author` — their identity, their choice
- `name` — Chinese display name, they know best
- `type` — your classification is a suggestion, they confirm
