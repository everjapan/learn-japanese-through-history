#!/usr/bin/env python3
"""Normalize an already edited recording and verify the encoded MP3."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def executable(value):
    found = shutil.which(value)
    if not found:
        raise ValueError(f"Executable not found: {value}; supply its full path")
    return found


def probe(ffprobe, path):
    result = subprocess.run(
        [ffprobe, "-v", "error", "-select_streams", "a:0", "-show_streams",
         "-show_format", "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)


def run_logged(command, log):
    with log.open("w", encoding="utf-8") as stream:
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=stream, check=True)
    return log.read_text(encoding="utf-8")


def measurement(log):
    values = json.loads(re.findall(r"\{[^{}]*\}", log, re.S)[-1])
    for key in ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset"):
        if not math.isfinite(float(values[key])):
            raise ValueError("Loudness measurement is not finite; inspect silent/short input")
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--work", required=True, type=Path)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--upstream-filter", default="")
    parser.add_argument("--lufs", type=float, default=-16)
    parser.add_argument("--peak", type=float, default=-1.5)
    parser.add_argument("--lra", type=float, default=7)
    args = parser.parse_args()
    if not (-70 <= args.lufs <= -5 and -8 <= args.peak <= 0 and 1 <= args.lra <= 50):
        parser.error("Invalid loudnorm target range")
    source, output, work = (p.resolve() for p in (args.input, args.output, args.work))
    if not source.is_file() or output.exists() or output.suffix.lower() != ".mp3":
        parser.error("Input must exist; output must be a new .mp3 file")
    ffmpeg, ffprobe = executable(args.ffmpeg), executable(args.ffprobe)
    identity = sha256(source)
    source_info = probe(ffprobe, source)
    stream = source_info["streams"][0]
    sample_rate, channels = int(stream["sample_rate"]), int(stream["channels"])
    if sample_rate not in (32000, 44100, 48000) or channels not in (1, 2):
        parser.error("Source format needs an explicit MP3 conversion choice; preserve a WAV master")
    source_duration = float(stream.get("duration", source_info["format"]["duration"]))
    work.mkdir(parents=True, exist_ok=False)
    output.parent.mkdir(parents=True, exist_ok=True)
    (work / "input-probe.json").write_text(json.dumps(source_info, indent=2) + "\n")
    upstream = args.upstream_filter.strip().rstrip(",")
    prefix = upstream + "," if upstream else ""
    base = [ffmpeg, "-hide_banner", "-nostats", "-nostdin", "-n", "-i", str(source),
            "-map", "0:a:0", "-vn"]
    normalize_i, render_peak = args.lufs, args.peak - 0.3
    attempts = []
    for attempt in range(1, 4):
        normal = f"loudnorm=I={normalize_i}:TP={render_peak}:LRA={args.lra}"
        first = measurement(run_logged(
            base + ["-af", prefix + normal + ":print_format=json", "-f", "null", "-"],
            work / f"pass1-{attempt}.log",
        ))
        second = normal + (
            ":measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}"
            ":measured_thresh={input_thresh}:offset={target_offset}"
            ":linear=false:print_format=json"
        ).format(**first)
        master, candidate = work / f"master-{attempt}.wav", work / f"candidate-{attempt}.mp3"
        run_logged(base + ["-af", prefix + second, "-map_metadata", "-1", "-ar",
                          str(sample_rate), "-ac", str(channels), "-c:a", "pcm_s24le", str(master)],
                   work / f"pass2-{attempt}.log")
        run_logged([ffmpeg, "-hide_banner", "-nostats", "-nostdin", "-n", "-i", str(master),
                    "-map", "0:a:0", "-map_metadata", "-1", "-c:a", "libmp3lame", "-b:a", "192k",
                    "-ar", str(sample_rate), "-ac", str(channels), str(candidate)],
                   work / f"encode-{attempt}.log")
        final = measurement(run_logged(
            [ffmpeg, "-hide_banner", "-nostats", "-nostdin", "-i", str(candidate), "-af",
             f"loudnorm=I={args.lufs}:TP={args.peak}:LRA={args.lra}:print_format=json", "-f", "null", "-"],
            work / f"encoded-measurement-{attempt}.log",
        ))
        attempts.append({"attempt": attempt, "first_pass": first, "encoded_measurement": final})
        actual_i, actual_peak = float(final["input_i"]), float(final["input_tp"])
        if abs(actual_i - args.lufs) <= 0.5 and actual_peak <= args.peak:
            break
        normalize_i = max(-70, min(-5, normalize_i + args.lufs - actual_i))
        render_peak -= max(0, actual_peak - args.peak) + 0.2
    else:
        raise ValueError("Encoded output missed targets after 3 attempts; inspect logs, no final exported")
    run_logged([ffmpeg, "-v", "error", "-xerror", "-nostdin", "-i", str(candidate), "-f", "null", "-"],
               work / "decode-check.log")
    final_info = probe(ffprobe, candidate)
    final_stream = final_info["streams"][0]
    final_duration = float(final_stream.get("duration", final_info["format"]["duration"]))
    if (int(final_stream["sample_rate"]) != sample_rate or int(final_stream["channels"]) != channels
            or abs(final_duration - source_duration) > 0.15):
        raise ValueError("Encoded format or duration changed unexpectedly")
    if sha256(source) != identity:
        raise ValueError("Source identity changed during processing")
    # Exclusive creation also protects an output created by another process mid-run.
    with candidate.open("rb") as src, output.open("xb") as dest:
        shutil.copyfileobj(src, dest)
    report = {
        "input": str(source), "input_sha256": identity, "output": str(output),
        "output_sha256": sha256(output), "duration_seconds": final_duration,
        "sample_rate": sample_rate, "channels": channels,
        "upstream_filter": upstream, "target_lufs": args.lufs, "peak_ceiling_dbtp": args.peak,
        "actual_lufs": actual_i, "actual_true_peak_dbtp": actual_peak,
        "actual_lra_lu": float(final["input_lra"]), "attempts": attempts,
        "full_decode_passed": True,
        "limits": "Measurements and decode only; content editing and listening are separate checks",
    }
    (work / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    (work / "output-probe.json").write_text(json.dumps(final_info, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "attempts"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
