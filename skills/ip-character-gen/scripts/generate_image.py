#!/usr/bin/env python3
"""
IP Character Image Generator
Calls Google Gemini API with character reference images to generate scene illustrations.
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv


def load_image_as_base64(image_path: Path) -> tuple[str, str]:
    """Load an image file and return (base64_data, mime_type)."""
    suffix = image_path.suffix.lower()
    mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
    mime_type = mime_map.get(suffix, "image/png")
    with open(image_path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    return data, mime_type


def has_chinese(text: str) -> bool:
    """Check if text contains Chinese characters."""
    return any('\u4e00' <= ch <= '\u9fff' for ch in text)


def load_styles(assets_dir: Path) -> dict:
    """Load global styles from styles.json."""
    styles_path = assets_dir / "styles.json"
    if styles_path.exists():
        with open(styles_path) as f:
            return json.load(f)
    return {}


def resolve_style_key(style_input: str, styles: dict) -> str:
    """Resolve a style input (Chinese or English) to the styles.json key.

    Accepts: "平涂", "flat", "厚涂", "impasto", "3D", "3d", "2D", "2d"
    Returns: the key in styles.json (e.g. "flat", "impasto", "3d", "2d")
    """
    lower = style_input.lower()
    if lower in styles:
        return lower
    # Try matching by Chinese name
    for key, info in styles.items():
        if info.get("name") == style_input:
            return key
    return lower


def build_structured_prompt(characters: list[dict], style_key: str, scene: str, styles: dict) -> str:
    """
    Build a structured prompt with three separated layers:
    1. Character layer — anchor + description + refConstraint (per character)
    2. Style layer — keywords + suffix from styles.json (applied once)
    3. Scene layer — user's scene description
    """
    lines = []

    # === Character layer ===
    if len(characters) == 1:
        char = characters[0]
        char_identity = char["anchor"]
        if char.get("description"):
            char_identity += f"，{char['description']}"
        lines.append(char_identity + "，")
        lines.append(char.get("refConstraint", ""))
    else:
        names = "与".join(c["name"] for c in characters)
        lines.append(f"绝美的{names}IP形象设计，")
        for char in characters:
            desc_part = ""
            if char.get("description"):
                desc_part = f"（{char['description']}）"
            lines.append(f"图{char['index']}是{char['name']}的角色参考{desc_part}，{char.get('refConstraint', '')}")
        lines.append(f"保持每个角色各自的形象、精致细节、人物比例完全一致，{names}一起进行互动，")

    # === Style layer ===
    style_info = styles.get(style_key, {})
    keywords = style_info.get("keywords", style_key)
    suffix = style_info.get("suffix", "")
    lines.append(keywords)
    if suffix:
        lines.append(suffix)

    # === Scene layer ===
    lines.append(scene)

    return "\n".join(lines)


def select_reference_images(config: dict, char_dir: Path, style_key: str | None = None, max_refs: int = 5) -> list[tuple[Path, str]]:
    """Select reference images based on TapIP's referenceImage format.

    referenceImage can be:
    - string: single image for all styles
    - object: {style_key: filename_or_list} per style
    - null/missing: no reference images
    """
    ref_img = config.get("referenceImage")
    if not ref_img:
        return []

    if isinstance(ref_img, str):
        filenames = [ref_img]
    elif isinstance(ref_img, dict):
        value = ref_img.get(style_key) if style_key else None
        if value is None:
            # Fallback: use first available style's image
            value = next(iter(ref_img.values()), None)
        if value is None:
            return []
        filenames = value if isinstance(value, list) else [value]
    else:
        return []

    results = []
    for fn in filenames[:max_refs]:
        p = char_dir / fn
        if p.exists():
            results.append((p, "Character reference"))
    return results


def generate_image(
    character_names: list[str],
    scene: str,
    project_root: Path,
    output_dir: Path,
    style: str | None = None,
    model_name: str = "gemini-3-pro-image-preview",
    max_refs: int = 5,
    aspect_ratio: str = "1:1",
) -> Path:
    """Generate a character image using Gemini API."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: google-genai package not installed. Run: pip install google-genai", file=sys.stderr)
        sys.exit(1)

    # Load .env: check cwd first, then project root
    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        load_dotenv(cwd_env)
    else:
        env_path = project_root / ".env"
        if env_path.exists():
            load_dotenv(env_path)

    # Find API key
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    # Load registry
    registry_path = project_root / "characters.json"
    if not registry_path.exists():
        print(f"Error: Character registry not found at {registry_path}", file=sys.stderr)
        sys.exit(1)

    with open(registry_path) as f:
        registry = json.load(f)

    # Load styles
    styles = load_styles(project_root)

    # Find all characters
    characters_data = []
    for idx, character_name in enumerate(character_names, start=1):
        char_entry = None
        for name, entry in registry["characters"].items():
            if name == character_name or character_name.lower() in [a.lower() for a in entry.get("aliases", [])]:
                char_entry = entry
                break

        if not char_entry:
            available = ", ".join(registry["characters"].keys())
            print(f"Error: Character '{character_name}' not found. Available: {available}", file=sys.stderr)
            sys.exit(1)

        char_dir = project_root / char_entry["dir"]
        config_path = char_dir / "config.json"
        if not config_path.exists():
            print(f"Error: Character config not found at {config_path}", file=sys.stderr)
            sys.exit(1)

        with open(config_path) as f:
            config = json.load(f)

        characters_data.append({
            "name": config["name"],
            "key": config.get("key", ""),
            "index": idx,
            "anchor": config.get("anchor", config["name"]),
            "description": config.get("description", ""),
            "refConstraint": config.get("refConstraint", ""),
            "config": config,
            "char_dir": char_dir,
        })

    # Resolve style key (Chinese "平涂" or English "flat" → styles.json key)
    resolved_style = resolve_style_key(style, styles) if style else next(iter(styles), "flat")

    # Build structured prompt
    prompt_text = build_structured_prompt(
        [{"name": c["name"], "index": c["index"],
          "anchor": c["anchor"], "description": c["description"], "refConstraint": c["refConstraint"]}
         for c in characters_data],
        resolved_style,
        scene,
        styles,
    )
    print(f"Prompt:\n{prompt_text}\n", file=sys.stderr)

    # Select reference images for each character
    all_ref_images = []
    for char in characters_data:
        refs = select_reference_images(char["config"], char["char_dir"], resolved_style, max_refs)
        all_ref_images.extend(refs)
        print(f"{char['name']} reference images: {[(p.name, label) for p, label in refs]}", file=sys.stderr)

    # Build API request contents: images first, then prompt
    contents = []
    for ref_path, label in all_ref_images:
        img_data, mime_type = load_image_as_base64(ref_path)
        contents.append(types.Part.from_bytes(data=base64.standard_b64decode(img_data), mime_type=mime_type))
    contents.append(types.Part.from_text(text=prompt_text))

    # Call Gemini API
    client = genai.Client(api_key=api_key)
    print(f"Calling model: {model_name}...", file=sys.stderr)

    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
    )

    # Extract and save generated image
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    char_names = "_".join(c["name"] for c in characters_data)
    safe_scene = scene[:30].replace(" ", "_").replace("/", "_")
    output_filename = f"{char_names}_{safe_scene}_{timestamp}.png"
    output_path = output_dir / output_filename

    image_saved = False
    response_text = ""

    if response.candidates:
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                with open(output_path, "wb") as f:
                    f.write(part.inline_data.data)
                image_saved = True
                print(f"Image saved to: {output_path}", file=sys.stderr)
            elif part.text:
                response_text += part.text

    if response_text:
        print(f"Model response text: {response_text}", file=sys.stderr)

    if not image_saved:
        print("Error: No image was generated in the response.", file=sys.stderr)
        print(f"Full response: {response}", file=sys.stderr)
        sys.exit(1)

    print(str(output_path))
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate IP character images using Gemini")
    parser.add_argument("--character", help="Single character name (e.g., 麦芬)")
    parser.add_argument("--characters", help="Multiple character names, comma-separated (e.g., 麦芬,嗒啦啦)")
    parser.add_argument("--scene", required=True, help="Scene description (e.g., 在海边散步)")
    parser.add_argument("--project-root", required=True, help="Project root directory containing characters.json")
    parser.add_argument("--output", default=None, help="Output directory (default: project-root/output/)")
    parser.add_argument("--style", default=None, help="Art style: flat/平涂, impasto/厚涂, 3d/3D, 2d/2D")
    parser.add_argument("--model", default="gemini-3-pro-image-preview", help="Gemini model name")
    parser.add_argument("--max-refs", type=int, default=5, help="Maximum reference images per character")
    parser.add_argument("--aspect-ratio", default="1:1", help="Image aspect ratio")
    args = parser.parse_args()

    if not args.character and not args.characters:
        print("Error: Provide --character or --characters", file=sys.stderr)
        sys.exit(1)

    if args.characters:
        character_names = [c.strip() for c in args.characters.split(",")]
    else:
        character_names = [args.character]

    project_root = Path(args.project_root).resolve()
    output_dir = Path(args.output).resolve() if args.output else project_root / "output"

    generate_image(
        character_names=character_names,
        scene=args.scene,
        project_root=project_root,
        output_dir=output_dir,
        style=args.style,
        model_name=args.model,
        max_refs=args.max_refs,
        aspect_ratio=args.aspect_ratio,
    )


if __name__ == "__main__":
    main()
