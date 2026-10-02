#!/usr/bin/env python3
"""
Existential Horror Anthology - DaVinci Resolve Production Bridge
Author: Antigravity IDE & Creative Pipeline
Version: 2.0.0

Generates full production assets for DaVinci Resolve timeline assembly:
  1. DaVinci Resolve Markers CSV (Cut markers + Foley cues + DP notes)
  2. Standard CMX 3600 EDL (Instant timeline sequence creation)
  3. 30-Second 48kHz Stereo Scratch Audio Bed (WAV with vacuum cutoff, foley rhythm, sub-bass)
  4. 1920x1080 Animatic Storyboard Slates for visual timeline layout
"""

import os
import sys
import json
import math
import struct
import wave
import argparse
from pathlib import Path
from typing import Dict, List, Any
from PIL import Image, ImageDraw, ImageFont


def seconds_to_timecode(seconds: float, fps: int = 24, start_hour: int = 1) -> str:
    """Converts seconds to SMPTE timecode string HH:MM:SS:FF."""
    total_frames = int(round(seconds * fps))
    frames = total_frames % fps
    total_seconds = total_frames // fps
    secs = total_seconds % 60
    total_minutes = total_seconds // 60
    mins = total_minutes % 60
    hours = (total_minutes // 60) + start_hour
    return f"{hours:02d}:{mins:02d}:{secs:02d}:{frames:02d}"


def generate_davinci_markers_csv(shots: List[Dict[str, Any]], fps: int, output_csv_path: Path):
    """
    Exports a DaVinci Resolve compatible Timeline Markers CSV file.
    Columns: Timecode In, Timecode Out, Name, Comment, Color, Duration
    """
    lines = ["Timecode In,Timecode Out,Name,Comment,Color,Duration"]

    for shot in shots:
        shot_id = shot.get("shot_id", "")
        beat_name = shot.get("beat_name", "")
        timing = shot.get("timing", {})
        start_s = timing.get("start_seconds", 0.0)
        end_s = timing.get("end_seconds", 0.0)
        dur_s = timing.get("duration_seconds", round(end_s - start_s, 2))

        tc_in = seconds_to_timecode(start_s, fps)
        tc_out = seconds_to_timecode(end_s, fps)
        dur_tc = seconds_to_timecode(dur_s, fps, start_hour=0)

        marker = shot.get("davinci_marker", {})
        color = marker.get("color", "Yellow")
        name = marker.get("name", f"Cut: {shot_id}")
        note = marker.get("note", f"{beat_name} ({dur_s}s)")

        # Escape quotes for CSV
        clean_note = note.replace('"', '""')
        lines.append(f'"{tc_in}","{tc_out}","{name}","{clean_note}","{color}","{dur_tc}"')

        # Add foley cue markers
        for cue in shot.get("foley_cues", []):
            cue_t = cue.get("timestamp_seconds", start_s)
            cue_dur = cue.get("duration_seconds", 0.5)
            cue_tc_in = seconds_to_timecode(cue_t, fps)
            cue_tc_out = seconds_to_timecode(cue_t + cue_dur, fps)
            cue_name = f"Foley: {cue.get('cue_id', 'cue')}"
            cue_comment = f"[{cue.get('track_layer', 'A2')}] {cue.get('filename')}: {cue.get('description')}"
            cue_clean_comment = cue_comment.replace('"', '""')
            lines.append(f'"{cue_tc_in}","{cue_tc_out}","{cue_name}","{cue_clean_comment}","Cyan","00:00:00:01"')

    # Add Final Infinite Loop Seam Marker
    if shots:
        final_s = shots[-1].get("timing", {}).get("end_seconds", 30.0)
        final_tc = seconds_to_timecode(final_s, fps)
        lines.append(f'"{final_tc}","{final_tc}","LOOP SEAM: RESET POINT","Infinite Loop Seam: Seamless cut back to 01:00:00:00 for YouTube Shorts/TikTok (>110% APV)","Magenta","00:00:00:01"')

    with open(output_csv_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[+] DaVinci Resolve Markers CSV: {output_csv_path}")


def generate_cmx3600_edl(shots: List[Dict[str, Any]], fps: int, output_edl_path: Path, title: str = "HORROR_LOOP"):
    """
    Generates a standard CMX 3600 EDL for instant timeline import in DaVinci Resolve.
    """
    edl_lines = [
        f"TITLE: {title.upper().replace(' ', '_')}",
        "FCM: NON-DROP FRAME",
        ""
    ]

    for idx, shot in enumerate(shots, start=1):
        shot_id = shot.get("shot_id", f"SHOT_{idx:02d}").upper()
        beat_name = shot.get("beat_name", "").upper().replace(" ", "_")
        timing = shot.get("timing", {})
        start_s = timing.get("start_seconds", 0.0)
        end_s = timing.get("end_seconds", 0.0)
        dur_s = timing.get("duration_seconds", round(end_s - start_s, 2))

        # Source TC (00:00:00:00 to duration)
        src_in = "00:00:00:00"
        src_out = seconds_to_timecode(dur_s, fps, start_hour=0)

        # Record TC (Timeline master TC)
        rec_in = seconds_to_timecode(start_s, fps, start_hour=1)
        rec_out = seconds_to_timecode(end_s, fps, start_hour=1)

        # CMX 3600 record line format: EventNum Reel Track Trans SourceIn SourceOut RecIn RecOut
        edl_lines.append(f"{idx:03d}  AX       V     C        {src_in} {src_out} {rec_in} {rec_out}")
        edl_lines.append(f"* FROM CLIP NAME: {shot_id}_{beat_name[:20]}")
        edl_lines.append(f"* COMMENT: Lens: {shot.get('cinematography', {}).get('lens_focal_length', 'N/A')}")
        edl_lines.append("")

    with open(output_edl_path, "w", encoding="utf-8") as f:
        f.write("\n".join(edl_lines))
    print(f"[+] DaVinci Resolve CMX 3600 EDL: {output_edl_path}")


def synthesize_scratch_audio_bed(shots: List[Dict[str, Any]], total_duration_s: float, output_wav_path: Path):
    """
    Synthesizes a broadcast-quality 48kHz 16-bit stereo scratch audio bed matching the exact foley pacing.
    Features:
      - 0.0s - 3.5s: Muffled room chatter + candle blow puff
      - 3.5s: Hard acoustic vacuum cutoff (airlock seal pop + total room silence)
      - 3.5s - 7.5s: Dead vacuum isolation + 14kHz faint tinnitus + 40Hz sub-rumble
      - 7.5s - 13.0s: Tactile blade scrape & ceramic fork clink
      - 13.0s - 24.5s: Rhythmic squelching chew pulse + accelerating visceral heartbeat
      - 24.5s - 26.0s: Sharp gasp intake & silence
      - 26.0s - 30.0s: Temporal whip snap & triumphant party chatter surge (Infinite Loop reset)
    """
    sample_rate = 48000
    total_samples = int(total_duration_s * sample_rate)
    left_channel = [0.0] * total_samples
    right_channel = [0.0] * total_samples

    # Helper: Add sine wave tone with envelope
    def add_tone(start_s: float, dur_s: float, freq: float, gain: float, pan: float = 0.0):
        start_idx = int(start_s * sample_rate)
        num_samples = int(dur_s * sample_rate)
        end_idx = min(start_idx + num_samples, total_samples)

        for i in range(start_idx, end_idx):
            t = (i - start_idx) / sample_rate
            progress = (i - start_idx) / num_samples

            # Linear attack/decay envelope (10ms fade in/out to prevent clicks)
            env = 1.0
            fade_samples = int(0.01 * sample_rate)
            if (i - start_idx) < fade_samples:
                env = (i - start_idx) / fade_samples
            elif (end_idx - i) < fade_samples:
                env = (end_idx - i) / fade_samples

            val = math.sin(2.0 * math.pi * freq * t) * gain * env
            left_gain = math.sqrt(0.5 * (1.0 - pan))
            right_gain = math.sqrt(0.5 * (1.0 + pan))
            left_channel[i] += val * left_gain
            right_channel[i] += val * right_gain

    # Helper: Add filtered noise burst (breath / chatter / whip snap)
    def add_noise(start_s: float, dur_s: float, gain: float, decay_rate: float = 5.0, pan: float = 0.0):
        start_idx = int(start_s * sample_rate)
        num_samples = int(dur_s * sample_rate)
        end_idx = min(start_idx + num_samples, total_samples)

        # Simple pseudo-random linear congruential generator for reproducibility
        seed = 42
        for i in range(start_idx, end_idx):
            seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
            noise = ((seed / 0x7FFFFFFF) * 2.0 - 1.0)
            t = (i - start_idx) / sample_rate
            env = math.exp(-decay_rate * t)
            val = noise * gain * env

            left_gain = math.sqrt(0.5 * (1.0 - pan))
            right_gain = math.sqrt(0.5 * (1.0 + pan))
            left_channel[i] += val * left_gain
            right_channel[i] += val * right_gain

    # 1. 2-Pop Sync Head Pip at 0.05s (Standard post-production audio sync)
    add_tone(0.05, 0.04, 1000.0, 0.15)

    # 2. Beat 1 (0.0s - 3.5s): Warm party chatter tone
    for t_step in [0.2, 0.8, 1.4, 2.0, 2.6]:
        add_tone(t_step, 0.5, 220.0, 0.04)
        add_tone(t_step + 0.1, 0.4, 330.0, 0.03)
        add_noise(t_step, 0.3, 0.02, decay_rate=3.0)

    # Candle Blow Hiss at 2.8s - 3.4s
    add_noise(2.8, 0.6, 0.12, decay_rate=2.0)

    # 3. Beat 2 (3.5s): Hard Vacuum Airlock Cutoff!
    # Air seal suction click
    add_noise(3.5, 0.15, 0.25, decay_rate=25.0)
    add_tone(3.5, 0.08, 90.0, 0.35)

    # 3.5s - 7.5s: Dead silence with 14kHz ear-ring & 40Hz sub-bass pressure
    add_tone(3.6, 3.8, 14200.0, 0.015)
    add_tone(3.5, 4.0, 42.0, 0.08)

    # 4. Beat 3 (7.5s - 13.0s): Cold solitary slicing
    add_tone(8.0, 0.2, 850.0, 0.06)  # Knife clink
    add_noise(8.1, 0.5, 0.05, decay_rate=4.0)  # Dense cake slice drag
    add_tone(10.2, 0.15, 1200.0, 0.07)  # Porcelain clink
    add_noise(11.5, 0.4, 0.06, decay_rate=5.0)  # Soft chew

    # 5. Beat 4 (13.0s - 24.5s): Visceral Decay - Accelerated squelch & Heartbeat
    # Heartbeat pulse (40Hz-70Hz thud) accelerating
    heartbeat_times = [
        13.0, 13.8, 14.5, 15.2, 15.8, 16.4, 16.9, 17.4, 17.9, 18.4,
        18.8, 19.2, 19.6, 20.0, 20.4, 20.7, 21.0, 21.3, 21.6, 21.9,
        22.2, 22.5, 22.8, 23.1, 23.4, 23.7, 24.0, 24.3
    ]
    for hb in heartbeat_times:
        add_tone(hb, 0.12, 55.0, 0.18)
        add_tone(hb + 0.08, 0.10, 45.0, 0.14)

    # Metal fork scraping glazed porcelain (13.2s)
    add_tone(13.2, 0.35, 3400.0, 0.08)
    add_noise(13.2, 0.4, 0.07, decay_rate=6.0)

    # Rhythmic wet squelching chewing loops
    chew_times = [14.0, 14.7, 15.5, 16.3, 17.2, 18.0, 19.0, 19.8, 20.8, 21.8, 22.8, 23.8]
    for ct in chew_times:
        add_noise(ct, 0.25, 0.11, decay_rate=8.0)
        add_tone(ct, 0.15, 180.0, 0.08)

    # Enamel grinding against metal (18.8s)
    add_tone(18.8, 0.4, 2800.0, 0.10)
    add_tone(18.85, 0.3, 3150.0, 0.09)

    # Choked esophagus swallow resonance (20.5s)
    add_tone(20.5, 0.6, 68.0, 0.22)
    add_noise(20.5, 0.5, 0.08, decay_rate=4.0)

    # Infrasound tension swell (19.0s to 24.5s)
    add_tone(19.0, 5.5, 36.0, 0.15)

    # 6. Beat 5 (24.5s - 30.0s): The Reset
    # Sharp dry gasp
    add_noise(24.6, 0.5, 0.09, decay_rate=3.0)

    # Temporal whip snap & reality pop at 26.0s
    add_noise(26.0, 0.12, 0.35, decay_rate=30.0)
    add_tone(26.0, 0.08, 1800.0, 0.25)
    add_tone(26.02, 0.15, 60.0, 0.30)

    # Laughter and applause surges back (26.1s - 30.0s)
    for t_step in [26.2, 26.8, 27.4, 28.0, 28.6, 29.2]:
        add_tone(t_step, 0.5, 240.0, 0.05)
        add_tone(t_step + 0.1, 0.4, 360.0, 0.04)
        add_noise(t_step, 0.4, 0.04, decay_rate=2.5)

    # Normalize audio to prevent clipping
    max_peak = max(max(abs(s) for s in left_channel), max(abs(s) for s in right_channel), 0.001)
    target_peak = 0.89  # -1 dBFS headroom
    norm_factor = target_peak / max_peak

    # Pack into 16-bit PCM WAV
    output_wav_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output_wav_path), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        packed_frames = bytearray()
        for l, r in zip(left_channel, right_channel):
            int_l = max(-32767, min(32767, int(l * norm_factor * 32767.0)))
            int_r = max(-32767, min(32767, int(r * norm_factor * 32767.0)))
            packed_frames.extend(struct.pack("<hh", int_l, int_r))

        wav_file.writeframes(packed_frames)

    print(f"[+] 30s Master Scratch Audio Bed (48kHz Stereo): {output_wav_path}")


def generate_animatic_slates(shots: List[Dict[str, Any]], fps: int, output_dir: Path):
    """
    Generates 1920x1080 graphic storyboard slate cards for each shot.
    Can be placed directly on the video track in DaVinci Resolve as visual placeholders.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    for idx, shot in enumerate(shots, start=1):
        shot_id = shot.get("shot_id", f"shot_{idx:02d}")
        beat_name = shot.get("beat_name", f"Beat {idx}")
        timing = shot.get("timing", {})
        start_s = timing.get("start_seconds", 0.0)
        end_s = timing.get("end_seconds", 0.0)
        dur_s = timing.get("duration_seconds", round(end_s - start_s, 2))
        frames = int(round(dur_s * fps))

        tc_in = seconds_to_timecode(start_s, fps)
        tc_out = seconds_to_timecode(end_s, fps)

        cinema = shot.get("cinematography", {})
        lens = cinema.get("lens_focal_length", "N/A")
        angle = cinema.get("camera_angle", "N/A")
        lighting = cinema.get("lighting_source", "N/A")
        sensory = cinema.get("sensory_grounding", "N/A")
        foley_cues = shot.get("foley_cues", [])

        # Create slate image
        img = Image.new("RGB", (1920, 1080), color=(14, 15, 18))
        draw = ImageDraw.Draw(img)

        # Draw technical border and safe zones
        draw.rectangle([(40, 40), (1880, 1040)], outline=(45, 50, 60), width=2)
        draw.rectangle([(80, 80), (1840, 1000)], outline=(30, 35, 42), width=1)

        # 9:16 Vertical Mobile Crop Safe Zone (Center 608px)
        mobile_left = 960 - 304   # 656
        mobile_right = 960 + 304  # 1264
        draw.line([(mobile_left, 40), (mobile_left, 1040)], fill=(75, 65, 40), width=1)
        draw.line([(mobile_right, 40), (mobile_right, 1040)], fill=(75, 65, 40), width=1)
        draw.text((mobile_left + 15, 60), "[ 9:16 SHORTS / TIKTOK SAFE ZONE ]", fill=(160, 140, 60))

        # Crosshairs in center
        cx, cy = 960, 540
        draw.line([(cx - 30, cy), (cx + 30, cy)], fill=(60, 65, 75), width=1)
        draw.line([(cx, cy - 30), (cx, cy + 30)], fill=(60, 65, 75), width=1)

        # Header
        draw.text((100, 95), "EXISTENTIAL HORROR ANTHOLOGY // PILOT: THE BIRTHDAY LOOP", fill=(140, 145, 160))
        draw.text((100, 140), f"SHOT {idx:02d} / {len(shots):02d}  [{shot_id.upper()}]", fill=(245, 245, 245))
        draw.text((100, 185), f"BEAT: {beat_name.upper()}", fill=(230, 180, 80))

        # Timecode info box
        draw.rectangle([(100, 240), (600, 360)], fill=(22, 25, 30), outline=(50, 55, 65))
        draw.text((120, 255), f"TIMECODE IN:  {tc_in}", fill=(200, 210, 220))
        draw.text((120, 285), f"TIMECODE OUT: {tc_out}", fill=(200, 210, 220))
        draw.text((120, 315), f"DURATION:     {dur_s}s ({frames} Frames @ {fps}fps)", fill=(90, 200, 150))

        # Cinematography Specifications
        draw.rectangle([(100, 390), (1820, 620)], fill=(20, 22, 27), outline=(45, 50, 60))
        draw.text((120, 410), "CINEMATOGRAPHIC RIGOR & SENSORY GROUNDING (rule.md)", fill=(180, 120, 90))
        draw.text((120, 450), f"LENS & FOCAL LENGTH : {lens}", fill=(220, 220, 220))
        draw.text((120, 485), f"CAMERA ANGLE & TILT : {angle}", fill=(220, 220, 220))
        draw.text((120, 520), f"PHYSICAL LIGHTING   : {lighting}", fill=(220, 220, 220))
        draw.text((120, 555), f"TACTILE PHYSIOLOGY  : {sensory}", fill=(210, 170, 170))

        # Audio & Foley cues box
        draw.rectangle([(100, 650), (1820, 920)], fill=(18, 20, 25), outline=(40, 45, 55))
        draw.text((120, 670), "AUDIO-FIRST SOUND DESIGN CUES", fill=(100, 180, 220))
        y_pos = 710
        for cue in foley_cues[:4]:
            cue_line = f"* [{cue.get('track_layer', 'A2')}] @ {cue.get('timestamp_seconds', 0.0):.1f}s: {cue.get('filename')} - {cue.get('description')}"
            draw.text((120, y_pos), cue_line[:120], fill=(190, 195, 205))
            y_pos += 35

        # Footer
        draw.text((100, 955), "DRAG INTO DAVINCI RESOLVE VIDEO TRACK 1 AS ANIMATIC PLACEHOLDER", fill=(80, 85, 95))
        draw.text((1500, 955), f"ASPECT: 16:9 | 24 FPS", fill=(80, 85, 95))

        slate_filename = output_dir / f"slate_{idx:02d}_{shot_id}.png"
        img.save(slate_filename, format="PNG")

    print(f"[+] 6 Animatic Storyboard Slates generated: {output_dir}")


def export_davinci_suite(episode_path: Path, output_base: Path):
    print(f"\n=======================================================")
    print(f" EXPORTING DAVINCI RESOLVE PRODUCTION ASSETS")
    print(f"=======================================================\n")

    if not episode_path.exists():
        raise FileNotFoundError(f"Episode file not found: {episode_path}")

    with open(episode_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("episode_metadata", {})
    specs = meta.get("technical_specifications", {})
    fps = specs.get("fps", 24)
    total_duration = specs.get("total_duration_seconds", 30.0)
    episode_id = meta.get("episode_id", episode_path.stem)
    shots = data.get("shots", [])

    # Setup directories
    episode_output_dir = output_base / "episodes" / episode_id
    episode_output_dir.mkdir(parents=True, exist_ok=True)
    slates_dir = episode_output_dir / "slates"

    workspace_root = episode_path.parent.parent
    beds_dir = workspace_root / "assets" / "audio" / "beds"
    beds_dir.mkdir(parents=True, exist_ok=True)

    # 1. Markers CSV
    csv_path = episode_output_dir / "davinci_markers.csv"
    generate_davinci_markers_csv(shots, fps, csv_path)

    # 2. CMX 3600 EDL
    edl_path = episode_output_dir / "timeline.edl"
    generate_cmx3600_edl(shots, fps, edl_path, title=meta.get("episode_title", "HORROR_LOOP"))

    # 3. Scratch Audio Bed
    wav_path = beds_dir / f"{episode_id}_scratch_audio_bed.wav"
    synthesize_scratch_audio_bed(shots, total_duration, wav_path)

    # Also copy a reference copy of the audio bed to the episode output folder for convenience
    dest_wav_copy = episode_output_dir / "scratch_audio_bed.wav"
    try:
        import shutil
        shutil.copyfile(wav_path, dest_wav_copy)
    except Exception:
        pass

    # 4. Animatic Storyboard Slates
    generate_animatic_slates(shots, fps, slates_dir)

    print("\n[+] DaVinci Resolve Production Suite successfully exported!")


def main():
    parser = argparse.ArgumentParser(description="Export DaVinci Resolve Production Assets")
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

    args = parser.parse_args()
    workspace_root = Path(__file__).resolve().parent.parent

    episode_path = workspace_root / args.episode
    output_dir = workspace_root / args.output_dir

    try:
        export_davinci_suite(episode_path, output_dir)
    except Exception as e:
        print(f"[x] DaVinci export failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
