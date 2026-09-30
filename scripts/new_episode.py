#!/usr/bin/env python3
"""
Existential Horror Anthology - New Episode Generator & Scaffolder
Author: Antigravity IDE & Creative Pipeline
Version: 2.0.0

Quickly scaffolds a production-ready episode JSON file adhering to:
  - The Core Four-Part Psychological Engine (Spark -> Grant -> Decay -> Trap)
  - The Three-Anchor Prompt System (Style, Character, Environment)
  - Cinematographic Rigor & Audio-First Foley Pacing (rule.md)
"""

import sys
import json
import argparse
from pathlib import Path


def get_episode_template(episode_num: int, title: str, slug: str, logline: str) -> dict:
    return {
        "$schema_version": "2.0.0",
        "episode_metadata": {
            "episode_id": f"episode_{episode_num:02d}_{slug}",
            "series_title": "Existential Horror Anthology",
            "episode_number": episode_num,
            "episode_title": title,
            "logline": logline,
            "technical_specifications": {
                "aspect_ratio": "16:9",
                "resolution": "3840x2160",
                "fps": 24,
                "total_duration_seconds": 30.0,
                "audio_sample_rate_hz": 48000,
                "timecode_start": "01:00:00:00"
            },
            "narrative_engine": {
                "spark": "1. The Relatable Spark: An innocent micro-sin or everyday intrusive thought.",
                "malicious_grant": "2. The Malicious Grant: Reality bends to fulfill the wish with literal malice.",
                "visceral_decay": "3. The Visceral Decay: Tactile, mechanical sensory torture and anatomical breakdown.",
                "infinite_trap": "4. The Infinite Trap: The sudden realization that the task resets the loop forever."
            }
        },
        "anchors": {
            "style_anchor": "Dark graphic novel illustration, heavy ink line art, muted cel-shading, 1990s anime film aesthetic, desaturated palette, 35mm film grain, micro-scratches on emulsion",
            "character_anchor": "Protagonist, 20s, specific distinguishing physical traits, tactile wardrobe details",
            "environment_anchor": "Specific tactile environment, architectural textures, precise single light source"
        },
        "shots": [
            {
                "shot_id": "shot_01",
                "beat_number": 1,
                "beat_name": "The Spark",
                "engine_phase": "spark",
                "timing": {
                    "start_seconds": 0.0,
                    "end_seconds": 4.0,
                    "duration_seconds": 4.0,
                    "timecode_in": "01:00:00:00",
                    "timecode_out": "01:00:04:00",
                    "frame_in": 0,
                    "frame_out": 96
                },
                "cinematography": {
                    "lens_focal_length": "35mm prime lens",
                    "camera_angle": "Eye-level medium shot",
                    "lighting_source": "Specify exact physical light source (e.g., 40W tungsten bulb 3 feet overhead)",
                    "sensory_grounding": "Tactile physiological detail (e.g., sweat stinging tear duct, fingernail biting)"
                },
                "shot_variable": "Describe camera angle, lens, subject action, expression, and precise lighting.",
                "motion_prompt": "Camera motion vector and kinetic physical action for Kling / Runway.",
                "foley_cues": [
                    {
                        "cue_id": "cue_01",
                        "filename": "foley_stem_name.wav",
                        "timestamp_seconds": 0.0,
                        "duration_seconds": 3.5,
                        "track_layer": "A1_Ambience",
                        "description": "Tactile audio description."
                    }
                ],
                "davinci_marker": {
                    "color": "Yellow",
                    "name": "Beat 01: The Spark",
                    "note": "Cut point and sound transition instructions."
                }
            }
        ]
    }


def create_episode(episode_num: int, title: str, logline: str, workspace_root: Path) -> Path:
    slug = title.lower().replace(" ", "_").replace("'", "").replace('"', "")
    filename = f"episode_{episode_num:02d}_{slug}.json"
    target_path = workspace_root / "episodes" / filename

    if target_path.exists():
        print(f"[!] Warning: File already exists: {target_path}")
        return target_path

    template_data = get_episode_template(episode_num, title, slug, logline)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(template_data, f, indent=2, ensure_ascii=False)

    print(f"[+] Created new episode schema template: {target_path}")
    print(f"    Open {target_path} and fill out your 4-part engine beats and shot list.")
    return target_path


def main():
    parser = argparse.ArgumentParser(description="Existential Horror Episode Scaffolder")
    parser.add_argument("--num", type=int, required=True, help="Episode number (e.g. 2)")
    parser.add_argument("--title", type=str, required=True, help="Episode title (e.g. 'The Infinite Elevator')")
    parser.add_argument("--logline", type=str, default="A character gets trapped in an everyday horror loop.", help="One-sentence episode logline")

    args = parser.parse_args()
    workspace_root = Path(__file__).resolve().parent.parent

    create_episode(args.num, args.title, args.logline, workspace_root)


if __name__ == "__main__":
    main()
