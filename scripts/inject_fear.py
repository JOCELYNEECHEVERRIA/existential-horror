#!/usr/bin/env python3
"""
Existential Horror Anthology - Automated Biological Fear Injector
Author: Antigravity IDE & Creative Pipeline
Version: 2.0.0

Analyzes episode drafts and injects evolutionary neurobiology fear triggers:
  1. Insular Cortex Visceral Disgust (enamel scraping, congealed fat, peristalsis)
  2. Motor Agency Hijack (involuntary muscle lock, tendon strain, autonomous limb motion)
  3. Auditory Predator Vigilance (acoustic vacuum, infrasound swell, 14kHz tinnitus)
  4. Uncanny Facial Paralysis (dry corneas, frozen laugh, dilated pupils)
  5. Infinite Loop Seam Alignment (seamless match between final shot and opening shot)
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple


# Biological fear triggers mapped by narrative engine phase
FEAR_TRIGGERS_BY_PHASE = {
    "spark": {
        "sensory": [
            "tiny droplet of saliva catching flame light on lower lip",
            "forced air rushing through pursed front incisors",
            "fleeting nervous twitch in the left eyelid before the wish"
        ],
        "lighting": "Warm flickering candle flame 10 inches from chin, contrasting against cold 40W tungsten overhead fill",
        "lens": "35mm prime lens",
        "angle": "Eye-level medium two-shot tracking subtly forward"
    },
    "grant": {
        "sensory": [
            "unblinking dry corneas glistening under harsh tungsten bulb",
            "candle smoke frozen in mid-air like spun glass",
            "absolute acoustic pressure drops in eardrums as room reverberation cuts to 0.00s",
            "mouths frozen wide mid-laugh, rigid like porcelain mannequins"
        ],
        "lighting": "Cold desaturated overhead 40W tungsten bulb casting hard downward shadows into eye sockets",
        "lens": "28mm wide-angle lens",
        "angle": "Low-angle Dutch tilt 12 degrees counter-clockwise from table surface looking up"
    },
    "visceral_decay": {
        "sensory": [
            "enamel incisors scraping violently against stainless steel fork tines",
            "cold shortening and congealed lard coating the tongue and roof of mouth",
            "forearm flexor tendons straining taut under knit wool cuffs as hands move autonomously",
            "esophageal muscles visibly convulsing in painful involuntary swallow",
            "cold sweat beading along the upper lip, stinging an open tear duct"
        ],
        "lighting": "Harsh top-down key light accentuating beads of sweat on throat and greasy sheen on jawline",
        "lens": "100mm macro lens",
        "angle": "Extreme macro close-up of throat and locked jaw, canted 15 degrees"
    },
    "infinite_trap": {
        "sensory": [
            "violent dry gasp of air through parted lips as jaw tension snaps free",
            "grease and frosting vanishing instantaneously from lips in a single-frame flash",
            "sudden blast of warm room air and auditory surge of cheerful party chatter"
        ],
        "lighting": "Instantaneous snap from bleak shadow to warm flickering orange candle flame and 40W bulb",
        "lens": "35mm prime lens",
        "angle": "Eye-level medium shot matching Shot 01 framing exactly"
    }
}

DEFAULT_FOLEY_TEMPLATES = {
    "spark": [
        {"filename": "party_room_tone_chatter.wav", "layer": "A1_Ambience", "desc": "Subdued party chatter, gentle applause."},
        {"filename": "candle_blow_exhale.wav", "layer": "A2_Foley", "desc": "Focused exhale hiss through pursed lips, candle fizzle."}
    ],
    "grant": [
        {"filename": "sudden_vacuum_airlock_cutoff.wav", "layer": "A3_SFX", "desc": "Violent acoustic vacuum pop: room reverb cuts instantly."},
        {"filename": "high_ear_ring_sub_drone.wav", "layer": "A1_Ambience", "desc": "Ultra-faint 14kHz ear-ring tone with 40Hz sub-bass pressure."}
    ],
    "visceral_decay": [
        {"filename": "metal_fork_scrape_porcelain.wav", "layer": "A2_Foley", "desc": "Harsh screech of fork tines scraping glazed porcelain."},
        {"filename": "heavy_squelch_wet_chewing.wav", "layer": "A2_Foley", "desc": "Amplified wet squelching of thick sponge cake in mouth."},
        {"filename": "teeth_enamel_grate_metal.wav", "layer": "A2_Foley", "desc": "Bone-dry scrape of front incisor enamel against steel."},
        {"filename": "deep_choked_esophagus_swallow.wav", "layer": "A2_Foley", "desc": "Heavy wet contraction of throat muscles forcing down dense mass."}
    ],
    "infinite_trap": [
        {"filename": "dry_gasp_breath_intake.wav", "layer": "A2_Foley", "desc": "Violent gasp of air through parted lips, release of jaw tension."},
        {"filename": "reality_whip_snap_pop.wav", "layer": "A3_SFX", "desc": "Hyper-sharp whip snap and temporal pop as reality resets."},
        {"filename": "party_room_laughter_surge.wav", "layer": "A1_Ambience", "desc": "Instant burst of cheerful chatter and laughter surging back."}
    ]
}


class FearInjector:
    """Enriches episode shot lists with biological fear vectors."""

    def __init__(self, intensity: float = 1.0):
        self.intensity = intensity

    def inject_shot(self, shot: Dict[str, Any], phase: str, is_loop_seam: bool = False) -> Dict[str, Any]:
        enriched = dict(shot)
        phase_key = phase.lower().strip()
        if phase_key not in FEAR_TRIGGERS_BY_PHASE:
            phase_key = "visceral_decay"

        trigger_data = FEAR_TRIGGERS_BY_PHASE[phase_key]

        cinema = enriched.get("cinematography", {})
        if not cinema.get("lens_focal_length") or cinema.get("lens_focal_length") == "N/A":
            cinema["lens_focal_length"] = trigger_data["lens"]

        if not cinema.get("camera_angle") or cinema.get("camera_angle") == "N/A":
            cinema["camera_angle"] = trigger_data["angle"]

        if not cinema.get("lighting_source") or "specify" in cinema.get("lighting_source", "").lower():
            cinema["lighting_source"] = trigger_data["lighting"]

        existing_sensory = cinema.get("sensory_grounding", "")
        if not existing_sensory or "tactile" in existing_sensory.lower():
            # Inject primary biological sensory detail
            cinema["sensory_grounding"] = trigger_data["sensory"][0]
        enriched["cinematography"] = cinema

        # Enhance shot variable if generic
        var_text = enriched.get("shot_variable", "")
        if len(var_text) < 40 or "describe" in var_text.lower():
            sensory_text = cinema["sensory_grounding"]
            enriched["shot_variable"] = (
                f"{cinema['camera_angle']}, {cinema['lens_focal_length']}. "
                f"Subject under {cinema['lighting_source']}. "
                f"Tactile detail: {sensory_text}."
            )

        # Enhance motion prompt if generic
        motion_text = enriched.get("motion_prompt", "")
        if len(motion_text) < 30 or "camera motion" in motion_text.lower():
            if phase_key == "grant":
                enriched["motion_prompt"] = (
                    "Slow rotational drift. Subject turns head in mounting confusion; "
                    "background figures remain completely frozen, eyes unblinking like glass."
                )
            elif phase_key == "visceral_decay":
                enriched["motion_prompt"] = (
                    "Micro-shaky camera tracking involuntary movement. Hand acts autonomously, "
                    "forcing mass into mouth. Jaw chews relentlessly while eyes convey paralyzed terror."
                )
            elif phase_key == "infinite_trap":
                enriched["motion_prompt"] = (
                    "Violent chest heave gasp. Single-frame flash: scene instantaneously snaps back "
                    "to pristine state. Subject stares down in paralyzing dread as cycle begins anew."
                )
            else:
                enriched["motion_prompt"] = "Subtle slow forward camera push-in focusing on micro-tension."

        # Add foley cues if empty or placeholder
        foley_cues = enriched.get("foley_cues", [])
        if not foley_cues or "stem_name" in foley_cues[0].get("filename", ""):
            templates = DEFAULT_FOLEY_TEMPLATES.get(phase_key, DEFAULT_FOLEY_TEMPLATES["visceral_decay"])
            t_start = enriched.get("timing", {}).get("start_seconds", 0.0)
            t_dur = enriched.get("timing", {}).get("duration_seconds", 4.0)

            new_cues = []
            for i, tmpl in enumerate(templates[:2]):
                new_cues.append({
                    "cue_id": f"cue_{shot.get('shot_id', 'shot')}_{i+1:02d}",
                    "filename": tmpl["filename"],
                    "timestamp_seconds": round(t_start + (i * 1.5), 1),
                    "duration_seconds": round(min(t_dur, 2.5), 1),
                    "track_layer": tmpl["layer"],
                    "description": tmpl["desc"]
                })
            enriched["foley_cues"] = new_cues

        return enriched

    def process_episode(self, episode_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        shots = episode_data.get("shots", [])
        enriched_shots = []
        metrics = {
            "total_shots": len(shots),
            "sensory_injections": 0,
            "foley_cues_added": 0,
            "loop_seam_aligned": False
        }

        num_shots = len(shots)
        for idx, shot in enumerate(shots):
            phase = shot.get("engine_phase", "")
            if not phase:
                if idx == 0:
                    phase = "spark"
                elif idx == 1:
                    phase = "grant"
                elif idx == num_shots - 1:
                    phase = "infinite_trap"
                else:
                    phase = "visceral_decay"

            is_last = (idx == num_shots - 1)
            injected = self.inject_shot(shot, phase, is_loop_seam=is_last)
            enriched_shots.append(injected)
            metrics["sensory_injections"] += 1
            metrics["foley_cues_added"] += len(injected.get("foley_cues", []))

        # Loop Seam Check: Match Shot 06 with Shot 01
        if num_shots >= 2:
            first_shot = enriched_shots[0]
            last_shot = enriched_shots[-1]
            last_shot["cinematography"]["camera_angle"] = f"Matching {first_shot.get('shot_id', 'Shot 01')} eye-level medium framing"
            last_shot["cinematography"]["lens_focal_length"] = first_shot.get("cinematography", {}).get("lens_focal_length", "35mm prime lens")
            metrics["loop_seam_aligned"] = True

        result = dict(episode_data)
        result["shots"] = enriched_shots
        result["episode_metadata"]["fear_injected"] = True
        return result, metrics


def main():
    parser = argparse.ArgumentParser(description="Existential Horror Biological Fear Injector")
    parser.add_argument("--input", type=str, required=True, help="Input episode JSON file")
    parser.add_argument("--output", type=str, default="", help="Output episode JSON file (defaults to overwrite or <name>_injected.json)")
    parser.add_argument("--inplace", action="store_true", help="Overwrite the input file in place")
    parser.add_argument("--intensity", type=float, default=1.0, help="Fear injection intensity multiplier (0.5 to 2.0)")

    args = parser.parse_args()
    workspace_root = Path(__file__).resolve().parent.parent

    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = workspace_root / input_path

    if not input_path.exists():
        print(f"[x] Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if args.inplace:
        output_path = input_path
    elif args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = workspace_root / output_path
    else:
        output_path = input_path.parent / f"{input_path.stem}_fear_injected.json"

    print("=" * 65)
    print(" BIOLOGICAL FEAR INJECTOR: NEURO-VISCERAL SENSORY ENGINE")
    print("=" * 65)
    print(f"[*] Input File:      {input_path.name}")
    print(f"[*] Output Target:   {output_path.name}")
    print(f"[*] Fear Intensity:  {args.intensity}x\n")

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    injector = FearInjector(intensity=args.intensity)
    enriched_data, metrics = injector.process_episode(data)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched_data, f, indent=2, ensure_ascii=False)

    print(f"[+] Biological Fear Injection Complete:")
    print(f"    - Processed Shots:       {metrics['total_shots']}")
    print(f"    - Sensory Injections:    {metrics['sensory_injections']}")
    print(f"    - Active Foley Stems:    {metrics['foley_cues_added']}")
    print(f"    - Loop Seam Aligned:     {'YES (Seamless Infinite Replay Seam)' if metrics['loop_seam_aligned'] else 'NO'}")
    print(f"\n[+] Saved enriched episode to: {output_path}")


if __name__ == "__main__":
    main()
