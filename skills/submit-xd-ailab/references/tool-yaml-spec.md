# tool.yaml Field Reference

## Required Fields (all types)

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | kebab-case identifier, must match directory name under `tools/` |
| `name` | string | Chinese display name shown on Portal homepage |
| `description` | string | One-line description of what the tool does |
| `type` | enum | `C1` (pure frontend) \| `C2` (ComfyUI) \| `C3` (shared API) \| `C4` (independent service) |
| `author` | string | Tool author's name — always ask the user, never guess |

## Optional Fields (all types)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `icon` | string | `tool` | Portal card icon: `image` \| `cube` \| `activity` \| `edit` \| `link` |
| `scope` | enum | `public` | `public` \| `internal` (requires login) |
| `hidden` | bool | `false` | Hide from Portal homepage |
| `cover` | string | — | Cover image path, e.g. `/covers/my-tool.png` |
| `path` | string | `/<id>/` | Gateway URL path (override if different from id) |

## C3-Only Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `api_prefix` | string | **yes** | — | Route prefix in shared api-server, e.g. `/sprite-animator`. Must match `APIRouter(prefix=...)` in the route module |
| `rate_limit.generate` | string | no | — | API path that needs strict rate limiting (2r/m per IP), e.g. `/api/generate` |

## C4-Only Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `port` | int | **yes** | — | Service port. Start from 9001, increment. Check existing tools to avoid conflicts |
| `start_cmd` | string | **yes** | — | Command to start the service, e.g. `python server.py --port 9003` |
| `health_url` | string | no | PORT_CHECK | Health check path, e.g. `/api/health`. If omitted, watchdog checks port only |
| `conda_env` | string | no | `xd-aigc-toolbox` | Conda environment name for the start command |
| `websocket` | bool | no | `false` | Set `true` for Gradio or other WebSocket-dependent services |
| `rate_limit.generate` | string | no | — | API path that needs strict rate limiting (2r/m per IP), e.g. `/api/generate` |

## Example: C1 Tool

```yaml
id: color-remapper
name: 小镇场景色彩映射工具
description: 分色图色块映射换色、HSL 纹理保留
type: C1
author: Johnny.zxt
icon: image
cover: /covers/color-remapper.png
```

## Example: C3 Tool with Rate Limiting

```yaml
id: sprite-animator
name: 像素风格序列帧生成器
description: 图片序列帧动画预览与导出
type: C3
author: AJ
icon: activity
cover: /covers/sprite-animator.png
api_prefix: /sprite-animator
rate_limit:
  generate: /api/generate
```

## Example: C4 Tool with WebSocket

```yaml
id: my-service
name: 独立服务
description: 需要独立后端进程的工具
type: C4
author: DevName
port: 9003
start_cmd: python server.py --port 9003
health_url: /api/health
websocket: true
```

## Validation

Run `bash scripts/validate-tool-yaml.sh` to check:
- All required fields present
- `id` is valid kebab-case
- `type` is one of C1/C2/C3/C4
- C4 has `port` (numeric) and `start_cmd`
- `scope` is valid if present
- No duplicate ids across all tools
