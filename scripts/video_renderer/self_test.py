from __future__ import annotations

import tempfile
from pathlib import Path

from worker import load_tts, render_video


def main() -> int:
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
                "visual_type": "slides",
                "visual_direction": "Introduce a worksheet grid and identify a row, column and cell.",
                "on_screen_text": ["Rows", "Columns", "Cell references"],
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
