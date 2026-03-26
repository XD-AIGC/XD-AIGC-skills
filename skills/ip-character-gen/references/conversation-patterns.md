# Conversation Patterns

## Common flows

**Simple generation:**
```
User: 麦芬在森林里探险
You: [confirm briefly] → [generate] → [show image]
```

**Style selection (嗒啦啦):**
```
User: 画嗒啦啦在海边
You: 找到角色「嗒啦啦」，请选择风格：
     1. 平涂 2. 厚涂 3. 3D
User: 2
You: [generate with 厚涂 style prompt] → [show image]
```

**Style specified upfront:**
```
User: 画平涂风格的嗒啦啦在咖啡馆
You: [skip selection, use 平涂 directly] → [generate]
```

**Multi-character:**
```
User: 麦芬和嗒啦啦一起在公园野餐
You: [load both characters] → [combine in prompt] → [generate]
```

**Iterative refinement:**
```
User: 表情再开心一点
You: [adjust prompt, re-generate]
```

**Unknown character:**
```
User: 小蓝在跳舞
You: 我在角色库中没有找到「小蓝」。目前已注册的角色有：嗒啦啦、麦芬
     要添加这个新角色吗？
```

## Adding New Characters

1. Create a new folder in project root (e.g., `annie/`)
2. Ask user to add reference images (3–5, different angles/poses)
3. Write `config.json` by analyzing the reference images
4. Add character to `characters.json` registry
5. Test with a simple generation

## Troubleshooting

- **API key error**: Check `GOOGLE_API_KEY` is set (`export GOOGLE_API_KEY=your-key` or `.env`)
- **Character not found**: Verify name/alias is in `characters.json`
- **Image quality issues**: Use fewer but higher-quality reference images; be more specific about art style in prompt
- **Model not available**: Default model is `gemini-3-pro-image-preview`. Check Google AI docs for current model name if unavailable.
