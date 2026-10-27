"""Scaffold a video project from the template.

    python new_project.py ~/videos/my-topic

Creates project.json, script/narration.json, scenes/style.py, manim.cfg, .gitignore, .env.example and
the folders the pipeline writes to. Run setup.sh on the new directory afterwards.
"""
import shutil, sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "template"


def main(dest):
    dest = Path(dest).expanduser().resolve()
    if (dest / "project.json").exists():
        raise SystemExit(f"{dest} already has a project.json")
    shutil.copytree(TEMPLATE, dest, dirs_exist_ok=True)
    for d in ("research", "script", "scenes", "clips", "assets/img", "assets/music", "build", "versions"):
        (dest / d).mkdir(parents=True, exist_ok=True)
    print(f"created {dest}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
