from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from .notify import notify
from .report import build, write


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the daily information-gap radar")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--no-notify", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    path = Path(args.config)
    if not path.exists(): path = root / "config.example.yaml"
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    report = build(config)
    output = write(report, root)
    sent = [] if args.no_notify else notify(report, config)
    print(f"Wrote {output}; notifications: {', '.join(sent) or 'not configured'}")


if __name__ == "__main__":
    main()
