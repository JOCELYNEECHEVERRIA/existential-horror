#!/usr/bin/env python3
"""
Existential Horror Anthology - Master Pipeline Orchestrator
Author: Antigravity IDE & Creative Pipeline
Version: 2.0.0

One-click execution of the entire pre-production & DaVinci Resolve asset pipeline:
  1. Creative Standards Audit (rule.md compliance)
  2. Prompts Generation (Flux, Midjourney, Kling, Runway)
  3. DaVinci Resolve Timeline Markers CSV
  4. DaVinci Resolve CMX 3600 EDL
  5. Broadcast-Quality Scratch Audio Bed (48kHz WAV)
  6. HD Animatic Storyboard Slates (1920x1080)
"""

import sys
import argparse
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(scripts_dir))

from compile_prompts import compile_episode
from export_davinci_tools import export_davinci_suite


def build_pipeline(episode_file: Path, output_base: Path, strict: bool = False):
    print("=" * 70)
    print(" EXISTENTIAL HORROR ANTHOLOGY - MASTER PRODUCTION PIPELINE")
    print("=" * 70)
    print(f"[*] Target Episode: {episode_file.name}")
    print(f"[*] Output Directory: {output_base}")
    print(f"[*] Creative Standards Audit: {'Strict' if strict else 'Standard (Permissive)'}")

    # Step 1: Compile prompts & audit
    print("\n--- STEP 1: PROMPT COMPILATION & CREATIVE AUDIT ---")
    compile_episode(episode_file, output_base, strict=strict)

    # Step 2: Export DaVinci Suite
    print("\n--- STEP 2: DAVINCI RESOLVE PRODUCTION SUITE EXPORT ---")
    export_davinci_suite(episode_file, output_base)

    print("\n" + "=" * 70)
    print(" [SUCCESS] PIPELINE BUILD COMPLETE!")
    print("=" * 70)
    print("\nImmediate Next Steps:")
    print("1. DaVinci Resolve: Import 'timeline.edl' -> Right click timeline -> Import Markers from CSV ('davinci_markers.csv').")
    print("2. DaVinci Resolve: Drag 'scratch_audio_bed.wav' onto Audio Track 1. Your 30s cut is instantly locked!")
    print("3. Visual Slates: Drag 'slates/*.png' to Video Track 1 to view your full animatic with camera & lighting notes.")
    print("4. AI Video Generation: Copy prompts from 'prompts_for_generation.txt' or 'prompts_kling_runway.txt'.\n")


def main():
    parser = argparse.ArgumentParser(description="Master Production Pipeline Orchestrator")
    parser.add_argument(
        "--episode",
        type=str,
        default="episodes/episode_01_the_birthday_loop.json",
        help="Path to episode JSON file"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Base output directory"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enforce strict rule.md creative standards"
    )

    args = parser.parse_args()
    workspace_root = Path(__file__).resolve().parent.parent

    episode_path = workspace_root / args.episode
    output_dir = workspace_root / args.output_dir

    if not episode_path.exists():
        print(f"[x] Error: Episode file '{episode_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    build_pipeline(episode_path, output_dir, strict=args.strict)


if __name__ == "__main__":
    main()
