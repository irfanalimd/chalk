"""Scaffold a video project from the template.

    python new_project.py ~/videos/my-topic          # short mode (2–3 min)
    python new_project.py ~/videos/my-paper --long   # long mode (8–10 min, chapters)

Creates project.json, script/narration.json, scenes/style.py, manim.cfg, .gitignore, .env.example and
the folders the pipeline writes to. Run setup.sh on the new directory afterwards.
"""
import shutil, sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "template"


def main(dest, long=False):
    dest = Path(dest).expanduser().resolve()
    if (dest / "project.json").exists():
        raise SystemExit(f"{dest} already has a project.json")
    shutil.copytree(TEMPLATE, dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
    long_cfg = dest / "project_long.json"
    if long:
        long_cfg.replace(dest / "project.json")
    else:
        long_cfg.unlink()
        (dest / "scenes/cards.py").unlink()
    for d in ("research", "script", "scenes", "clips", "assets/img", "assets/music", "build", "versions"):
        (dest / d).mkdir(parents=True, exist_ok=True)
    print(f"created {dest}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args[0] if args else ".", long="--long" in sys.argv)
