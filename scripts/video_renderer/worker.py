from __future__ import annotations

import argparse
import hashlib
import logging
import math
import os
import re
import shutil
import subprocess
import tempfile
import textwrap
import urllib.request
from pathlib import Path
from typing import Any

import boto3
import numpy as np
import soundfile as sf
from botocore.config import Config
from kokoro_onnx import Kokoro
from PIL import Image, ImageDraw, ImageFont
from supabase import Client, create_client

LOGGER = logging.getLogger("learnora.video_renderer")
WIDTH, HEIGHT = 1280, 720
FPS = 30
MAX_VIDEO_SECONDS = 300
MODEL_DIR = Path(os.getenv("LEARNORA_TTS_CACHE", "~/.cache/learnora-kokoro")).expanduser()
MODEL_URLS = {
    "kokoro-v1.0.int8.onnx": (
        "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/kokoro-v1.0.int8.onnx",
        "ae315a79b623f244700e4afb9246c46a26066782e049ba174bf3ba433970ee9c",
    ),
    "voices-v1.0.bin": (
        "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/voices-v1.0.bin",
        "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d",
    ),
}


def run(command: list[str], *, cwd: Path | None = None) -> None:
    LOGGER.debug("Running command: %s", " ".join(command))
    subprocess.run(command, cwd=str(cwd) if cwd else None, check=True, capture_output=True, text=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_model_file(filename: str) -> Path:
    url, expected_sha = MODEL_URLS[filename]
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    target = MODEL_DIR / filename
    if target.exists() and sha256_file(target) == expected_sha:
        return target
    target.unlink(missing_ok=True)
    temporary = target.with_suffix(target.suffix + ".part")
    LOGGER.info("Downloading verified TTS asset: %s", filename)
    with urllib.request.urlopen(url, timeout=180) as response, temporary.open("wb") as output:
        shutil.copyfileobj(response, output)
    actual_sha = sha256_file(temporary)
    if actual_sha != expected_sha:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(f"Checksum verification failed for TTS asset {filename}.")
    temporary.replace(target)
    return target


def load_tts() -> Kokoro:
    model_path = ensure_model_file("kokoro-v1.0.int8.onnx")
    voices_path = ensure_model_file("voices-v1.0.bin")
    return Kokoro(str(model_path), str(voices_path))


def split_tts_chunks(text: str, max_chars: int = 230) -> list[str]:
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        words = sentence.split()
        fragments: list[str] = []
        fragment = ""
        for word in words:
            candidate = word if not fragment else f"{fragment} {word}"
            if len(candidate) <= max_chars:
                fragment = candidate
            else:
                if fragment:
                    fragments.append(fragment)
                fragment = word
        if fragment:
            fragments.append(fragment)
        for part in fragments:
            candidate = part if not current else f"{current} {part}"
            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = part
    if current:
        chunks.append(current)
    return chunks or [text.strip()]


def synthesize_narration(tts: Kokoro, script: str, voice_id: str, output_path: Path) -> float:
    chunks = split_tts_chunks(script)
    language = "en-gb" if voice_id.startswith(("bf_", "bm_")) else "en-us"
    audio_parts: list[np.ndarray] = []
    sample_rate: int | None = None
    for index, chunk in enumerate(chunks):
        samples, current_rate = tts.create(chunk, voice=voice_id, speed=1.0, lang=language)
        samples = np.asarray(samples, dtype=np.float32).reshape(-1)
        if sample_rate is None:
            sample_rate = int(current_rate)
        elif int(current_rate) != sample_rate:
            raise RuntimeError("TTS returned inconsistent sample rates.")
        if index:
            audio_parts.append(np.zeros(int(sample_rate * 0.12), dtype=np.float32))
        audio_parts.append(samples)
    if not audio_parts or not sample_rate:
        raise RuntimeError("TTS did not return narration audio.")
    audio = np.concatenate(audio_parts)
    sf.write(str(output_path), audio, sample_rate, subtype="PCM_16")
    return float(len(audio) / sample_rate)


def font(path: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(path, size=size)
    except OSError:
        return ImageFont.load_default()


FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def wrap_lines(draw: ImageDraw.ImageDraw, text: str, selected_font: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in str(text).splitlines() or [""]:
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = ""
        for word in words:
            candidate = word if not current else f"{current} {word}"
            if draw.textlength(candidate, font=selected_font) <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    selected_font: ImageFont.ImageFont,
    fill: str,
    max_width: int,
    line_gap: int = 12,
    max_lines: int = 8,
) -> int:
    x, y = xy
    lines = wrap_lines(draw, text, selected_font, max_width)[:max_lines]
    line_height = max(24, selected_font.getbbox("Ag")[3] - selected_font.getbbox("Ag")[1])
    for line in lines:
        draw.text((x, y), line, font=selected_font, fill=fill)
        y += line_height + line_gap
    return y


def render_scene_image(
    scene: dict[str, Any],
    course_title: str,
    module_title: str,
    lesson_title: str,
    scene_index: int,
    scene_count: int,
    output_path: Path,
) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#0b1220")
    draw = ImageDraw.Draw(image)
    regular = font(FONT_REGULAR, 24)
    small = font(FONT_REGULAR, 17)
    bold = font(FONT_BOLD, 42)
    heading = font(FONT_BOLD, 52)
    mono = font(FONT_MONO, 21)

    draw.rounded_rectangle((28, 28, WIDTH - 28, HEIGHT - 28), radius=26, outline="#26344c", width=2)
    draw.text((72, 52), "LEARNORA ME", font=font(FONT_BOLD, 20), fill="#ff6b4a")
    draw.text((72, 88), course_title[:90], font=small, fill="#aebbd0")
    draw.text((72, 122), module_title[:90], font=font(FONT_BOLD, 22), fill="#d7deea")
    draw.text((72, 157), lesson_title[:100], font=font(FONT_REGULAR, 18), fill="#8797b0")
    draw.text((1100, 62), f"{scene_index + 1:02d} / {scene_count:02d}", font=small, fill="#aebbd0")
    draw.rounded_rectangle((72, 190, WIDTH - 72, 194), radius=2, fill="#29364e")
    draw.rounded_rectangle((72, 190, 72 + int((WIDTH - 144) * (scene_index + 1) / max(1, scene_count)), 194), radius=2, fill="#5b4bdb")

    panel = (72, 224, WIDTH - 72, 632)
    draw.rounded_rectangle(panel, radius=22, fill="#121d30", outline="#253650", width=1)
    visual_type = str(scene.get("visual_type") or "slides").lower()
    texts = [str(item).strip() for item in (scene.get("on_screen_text") or []) if str(item).strip()]
    if not texts:
        texts = [lesson_title]

    if visual_type == "code_demo":
        draw.rounded_rectangle((112, 258, WIDTH - 112, 596), radius=14, fill="#080e18", outline="#35445d", width=2)
        draw.rounded_rectangle((112, 258, WIDTH - 112, 300), radius=14, fill="#1d2a3f")
        for dot_x, dot_color in [(138, "#ff6b6b"), (164, "#f6c65b"), (190, "#5bd69a")]:
            draw.ellipse((dot_x, 273, dot_x + 12, 285), fill=dot_color)
        code = "\n".join(texts)
        code_lines = []
        for raw_line in code.splitlines():
            code_lines.extend(textwrap.wrap(raw_line, width=86, replace_whitespace=False, drop_whitespace=False) or [""])
        y = 322
        for line_number, line in enumerate(code_lines[:10], start=1):
            draw.text((140, y), f"{line_number:02d}", font=small, fill="#61738f")
            draw.text((190, y), line[:88], font=mono, fill="#e5eaf3")
            y += 27
    elif visual_type == "diagram":
        labels = texts[:5]
        count = len(labels)
        box_width = min(220, int((WIDTH - 240 - (count - 1) * 24) / max(1, count)))
        total_width = count * box_width + (count - 1) * 24
        x = (WIDTH - total_width) // 2
        y = 360
        for index, label in enumerate(labels):
            box = (x, y - 58, x + box_width, y + 72)
            draw.rounded_rectangle(box, radius=16, fill="#202c48", outline="#5b4bdb", width=2)
            draw_wrapped(draw, label, (x + 14, y - 30), font(FONT_BOLD, 22), "#f2f5fb", box_width - 28, 7, 4)
            if index < count - 1:
                mid_y = y + 7
                draw.line((x + box_width + 3, mid_y, x + box_width + 20, mid_y), fill="#ff6b4a", width=4)
                draw.polygon([(x + box_width + 20, mid_y - 8), (x + box_width + 32, mid_y), (x + box_width + 20, mid_y + 8)], fill="#ff6b4a")
            x += box_width + 24
    elif visual_type == "screen_demo":
        draw.rounded_rectangle((112, 254, WIDTH - 112, 602), radius=14, fill="#f3f5f8", outline="#45546c", width=2)
        draw.rounded_rectangle((112, 254, WIDTH - 112, 300), radius=14, fill="#e0e5ed")
        draw.ellipse((134, 270, 146, 282), fill="#f06d6d")
        draw.ellipse((158, 270, 170, 282), fill="#e9bd5b")
        draw.ellipse((182, 270, 194, 282), fill="#6bbd8b")
        draw.text((222, 267), "LEARNING DEMONSTRATION", font=font(FONT_BOLD, 15), fill="#42516a")
        rows = texts[:5]
        y = 324
        for index, row in enumerate(rows):
            fill = "#dfe7f6" if index == 0 else "#ffffff"
            draw.rounded_rectangle((146, y, WIDTH - 146, y + 44), radius=7, fill=fill, outline="#d1d9e5")
            draw.text((166, y + 10), row[:100], font=font(FONT_REGULAR, 18), fill="#17253a")
            y += 52
    elif visual_type == "equation":
        equation = "   ".join(texts)
        equation = equation.replace(r"\(", "").replace(r"\)", "").replace("$", "").replace(r"\[", "").replace(r"\]", "")
        draw_wrapped(draw, equation, (132, 345), heading, "#ffffff", WIDTH - 264, 18, 5)
    elif visual_type == "illustration":
        draw.ellipse((170, 310, 380, 520), fill="#242f55", outline="#5b4bdb", width=4)
        draw.ellipse((280, 280, 500, 500), outline="#ff6b4a", width=5)
        draw.line((390, 390, 570, 390), fill="#5b4bdb", width=6)
        draw_wrapped(draw, " ".join(texts), (610, 310), bold, "#f4f6fb", 470, 14, 5)
    else:
        title = texts[0]
        draw_wrapped(draw, title, (120, 270), heading, "#ffffff", WIDTH - 240, 12, 3)
        bullets = texts[1:]
        y = 410
        for item in bullets[:4]:
            draw.ellipse((140, y + 9, 154, y + 23), fill="#ff6b4a")
            y = draw_wrapped(draw, item, (178, y), regular, "#d9e1ee", WIDTH - 350, 8, 2) + 14

    draw.text((72, 654), "Learnora ME  •  Learn in short, focused steps", font=small, fill="#7e8da5")
    image.save(output_path, format="PNG", optimize=True)


def sentence_list(script: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", script.strip()) if part.strip()] or [script.strip()]


def srt_time(seconds: float) -> str:
    milliseconds = max(0, int(round(seconds * 1000)))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_subtitles(script: str, duration: float, path: Path) -> None:
    sentences = sentence_list(script)
    weights = [max(1, len(sentence.split())) for sentence in sentences]
    total_weight = sum(weights)
    cursor = 0.0
    entries = []
    for index, (sentence, weight) in enumerate(zip(sentences, weights), start=1):
        end = duration if index == len(sentences) else cursor + duration * weight / total_weight
        caption = "\n".join(textwrap.wrap(sentence, width=72))
        entries.append(f"{index}\n{srt_time(cursor)} --> {srt_time(end)}\n{caption}\n")
        cursor = end
    path.write_text("\n".join(entries), encoding="utf-8")


def probe_duration(path: Path) -> float:
    output = subprocess.check_output(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path),
        ],
        text=True,
    ).strip()
    return float(output)


def render_video(
    tts: Kokoro,
    package: dict[str, Any],
    course_title: str,
    module_title: str,
    lesson_title: str,
    voice_id: str,
    output_path: Path,
) -> tuple[int, int]:
    script = str(package.get("teaching_script") or "").strip()
    if not script:
        raise RuntimeError("The approved lesson package has no teaching script.")
    with tempfile.TemporaryDirectory(prefix="learnora-render-") as temporary:
        workdir = Path(temporary)
        narration_path = workdir / "narration.wav"
        audio_duration = synthesize_narration(tts, script, voice_id, narration_path)
        if audio_duration > MAX_VIDEO_SECONDS:
            raise RuntimeError(f"Rendered narration is {audio_duration:.1f} seconds; the lesson limit is 300 seconds.")

        scenes = package.get("video_plan") or []
        if not scenes:
            raise RuntimeError("The approved video lesson has no renderable scene plan.")
        weights = [max(1, len(str(scene.get("narration") or "").split())) for scene in scenes]
        total_weight = sum(weights)
        concat_lines = []
        for index, (scene, weight) in enumerate(zip(scenes, weights)):
            scene_duration = audio_duration * weight / total_weight
            image_path = workdir / f"scene-{index:02d}.png"
            segment_path = workdir / f"scene-{index:02d}.mp4"
            render_scene_image(scene, course_title, module_title, lesson_title, index, len(scenes), image_path)
            filter_graph = "zoompan=z='min(zoom+0.00035,1.035)':d=1:s=1280x720:fps=30,format=yuv420p"
            run([
                "ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", str(image_path),
                "-t", f"{scene_duration:.3f}", "-vf", filter_graph, "-r", str(FPS),
                "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "25",
                "-pix_fmt", "yuv420p", str(segment_path),
            ])
            concat_lines.append(f"file '{segment_path.as_posix()}'")

        concat_path = workdir / "concat.txt"
        concat_path.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
        subtitles_path = workdir / "captions.srt"
        write_subtitles(script, audio_duration, subtitles_path)
        subtitle_filter = (
            f"subtitles={subtitles_path.as_posix()}:"
            "force_style='FontName=DejaVu Sans,FontSize=18,PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H80000000,BorderStyle=3,Outline=1,Shadow=0,MarginV=30'"
        )
        run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_path),
            "-i", str(narration_path), "-map", "0:v:0", "-map", "1:a:0",
            "-vf", subtitle_filter, "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "24", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart", "-shortest", str(output_path),
        ])
    actual_duration = probe_duration(output_path)
    if actual_duration < 1 or actual_duration > MAX_VIDEO_SECONDS:
        raise RuntimeError(f"Final video duration {actual_duration:.1f}s is outside the 1-300 second limit.")
    return int(round(actual_duration)), output_path.stat().st_size


def r2_client():
    account_id = os.environ["R2_ACCOUNT_ID"]
    return boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )


def upload_video(path: Path, object_key: str) -> tuple[int, str]:
    bucket = os.environ["R2_BUCKET_NAME"]
    client = r2_client()
    client.upload_file(
        str(path),
        bucket,
        object_key,
        ExtraArgs={
            "ContentType": "video/mp4",
            "CacheControl": "private, max-age=0",
        },
    )
    size = path.stat().st_size
    return size, sha256_file(path)


def fetch_one(client: Client, table: str, row_id: str) -> dict[str, Any]:
    result = client.table(table).select("*").eq("id", row_id).maybe_single().execute()
    if not result.data:
        raise RuntimeError(f"Required {table} record was not found.")
    return result.data


def create_or_update_video_row(
    client: Client,
    job: dict[str, Any],
    lesson: dict[str, Any],
    bucket: str,
    duration: int,
    file_size: int,
    script: str,
) -> str:
    row = {
        "lesson_id": job["lesson_id"],
        "provider": "cloudflare",
        "storage_bucket": bucket,
        "storage_path": job["object_key"],
        "title": lesson.get("title") or "Lesson video",
        "duration_seconds": duration,
        "file_size_bytes": file_size,
        "mime_type": "video/mp4",
        "status": "processing",
        "is_private": True,
        "transcript_text": script,
    }
    existing_id = job.get("lesson_video_id")
    if existing_id:
        client.table("lesson_videos").update(row).eq("id", existing_id).execute()
        video_id = str(existing_id)
    else:
        result = client.table("lesson_videos").insert(row).execute()
        if not result.data:
            raise RuntimeError("Supabase did not return the inserted lesson-video record.")
        video_id = str(result.data[0]["id"])
        client.table("learnora_video_render_jobs").update(
            {"lesson_video_id": video_id}
        ).eq("id", job["id"]).execute()
    return video_id


def mark_job_failed(client: Client, job: dict[str, Any], error: Exception) -> None:
    try:
        current = client.table("learnora_video_render_jobs").select("status").eq("id", job["id"]).maybe_single().execute().data
        if current and current.get("status") in {"completed", "cancelled"}:
            return
        attempts = int(job.get("attempt_count") or 1)
        maximum = int(job.get("max_attempts") or 3)
        retry = attempts < maximum
        next_status = "queued" if retry else "failed"
        summary = f"{type(error).__name__}: {str(error)}"[:900]
        client.table("learnora_video_render_jobs").update({
            "status": next_status,
            "error_summary": summary,
            "claimed_at": None,
        }).eq("id", job["id"]).execute()
        client.table("learnora_lesson_production_packages").update({
            "status": "approved" if retry else "failed",
        }).eq("id", job["production_package_id"]).execute()
        if job.get("lesson_video_id"):
            client.table("lesson_videos").update({
                "status": "failed",
            }).eq("id", job["lesson_video_id"]).execute()
        else:
            client.table("lesson_videos").update({
                "status": "failed",
            }).eq("lesson_id", job["lesson_id"]).eq("provider", "cloudflare").eq("storage_path", job["object_key"]).eq("status", "processing").execute()
    except Exception:
        LOGGER.exception("Could not record failure state for video job %s", job.get("id"))


def process_job(client: Client, job: dict[str, Any], tts: Kokoro) -> None:
    package = fetch_one(client, "learnora_lesson_production_packages", str(job["production_package_id"]))
    lesson = fetch_one(client, "learnora_lessons", str(job["lesson_id"]))
    module = fetch_one(client, "course_modules", str(lesson["module_id"]))
    course = fetch_one(client, "learnora_courses", str(module["course_id"]))
    voice_id = str(job.get("voice_id") or "bf_emma")
    with tempfile.TemporaryDirectory(prefix="learnora-video-") as temporary:
        output_path = Path(temporary) / "lesson.mp4"
        duration, _ = render_video(
            tts,
            package,
            str(course.get("title") or "Learnora ME"),
            str(module.get("title") or ""),
            str(lesson.get("title") or "Lesson"),
            voice_id,
            output_path,
        )
        file_size, checksum = upload_video(output_path, str(job["object_key"]))
        video_id = create_or_update_video_row(
            client,
            job,
            lesson,
            os.environ["R2_BUCKET_NAME"],
            duration,
            file_size,
            str(package.get("teaching_script") or ""),
        )
        client.rpc(
            "complete_learnora_video_render_job",
            {
                "p_job_id": job["id"],
                "p_lesson_video_id": video_id,
                "p_duration_seconds": duration,
                "p_file_size_bytes": file_size,
                "p_checksum_sha256": checksum,
            },
        ).execute()
    LOGGER.info("Completed video render job %s (%ss, %s bytes)", job["id"], duration, file_size)


def claim_job(client: Client) -> dict[str, Any] | None:
    result = client.rpc("claim_next_learnora_video_render_job").execute()
    data = result.data
    if isinstance(data, list):
        return data[0] if data else None
    return data if isinstance(data, dict) else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Render queued Learnora ME lesson videos.")
    parser.add_argument("--max-jobs", type=int, default=2)
    args = parser.parse_args()
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(message)s")

    required = [
        "SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "R2_ACCOUNT_ID",
        "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET_NAME",
    ]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        LOGGER.error("Video renderer configuration is incomplete; missing: %s", ", ".join(missing))
        return 2

    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
    try:
        recovered = client.rpc(
            "requeue_stale_learnora_video_render_jobs",
            {"p_stale_minutes": 25},
        ).execute().data
        LOGGER.info("Recovered %s stale render job(s).", recovered or 0)
    except Exception:
        LOGGER.exception("Stale-job recovery failed; continuing to claim available jobs.")

    tts: Kokoro | None = None
    processed = 0
    for _ in range(max(1, min(args.max_jobs, 4))):
        job = claim_job(client)
        if not job:
            break
        try:
            if tts is None:
                tts = load_tts()
            process_job(client, job, tts)
            processed += 1
        except Exception as error:
            LOGGER.exception("Video render job %s failed.", job.get("id"))
            mark_job_failed(client, job, error)
            break
    LOGGER.info("Video renderer finished; completed %s job(s).", processed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
