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


def translate_scene_to_english(scene: str, api_key: str) -> str:
    """Translate Chinese scene description to English using Gemini."""
    from google import genai

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"Translate the following Chinese scene description to natural English. Only output the translation, nothing else:\n\n{scene}",
    )
    return response.text.strip()


def build_prompt(config: dict, scene: str, style: str | None = None, aspect_ratio: str = "1:1") -> str:
    """Build the generation prompt from character config and scene description."""
    name = config["name"]
    name_en = config.get("name_en", name)

    if style and style.lower() == "3d":
        style_direction = "3D rendered style"
    elif style and style.lower() == "2d":
        style_direction = config.get("default_style", "2D cartoon illustration")
    elif style:
        style_direction = style
    else:
        style_direction = config.get("default_style", "2D cartoon illustration")

    key_features = config.get("key_features", "")
    key_features_block = f"\n{key_features}\n" if key_features else ""

    prompt = f"""The reference images above show a character called {name_en} ({name}). Study these reference images carefully — every detail of the character's design matters: the exact shape, colors, outfit, accessories, proportions, and facial features.

Now generate a NEW illustration of this EXACT SAME character in the following scene:

Scene: {scene}

Style: {style_direction}
{key_features_block}
Rules:
- The character MUST look identical to the one in the reference images. Do not redesign or reinterpret the character.
- Do NOT include any of the reference images in the output. Generate a completely new scene.
- Keep the character's exact design: same outfit, same accessories, same color scheme, same proportions."""

    return prompt


def select_reference_images(config: dict, char_dir: Path, style: str | None = None, max_refs: int = 5) -> list[tuple[Path, str]]:
    """Select the best reference images for the given style. Returns list of (path, label)."""
    style_refs = config.get("style_reference_images", {})

    if style and style.lower() in style_refs:
        filenames = style_refs[style.lower()]
    elif "reference_images" in config:
        filenames = config["reference_images"]
    else:
        filenames = [f.name for f in sorted(char_dir.glob("*.png")) + sorted(char_dir.glob("*.jpg"))]

    # Build role labels from reference_roles config
    role_map = {}
    role_labels = {
        "art_style": "Art style reference",
        "proportions": "Character proportions reference",
        "back_view": "Back view / rear design reference",
        "front_view": "Front view reference",
        "expression": "Expression reference",
        "detail": "Detail reference",
    }
    for role, fns in config.get("reference_roles", {}).items():
        for fn in fns:
            role_map.setdefault(fn, []).append(role_labels.get(role, role))

    results = []
    for fn in filenames[:max_refs]:
        p = char_dir / fn
        if p.exists():
            labels = role_map.get(fn, [])
            label = " + ".join(labels) if labels else "Character reference"
            results.append((p, label))
    return results


def generate_image(
    character_name: str,
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

    # Find character
    char_entry = None
    char_key = None
    for name, entry in registry["characters"].items():
        if name == character_name or character_name.lower() in [a.lower() for a in entry.get("aliases", [])]:
            char_entry = entry
            char_key = name
            break

    if not char_entry:
        available = ", ".join(registry["characters"].keys())
        print(f"Error: Character '{character_name}' not found. Available: {available}", file=sys.stderr)
        sys.exit(1)

    # Load character config
    char_dir = project_root / char_entry["dir"]
    config_path = char_dir / "config.json"
    if not config_path.exists():
        print(f"Error: Character config not found at {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    # Check for style-specific prompt override in config (e.g., Feishu-sourced prompts)
    style_options = config.get("style_options", {})
    style_prompt_override = None
    if style and style in style_options:
        style_prompt_override = style_options[style].get("style_prompt")

    if style_prompt_override:
        # Use the full prompt from config directly, append key_features and scene
        key_features = config.get("key_features", "")
        key_features_block = f"\n\n{key_features}" if key_features else ""
        prompt_text = f"{style_prompt_override}{key_features_block}\n\n场景：{scene}"
        print(f"Using style prompt override for '{style}'", file=sys.stderr)
    else:
        # Translate Chinese scene to English for better generation quality
        if has_chinese(scene):
            print(f"Translating scene from Chinese: {scene}", file=sys.stderr)
            scene = translate_scene_to_english(scene, api_key)
            print(f"Translated to English: {scene}", file=sys.stderr)
        prompt_text = build_prompt(config, scene, style, aspect_ratio)
    print(f"Prompt:\n{prompt_text}\n", file=sys.stderr)

    # Select and load reference images
    ref_images = select_reference_images(config, char_dir, style, max_refs)
    print(f"Using {len(ref_images)} reference images: {[(p.name, label) for p, label in ref_images]}", file=sys.stderr)

    # Build API request contents
    contents = []

    # Add reference images (no labels — cleaner input yields better visual fidelity)
    for ref_path, label in ref_images:
        img_data, mime_type = load_image_as_base64(ref_path)
        contents.append(types.Part.from_bytes(data=base64.standard_b64decode(img_data), mime_type=mime_type))

    # Add text prompt
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
    safe_scene = scene[:30].replace(" ", "_").replace("/", "_")
    output_filename = f"{char_key}_{safe_scene}_{timestamp}.png"
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

    # Output the path for the caller to use
    print(str(output_path))
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate IP character images using Gemini")
    parser.add_argument("--character", required=True, help="Character name (e.g., 麦芬)")
    parser.add_argument("--scene", required=True, help="Scene description (e.g., 在海边散步)")
    parser.add_argument("--project-root", required=True, help="Project root directory containing characters.json")
    parser.add_argument("--output", default=None, help="Output directory (default: project-root/output/)")
    parser.add_argument("--style", default=None, help="Art style: 2d, 3d, or custom description")
    parser.add_argument("--model", default="gemini-3-pro-image-preview", help="Gemini model name")
    parser.add_argument("--max-refs", type=int, default=5, help="Maximum number of reference images to send")
    parser.add_argument("--aspect-ratio", default="1:1", help="Image aspect ratio (e.g., 1:1, 4:3, 16:9, 3:4, 9:16)")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    output_dir = Path(args.output).resolve() if args.output else project_root / "output"

    generate_image(
        character_name=args.character,
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
