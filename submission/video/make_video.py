#!/usr/bin/env python3
"""Assemble the Rafiq demo video: per-shot WebM captures (browser recorder) +
Samantha TTS narration → 1080p30 MP4 with burned captions, intro/outro cards,
sized under the 40MB submission cap.

Run:  uv run python submission/video/make_video.py
Inputs:  shots/shotN.webm  (browser captures, 1440x810)
Output:  ../rafiq-demo.mp4  + build report (durations, md5, size)
"""
from __future__ import annotations

import json
import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHOTS = HERE / "shots"
AUDIO = HERE / "audio"
BUILD = HERE / "build"
OUT = HERE.parent / "rafiq-demo.mp4"

FPS = 30
W, H = 1920, 1080
FONT = "/System/Library/Fonts/Helvetica.ttc"

NARRATIONS = [
    ("shot1", "Meet Rafiq — an employee-owned companion for onboarding and internal mobility at Emirates. Aisha is on day five. Before she asks anything, Rafiq already knows her laptop is two days past its target — and exactly who owns it."),
    ("shot2", "She asks in plain words. The answer is computed — journey events against journey-map targets, never generated — and it cites the source policy. Tapping the chip opens the exact section."),
    ("shot3", "One tap, and Rafiq chases the owner for her: a complete handoff card — stage, blocker, what has been tried — goes to the IT service desk."),
    ("shot4", "Omar is mid-transfer. The same rule engine covers mobility: his receiving team sign-off is three days stalled — the policy is cited, and the receiving manager is named."),
    ("shot5", "The journey timeline mirrors the real process: the medical can be completed at the visa window, and Emirates ID biometrics happen at the same visit — so finishing early is normal, not an error."),
    ("shot6", "Consent is real. With pulse consent off, the pulse signal is excluded from every calculation — and a test asserts it. Everything Rafiq does is recorded in the audit log Aisha can read."),
    ("shot7", "The same data serves the people around the employee. Grace, the line manager, sees risk sorted blockers — never pulse content. Fatima, the HR business partner, sees only real stalls, each already seen by the employee first. And the IT service desk receives complete handoff cards — acknowledge, resolve."),
    ("shot8", "The organization gets the aggregate view — where journeys stall most, never an individual. And Rafiq speaks Arabic, with a full right to left flip."),
    ("shot9", "Rafiq: knows where you are, answers with citations, and routes to the right human — before it escalates."),
]

TAIL = 0.8  # silence after narration ends, per shot


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        sys.exit(f"command failed: {' '.join(cmd[:6])}…")
    return r


def duration(path: Path) -> float:
    r = run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(path)])
    fmt = json.loads(r.stdout)["format"]
    if "duration" in fmt:
        return float(fmt["duration"])
    # live-recorded webm has no duration header — derive from frames
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets",
             "-show_entries", "stream=nb_read_packets", "-of", "default=nw=1", str(path)])
    frames = int(r.stdout.strip().split("=")[1])
    return frames / 30.0


def tts() -> dict[str, float]:
    """Synthesize narration per shot; returns {shot: audio_duration}."""
    AUDIO.mkdir(exist_ok=True)
    out = {}
    for shot, text in NARRATIONS:
        aiff = AUDIO / f"{shot}.aiff"
        if not aiff.exists():
            run(["say", "-v", "Samantha", "-r", "185", "-o", str(aiff), text])
        d = duration(aiff)
        wav = AUDIO / f"{shot}.wav"
        fade_start = max(0.0, d - 0.3)
        run(["ffmpeg", "-y", "-v", "error", "-i", str(aiff),
             "-af", f"afade=t=out:st={fade_start:.2f}:d=0.3",
             "-ar", "48000", "-ac", "2", str(wav)])
        want = d + TAIL
        run(["ffmpeg", "-y", "-v", "error", "-i", str(wav), "-af", "apad",
             "-t", f"{want:.2f}", "-ar", "48000", "-ac", "2", str(AUDIO / f"{shot}.pad.wav")])
        out[shot] = d
    return out


def srt(durs: dict[str, float]) -> Path:
    """Burned captions: one caption per narration, split on sentence ends."""
    def fmt(t: float) -> str:
        h, rem = divmod(t, 3600)
        m, s = divmod(rem, 60)
        return f"{int(h):02d}:{int(m):02d}:{s:06.3f}".replace(".", ",")

    lines, t0, idx = [], 2.0, 1  # intro card = 2s
    for shot, text in NARRATIONS:
        dur = durs[shot]
        # split into caption-sized chunks (~55 chars) proportionally
        sentences = [x.strip() + "." for x in text.split(".") if x.strip()]
        weights = [len(x) for x in sentences]
        total = sum(weights)
        t = t0
        for sent, w in zip(sentences, weights):
            d = dur * w / total
            lines.append(f"{idx}\n{fmt(t)} --> {fmt(min(t + d - 0.05, t0 + dur))}\n{sent}\n")
            t += d
            idx += 1
        t0 += dur + TAIL
    srt_path = BUILD / "captions.srt"
    srt_path.write_text("\n".join(lines), encoding="utf-8")
    return srt_path


def card(png_path: Path, title: str, subtitle: str, bg: str) -> None:
    filt = (f"drawbox=x=0:y=0:w={W}:h={H}:color={bg}:t=fill,"
            f"drawtext=fontfile={FONT}:text='{title}':fontcolor=white:fontsize=72:"
            f"x=(w-text_w)/2:y=(h-text_h)/2-40,"
            f"drawtext=fontfile={FONT}:text='{subtitle}':fontcolor=0x8fd9cc:fontsize=34:"
            f"x=(w-text_w)/2:y=(h-text_h)/2+70")
    run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
         "-i", f"color=c={bg}:s={W}x{H}:d=1", "-frames:v", "1", "-vf", filt, str(png_path)])


def main() -> None:
    BUILD.mkdir(exist_ok=True)
    durs = tts()
    print("narration durations:", {k: round(v, 1) for k, v in durs.items()})

    intro_png, outro_png = BUILD / "intro.png", BUILD / "outro.png"
    card(intro_png, "Rafiq", "Employee AI Companion · onboarding + internal mobility", "0x0e1417")
    card(outro_png, "Rafiq", "knows where you are · answers with citations · routes to the right human", "0x0e1417")

    subs = srt(durs)
    parts = []
    t0 = 0.0
    for shot, text in NARRATIONS[:-1]:  # shot9 is the outro card, not a capture
        webm = SHOTS / f"{shot}.webm"
        if not webm.exists():
            sys.exit(f"missing capture: {webm}")
        want = durs[shot] + TAIL
        have = duration(webm)
        keep = want
        pad = max(0.0, want - have)
        vf = f"scale={W}:{H}:flags=lanczos"
        if pad > 0:
            vf += f",tpad=stop_mode=clone:stop_duration={pad:.2f}"
        part = BUILD / f"{shot}.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-i", str(webm), "-i", str(AUDIO / f"{shot}.pad.wav"),
             "-t", f"{keep:.2f}", "-r", str(FPS),
             "-vf", vf,
             "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "160k", str(part)])
        parts.append(part)
        t0 += keep

    # cards
    intro = BUILD / "card-intro.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(intro_png),
         "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "2", "-r", str(FPS),
         "-vf", f"scale={W}:{H}", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", str(intro)])
    parts = [intro] + parts
    outro = BUILD / "card-outro.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(outro_png),
         "-i", str(AUDIO / "shot9.pad.wav"), "-t", f"{durs['shot9'] + TAIL:.2f}", "-r", str(FPS),
         "-vf", f"scale={W}:{H}", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", str(outro)])
    parts.append(outro)

    lst = BUILD / "parts.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))

    # concat, then burn captions + lightbox so the size fits the cap
    cat = BUILD / "concat.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c", "copy", str(cat)])
    total = duration(cat)
    crf = 23 if total < 150 else 25
    run(["ffmpeg", "-y", "-v", "error", "-i", str(cat),
         "-vf", f"subtitles={subs}:force_style='FontName=Helvetica,FontSize=17,"
                f"PrimaryColour=&H00FFFFFF,OutlineColour=&HAA000000,BorderStyle=1,Outline=1.2,"
                f"MarginV=42'", "-r", str(FPS),
         "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p",
         "-c:a", "copy", "-movflags", "+faststart", str(OUT)])

    size = OUT.stat().st_size
    md5 = hashlib.md5(OUT.read_bytes()).hexdigest()
    print(f"OK {OUT.name}: {duration(OUT):.1f}s, {size/1e6:.1f}MB, crf={crf}, md5={md5[:12]}…")
    if size > 38e6:
        print("WARNING: over the 40MB submission cap — raise crf and rerun")


if __name__ == "__main__":
    main()
