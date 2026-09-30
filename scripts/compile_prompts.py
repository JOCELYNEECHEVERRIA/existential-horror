#!/usr/bin/env python3
"""
Existential Horror Anthology - Multi-Engine Prompt Compiler
Author: Antigravity IDE & Creative Pipeline
Version: 2.0.0

Reads episode JSON specifications, validates them against creative standards (rule.md),
and compiles tailored prompt batches for:
  1. Primary Keyframe Generation (Flux / Midjourney) -> output/prompts_for_generation.txt
  2. Image-to-Video Motion Generation (Kling / Runway Gen-3 / Luma)
  3. Production Shot Manifest with timecodes and sound cue mappings.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Banned lexicon and concepts strictly enforced from rule.md
BANNED_WORDS = [
    "chilling", "spine-tingling", "blood-curdling", "unfathomable",
    "nightmarish", "eldritch", "sinister", "eerie", "epic cinematic", "hyperrealistic"
]

BANNED_CONCEPTS = [
    "jump scare", "red glowing eyes", "glowing red eyes",
    "shadowy figure", "shadowy figures", "maniacal laugh", "maniacal laughing"
]


class RuleValidator:
    """Validates prompts and metadata against creative standards defined in rule.md."""

    def __init__(self, strict: bool = False):
        self.strict = strict

    def audit_shot(self, shot: Dict[str, Any]) -> List[str]:
        warnings = []
        shot_id = shot.get("shot_id", "Unknown")
        combined_text = (
            f"{shot.get('shot_variable', '')} "
            f"{shot.get('motion_prompt', '')} "
            f"{json.dumps(shot.get('cinematography', {}))}"
        ).lower()

        # Check banned lexicon
        for word in BANNED_WORDS:
            if word in combined_text:
                warnings.append(
                    f"[{shot_id}] BANNED LEXICON DETECTED: '{word}'. "
                    f"Replace with mechanical/tactile physical descriptions."
                )

        # Check banned concepts
        for concept in BANNED_CONCEPTS:
            if concept in combined_text:
                warnings.append(
                    f"[{shot_id}] BANNED HORROR CONCEPT: '{concept}'. "
                    f"Focus on involuntary physiological decay instead."
                )

        # Sensory Grounding & Cinematography checks
        cinematography = shot.get("cinematography", {})
        if not cinematography.get("lens_focal_length"):
            warnings.append(f"[{shot_id}] Missing cinematographic focal length (e.g., 28mm, 85mm).")
        if not cinematography.get("lighting_source"):
            warnings.append(f"[{shot_id}] Missing physical light source (e.g., 40W tungsten bulb).")
        if not cinematography.get("sensory_grounding"):
            warnings.append(f"[{shot_id}] Missing tactile sensory grounding detail.")

        return warnings


def format_standard_prompt(style_anchor: str, character_anchor: str, shot_variable: str) -> str:
    """Concatenates: Style Anchor + ', ' + Character Anchor + ', ' + Shot Variable."""
    parts = [style_anchor.strip(), character_anchor.strip(), shot_variable.strip()]
    return ", ".join([p for p in parts if p])


def format_motion_prompt(shot: Dict[str, Any]) -> str:
    """
    Formats Image-to-Video prompts tailored for Kling and Runway.
    Avoids re-describing static costume/appearance to prevent motion model drift.
    """
    motion_action = shot.get("motion_prompt", shot.get("shot_variable", ""))
    lens = shot.get("cinematography", {}).get("lens_focal_length", "")
    angle = shot.get("cinematography", {}).get("camera_angle", "")

    prefix = f"Camera: {angle}, {lens}." if (angle or lens) else ""
    return f"{prefix} {motion_action}".strip()


def compile_episode(episode_path: Path, output_base: Path, strict: bool = False) -> Dict[str, Any]:
    print(f"\n=======================================================")
    print(f" COMPILING PROMPTS: {episode_path.name}")
    print(f"=======================================================\n")

    if not episode_path.exists():
        raise FileNotFoundError(f"Episode file not found: {episode_path}")

    with open(episode_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    metadata = data.get("episode_metadata", {})
    anchors = data.get("anchors", {})
    shots = data.get("shots", [])

    episode_id = metadata.get("episode_id", episode_path.stem)
    episode_title = metadata.get("episode_title", "Untitled Episode")
    style_anchor = anchors.get("style_anchor", "")
    character_anchor = anchors.get("character_anchor", "")
    environment_anchor = anchors.get("environment_anchor", "")

    # Creative Standards Audit
    validator = RuleValidator(strict=strict)
    all_warnings = []
    for shot in shots:
        warnings = validator.audit_shot(shot)
        all_warnings.extend(warnings)

    if all_warnings:
        print("[!] Creative Standards Audit Notices (rule.md compliance):")
        for w in all_warnings:
            print(f"    * {w}")
        print()
    else:
        print("[OK] All shots comply 100% with rule.md creative standards.\n")

    # Destination directories
    output_base.mkdir(parents=True, exist_ok=True)
    episode_output_dir = output_base / "episodes" / episode_id
    episode_output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Primary Output: output/prompts_for_generation.txt (Clean, numbered)
    prompts_for_generation_path = output_base / "prompts_for_generation.txt"
    primary_lines = []
    primary_lines.append(f"# {episode_title.upper()} - GENERATION PROMPTS")
    primary_lines.append(f"# Series: Existential Horror Anthology")
    primary_lines.append(f"# Total Shots: {len(shots)} | Duration: {metadata.get('technical_specifications', {}).get('total_duration_seconds', 30.0)}s\n")

    # 2. Detailed Flux / Midjourney Keyframe Prompts
    keyframe_prompts_path = episode_output_dir / "prompts_flux_midjourney.txt"
    keyframe_lines = []
    keyframe_lines.append(f"# FLUX / MIDJOURNEY KEYFRAME PROMPTS - {episode_title}")
    keyframe_lines.append(f"# Recommended settings: Aspect Ratio 16:9, Stylize 200-300\n")

    # 3. Motion Prompts for Video Generation (Kling / Runway / Luma)
    motion_prompts_path = episode_output_dir / "prompts_kling_runway.txt"
    motion_lines = []
    motion_lines.append(f"# KLING / RUNWAY IMAGE-TO-VIDEO (I2V) MOTION PROMPTS - {episode_title}")
    motion_lines.append(f"# Use maya_hero.png as character reference or feed initial keyframes.\n")

    # Process Shots
    compiled_manifest = {
        "metadata": metadata,
        "anchors": anchors,
        "shots_compiled": []
    }

    print(f"{'Shot ID':<10} | {'Beat':<22} | {'Time (s)':<12} | {'Duration':<8} | {'Foley Count'}")
    print("-" * 68)

    for idx, shot in enumerate(shots, start=1):
        shot_id = shot.get("shot_id", f"beat_{idx:02d}")
        beat_name = shot.get("beat_name", f"Beat {idx}")
        timing = shot.get("timing", {})
        start_t = timing.get("start_seconds", 0.0)
        end_t = timing.get("end_seconds", 0.0)
        dur = timing.get("duration_seconds", round(end_t - start_t, 2))
        foley_count = len(shot.get("foley_cues", []))

        print(f"{shot_id:<10} | {beat_name[:22]:<22} | {start_t:>4.1f}s - {end_t:>4.1f}s | {dur:>5.1f}s  | {foley_count:>2} cues")

        shot_variable = shot.get("shot_variable", "")

        # Standard requested prompt: Style Anchor + ", " + Character Anchor + ", " + Shot Variable
        standard_prompt = format_standard_prompt(style_anchor, character_anchor, shot_variable)
        primary_lines.append(f"Shot {idx:02d} ({shot_id}):")
        primary_lines.append(f"{standard_prompt}\n")

        # Detailed Keyframe prompt with environment and camera specs
        cinema = shot.get("cinematography", {})
        camera_specs = f"Shot Specs: {cinema.get('lens_focal_length', '')}, {cinema.get('camera_angle', '')}. Lighting: {cinema.get('lighting_source', '')}."
        full_keyframe_prompt = f"{style_anchor}, {character_anchor}, {environment_anchor}, {shot_variable} --ar 16:9"
        keyframe_lines.append(f"## Shot {idx:02d} [{shot_id}] - {beat_name} ({dur}s)")
        keyframe_lines.append(f"<!-- {camera_specs} -->")
        keyframe_lines.append(f"{full_keyframe_prompt}\n")

        # Motion prompt
        motion_p = format_motion_prompt(shot)
        motion_lines.append(f"## Shot {idx:02d} [{shot_id}] Motion Prompt (Target Duration: {dur}s)")
        motion_lines.append(f"{motion_p}\n")

        compiled_manifest["shots_compiled"].append({
            "index": idx,
            "shot_id": shot_id,
            "beat_name": beat_name,
            "timing": timing,
            "standard_prompt": standard_prompt,
            "keyframe_prompt": full_keyframe_prompt,
            "motion_prompt": motion_p,
            "foley_cues": shot.get("foley_cues", []),
            "davinci_marker": shot.get("davinci_marker", {})
        })

    # Write primary file: output/prompts_for_generation.txt
    with open(prompts_for_generation_path, "w", encoding="utf-8") as f:
        f.write("\n".join(primary_lines))

    # Write keyframe prompts
    with open(keyframe_prompts_path, "w", encoding="utf-8") as f:
        f.write("\n".join(keyframe_lines))

    # Write motion prompts
    with open(motion_prompts_path, "w", encoding="utf-8") as f:
        f.write("\n".join(motion_lines))

    # Write compiled manifest
    manifest_path = episode_output_dir / "shot_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(compiled_manifest, f, indent=2, ensure_ascii=False)

    print("-" * 68)
    print(f"\n[+] Successfully generated files:")
    print(f"    1. Primary generation prompts:   {prompts_for_generation_path}")
    print(f"    2. Flux / Midjourney keyframes:  {keyframe_prompts_path}")
    print(f"    3. Kling / Runway motion:        {motion_prompts_path}")
    print(f"    4. Compiled Shot Manifest:       {manifest_path}")

    return compiled_manifest


def main():
    parser = argparse.ArgumentParser(description="Existential Horror Prompt Compiler")
    parser.add_argument(
        "--episode",
        type=str,
        default="episodes/episode_01_the_birthday_loop.json",
        help="Path to episode JSON file (default: episodes/episode_01_the_birthday_loop.json)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Base output directory (default: output)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enforce strict rule.md validation"
    )

    args = parser.parse_args()
    workspace_root = Path(__file__).resolve().parent.parent

    episode_path = workspace_root / args.episode
    output_dir = workspace_root / args.output_dir

    try:
        compile_episode(episode_path, output_dir, strict=args.strict)
    except Exception as e:
        print(f"[x] Compilation failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
