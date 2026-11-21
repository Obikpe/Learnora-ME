from __future__ import annotations

import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from worker import create_or_update_video_row, load_tts, render_video


def verify_video_metadata_retry_is_idempotent() -> None:
    client = MagicMock()
    lesson_table = MagicMock()
    lookup = MagicMock()
    lookup.select.return_value = lookup
    lookup.eq.return_value = lookup
    lookup.maybe_single.return_value = lookup
    lookup.execute.return_value = SimpleNamespace(data={"id": "existing-video-id"})
    lesson_table.select.return_value = lookup

    update = MagicMock()
    update.eq.return_value = update
    update.execute.return_value = SimpleNamespace(data=[])
    lesson_table.update.return_value = update

    job_table = MagicMock()
    job_update = MagicMock()
    job_update.eq.return_value = job_update
    job_update.execute.return_value = SimpleNamespace(data=[])
    job_table.update.return_value = job_update
    client.table.side_effect = lambda name: lesson_table if name == "lesson_videos" else job_table

    video_id = create_or_update_video_row(
        client,
        {
            "id": "render-job-id",
            "lesson_id": "lesson-id",
            "object_key": "courses/course/modules/module/lessons/lesson/package.mp4",
        },
        {"title": "Retry-safe video"},
        90,
        1024,
        "A verified teaching script.",
    )

    if video_id != "existing-video-id" or lesson_table.insert.called:
        raise RuntimeError("A retry created duplicate lesson-video metadata.")
    job_table.update.assert_called_once_with({"lesson_video_id": "existing-video-id"})


def main() -> int:
    verify_video_metadata_retry_is_idempotent()
    script = (
        "A spreadsheet stores information in rows and columns. "
        "Each cell is identified by a column letter and a row number. "
        "A formula begins with an equals sign. "
        "For example, equals SUM of B2 through B6 adds the values in those cells. "
        "Relative references adjust when a formula is copied to another cell. "
        "An absolute reference, written with dollar signs such as dollar B dollar 2, stays fixed. "
        "Choose the reference type that matches the calculation you want."
    )
    package = {
        "teaching_script": script,
        "video_plan": [
            {
                "narration": "A spreadsheet stores information in rows and columns. Each cell is identified by a column letter and a row number.",
                "visual_type": "table",
                "visual_direction": "Show an illustrative worksheet-style table and identify row, column and cell references.",
                "on_screen_text": ["Cell | Reference | Meaning", "A1 | Column A, row 1 | First cell", "B2 | Column B, row 2 | Second row, second column"],
            },
            {
                "narration": "A formula begins with an equals sign. For example, equals SUM of B2 through B6 adds the values in those cells. Relative references adjust when a formula is copied to another cell. An absolute reference, written with dollar signs such as dollar B dollar 2, stays fixed. Choose the reference type that matches the calculation you want.",
                "visual_type": "code_demo",
                "visual_direction": "Show a short, legible formula example and distinguish relative and absolute references.",
                "on_screen_text": ["=SUM(B2:B6)", "B2 changes when copied", "$B$2 stays fixed"],
            },
        ],
    }
    tts = load_tts()
    with tempfile.TemporaryDirectory(prefix="learnora-render-smoke-") as temporary:
        output = Path(temporary) / "smoke-test.mp4"
        duration, size = render_video(
            tts,
            package,
            "Excel Fundamentals",
            "Formulas and references",
            "Understanding cell references",
            "bf_emma",
            output,
        )
        if not output.is_file() or size <= 0 or duration <= 0:
            raise RuntimeError("The video-render smoke test did not produce a valid MP4.")
        print(f"Video render smoke test passed: {duration}s, {size} bytes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
